import hashlib
import json

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from typing import (
    Dict,
    Optional,
)

from urllib.parse import quote


from services.github_service import (
    github_get,
)


# =========================================================
# CACHE CONFIG
# =========================================================

CACHE_DIRECTORY = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    / "analysis_cache"
)


CACHE_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# CACHE SCHEMA VERSION
#
# Change this only when the structure of the cache file
# itself changes.
# =========================================================

CACHE_SCHEMA_VERSION = 2


# =========================================================
# ANALYSIS ENGINE VERSIONS
#
# IMPORTANT:
#
# Change these whenever the corresponding analyzer logic
# changes in a way that should invalidate existing results.
#
# Example:
#
# architecture_service.py improved
#     architecture: "2.0" -> "2.1"
#
# insights_service.py improved
#     insights: "2.0" -> "2.1"
#
# Old cache files will automatically become invalid.
# No rm -rf analysis_cache/* required.
# =========================================================

ANALYSIS_ENGINE_VERSIONS = {
    "architecture":
        "2.2",

    "insights":
        "2.3",
}


DEFAULT_ANALYSIS_ENGINE_VERSION = (
    "1.0"
)


# =========================================================
# HELPERS
# =========================================================

def normalize_analysis_type(
    analysis_type: str,
) -> str:
    return (
        analysis_type
        .strip()
        .lower()
        .replace(
            " ",
            "-",
        )
    )


def get_analysis_engine_version(
    analysis_type: str,
) -> str:
    normalized_type = (
        normalize_analysis_type(
            analysis_type
        )
    )

    return (
        ANALYSIS_ENGINE_VERSIONS.get(
            normalized_type,
            DEFAULT_ANALYSIS_ENGINE_VERSION,
        )
    )


# =========================================================
# COMMIT SHA
# =========================================================

async def get_repository_commit_sha(
    owner: str,
    repo_name: str,
    branch: str,
) -> str:

    encoded_branch = quote(
        branch,
        safe="",
    )


    data = await github_get(
        (
            f"/repos/{owner}/{repo_name}"
            f"/commits/{encoded_branch}"
        )
    )


    commit_sha = (
        data.get(
            "sha"
        )
        if isinstance(
            data,
            dict,
        )
        else None
    )


    if not commit_sha:
        raise ValueError(
            "Could not determine the latest repository commit."
        )


    return str(
        commit_sha
    )


# =========================================================
# CACHE NAME
# =========================================================

def build_cache_filename(
    owner: str,
    repo_name: str,
    analysis_type: str,
) -> str:

    normalized_type = (
        normalize_analysis_type(
            analysis_type
        )
    )


    raw_key = (
        f"{owner}:"
        f"{repo_name}:"
        f"{normalized_type}"
    )


    digest = (
        hashlib.sha1(
            raw_key.encode(
                "utf-8"
            )
        )
        .hexdigest()[:12]
    )


    return (
        f"{normalized_type}-"
        f"{digest}.json"
    )


def get_cache_path(
    owner: str,
    repo_name: str,
    analysis_type: str,
) -> Path:

    return (
        CACHE_DIRECTORY
        /
        build_cache_filename(
            owner,
            repo_name,
            analysis_type,
        )
    )


# =========================================================
# CACHE VALIDATION
# =========================================================

def is_cache_payload_valid(
    payload: Dict,
    owner: str,
    repo_name: str,
    analysis_type: str,
    commit_sha: str,
) -> bool:

    normalized_type = (
        normalize_analysis_type(
            analysis_type
        )
    )


    expected_engine_version = (
        get_analysis_engine_version(
            normalized_type
        )
    )


    # -----------------------------------------------------
    # SCHEMA VERSION
    # -----------------------------------------------------

    if (
        payload.get(
            "schema_version"
        )
        != CACHE_SCHEMA_VERSION
    ):
        return False


    # -----------------------------------------------------
    # REPOSITORY IDENTITY
    # -----------------------------------------------------

    if (
        payload.get(
            "owner"
        )
        != owner
    ):
        return False


    if (
        payload.get(
            "repo_name"
        )
        != repo_name
    ):
        return False


    # -----------------------------------------------------
    # ANALYSIS TYPE
    # -----------------------------------------------------

    stored_analysis_type = (
        normalize_analysis_type(
            str(
                payload.get(
                    "analysis_type",
                    "",
                )
            )
        )
    )


    if (
        stored_analysis_type
        != normalized_type
    ):
        return False


    # -----------------------------------------------------
    # TARGET REPOSITORY VERSION
    #
    # If GitHub repository changed, cache is stale.
    # -----------------------------------------------------

    stored_commit_sha = (
        payload.get(
            "commit_sha"
        )
    )


    if (
        stored_commit_sha
        != commit_sha
    ):
        return False


    # -----------------------------------------------------
    # CODELENS ANALYZER VERSION
    #
    # If our analyzer changed, cache is stale even when
    # target repository commit SHA stayed the same.
    # -----------------------------------------------------

    stored_engine_version = (
        payload.get(
            "analysis_engine_version"
        )
    )


    if (
        stored_engine_version
        != expected_engine_version
    ):
        return False


    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    data = (
        payload.get(
            "data"
        )
    )


    if not isinstance(
        data,
        dict,
    ):
        return False


    return True


# =========================================================
# READ CACHE
# =========================================================

def get_cached_analysis(
    owner: str,
    repo_name: str,
    analysis_type: str,
    commit_sha: str,
) -> Optional[Dict]:

    cache_path = (
        get_cache_path(
            owner,
            repo_name,
            analysis_type,
        )
    )


    if not cache_path.exists():
        return None


    try:
        with cache_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            payload = (
                json.load(
                    file
                )
            )


    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None


    if not isinstance(
        payload,
        dict,
    ):
        return None


    if not is_cache_payload_valid(
        payload=
            payload,

        owner=
            owner,

        repo_name=
            repo_name,

        analysis_type=
            analysis_type,

        commit_sha=
            commit_sha,
    ):
        return None


    data = (
        payload.get(
            "data"
        )
    )


    return data


# =========================================================
# SAVE CACHE
# =========================================================

def save_cached_analysis(
    owner: str,
    repo_name: str,
    analysis_type: str,
    commit_sha: str,
    data: Dict,
):

    normalized_type = (
        normalize_analysis_type(
            analysis_type
        )
    )


    engine_version = (
        get_analysis_engine_version(
            normalized_type
        )
    )


    cache_path = (
        get_cache_path(
            owner,
            repo_name,
            normalized_type,
        )
    )


    payload = {
        "schema_version":
            CACHE_SCHEMA_VERSION,

        "analysis_engine_version":
            engine_version,

        "owner":
            owner,

        "repo_name":
            repo_name,

        "analysis_type":
            normalized_type,

        "commit_sha":
            commit_sha,

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "data":
            data,
    }


    temporary_path = (
        cache_path.with_suffix(
            ".tmp"
        )
    )


    try:

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=2,
            )


        temporary_path.replace(
            cache_path
        )


    except OSError:

        try:
            temporary_path.unlink(
                missing_ok=True
            )

        except OSError:
            pass


        raise


# =========================================================
# CACHE METADATA
# =========================================================

def get_cached_analysis_metadata(
    owner: str,
    repo_name: str,
    analysis_type: str,
) -> Optional[Dict]:

    cache_path = (
        get_cache_path(
            owner,
            repo_name,
            analysis_type,
        )
    )


    if not cache_path.exists():
        return None


    try:
        with cache_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            payload = (
                json.load(
                    file
                )
            )


    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None


    if not isinstance(
        payload,
        dict,
    ):
        return None


    return {
        "schema_version":
            payload.get(
                "schema_version"
            ),

        "analysis_engine_version":
            payload.get(
                "analysis_engine_version"
            ),

        "owner":
            payload.get(
                "owner"
            ),

        "repo_name":
            payload.get(
                "repo_name"
            ),

        "analysis_type":
            payload.get(
                "analysis_type"
            ),

        "commit_sha":
            payload.get(
                "commit_sha"
            ),

        "created_at":
            payload.get(
                "created_at"
            ),
    }


# =========================================================
# REMOVE CACHE
# =========================================================

def remove_cached_analysis(
    owner: str,
    repo_name: str,
    analysis_type: str,
):

    cache_path = (
        get_cache_path(
            owner,
            repo_name,
            analysis_type,
        )
    )


    try:
        cache_path.unlink(
            missing_ok=True
        )

    except OSError:
        pass


# =========================================================
# CLEAR REPOSITORY CACHE
# =========================================================

def clear_repository_analysis_cache(
    owner: str,
    repo_name: str,
):

    remove_cached_analysis(
        owner,
        repo_name,
        "architecture",
    )


    remove_cached_analysis(
        owner,
        repo_name,
        "insights",
    )


# =========================================================
# CLEAR ALL CACHE
# =========================================================

def clear_all_analysis_cache():

    try:

        for cache_file in (
            CACHE_DIRECTORY.glob(
                "*.json"
            )
        ):

            try:
                cache_file.unlink(
                    missing_ok=True
                )

            except OSError:
                continue


        for temporary_file in (
            CACHE_DIRECTORY.glob(
                "*.tmp"
            )
        ):

            try:
                temporary_file.unlink(
                    missing_ok=True
                )

            except OSError:
                continue


    except OSError:
        pass