import json
import os
import re

from pathlib import PurePosixPath

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import httpx

from dotenv import load_dotenv


load_dotenv()


GITHUB_API_URL = (
    "https://api.github.com"
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)


# =========================================================
# GITHUB ERROR
# =========================================================

class GitHubServiceError(
    ValueError
):
    def __init__(
        self,
        status_code: int,
        detail: str,
        retry_after:
            Optional[str] = None,
    ):
        super().__init__(
            detail
        )

        self.status_code = (
            status_code
        )

        self.detail = (
            detail
        )

        self.retry_after = (
            retry_after
        )


# =========================================================
# IGNORE RULES
# =========================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".cache",
    ".parcel-cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    "coverage",
    "target",
    "out",
    "tmp",
    "temp",
    "logs",
}


IGNORED_FILE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".bmp",
    ".svg",

    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",

    ".exe",
    ".dll",
    ".so",
    ".dylib",

    ".pyc",
    ".pyo",

    ".class",
    ".jar",

    ".mp3",
    ".wav",
    ".mp4",
    ".mov",
    ".avi",

    ".ttf",
    ".otf",
    ".woff",
    ".woff2",

    ".lock",
}


IGNORED_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}


# =========================================================
# HEADERS
# =========================================================

def get_github_headers() -> Dict[
    str,
    str,
]:
    headers = {
        "Accept":
            "application/vnd.github+json",

        "X-GitHub-Api-Version":
            "2022-11-28",

        "User-Agent":
            "CodeLens-AI",
    }


    if GITHUB_TOKEN:

        headers[
            "Authorization"
        ] = (
            f"Bearer {GITHUB_TOKEN}"
        )


    return headers


# =========================================================
# URL PARSING
# =========================================================

def parse_github_url(
    repo_url: str,
) -> Tuple[
    str,
    str,
]:
    repo_url = (
        repo_url
        .strip()
        .rstrip("/")
    )


    pattern = (
        r"^https?://(?:www\.)?"
        r"github\.com/"
        r"([^/]+)/"
        r"([^/]+)$"
    )


    match = re.match(
        pattern,
        repo_url,
    )


    if not match:

        raise ValueError(
            "Invalid GitHub repository URL."
        )


    owner = (
        match.group(
            1
        )
    )


    repo_name = (
        match.group(
            2
        )
    )


    if repo_name.endswith(
        ".git"
    ):

        repo_name = (
            repo_name[
                :-4
            ]
        )


    if (
        not owner
        or not repo_name
    ):

        raise ValueError(
            "Invalid GitHub repository URL."
        )


    return (
        owner,
        repo_name,
    )


# =========================================================
# GITHUB RESPONSE ERROR HANDLING
# =========================================================

def raise_for_github_response(
    response:
        httpx.Response,
):
    status_code = (
        response.status_code
    )


    if status_code == 200:
        return


    # -----------------------------------------------------
    # REPOSITORY / RESOURCE NOT FOUND
    # -----------------------------------------------------

    if status_code == 404:

        raise GitHubServiceError(
            status_code=404,
            detail=(
                "GitHub repository or resource "
                "was not found or is not accessible."
            ),
        )


    # -----------------------------------------------------
    # INVALID / EXPIRED TOKEN
    # -----------------------------------------------------

    if status_code == 401:

        raise GitHubServiceError(
            status_code=503,
            detail=(
                "GitHub authentication failed. "
                "The configured GitHub token may "
                "be invalid or expired."
            ),
        )


    # -----------------------------------------------------
    # FORBIDDEN / RATE LIMIT
    # -----------------------------------------------------

    if status_code == 403:

        remaining = (
            response.headers.get(
                "X-RateLimit-Remaining"
            )
        )


        retry_after = (
            response.headers.get(
                "Retry-After"
            )
        )


        message = ""

        try:

            payload = (
                response.json()
            )

            message = str(
                payload.get(
                    "message",
                    ""
                )
            ).lower()

        except Exception:

            message = ""


        is_rate_limit = (
            remaining == "0"
            or "rate limit"
            in message
            or "secondary rate limit"
            in message
        )


        if is_rate_limit:

            raise GitHubServiceError(
                status_code=429,
                detail=(
                    "GitHub API rate limit reached. "
                    "Please try again later."
                ),
                retry_after=
                    retry_after,
            )


        raise GitHubServiceError(
            status_code=403,
            detail=(
                "GitHub denied access to this "
                "repository or resource."
            ),
        )


    # -----------------------------------------------------
    # UNPROCESSABLE REQUEST
    # -----------------------------------------------------

    if status_code == 422:

        raise GitHubServiceError(
            status_code=422,
            detail=(
                "GitHub could not process this "
                "repository request."
            ),
        )


    # -----------------------------------------------------
    # GITHUB SERVER FAILURE
    # -----------------------------------------------------

    if (
        500
        <= status_code
        <= 599
    ):

        raise GitHubServiceError(
            status_code=503,
            detail=(
                "GitHub is temporarily unavailable. "
                "Please try again later."
            ),
        )


    # -----------------------------------------------------
    # UNKNOWN GITHUB FAILURE
    # -----------------------------------------------------

    raise GitHubServiceError(
        status_code=502,
        detail=(
            "GitHub returned an unexpected "
            f"response ({status_code})."
        ),
    )


# =========================================================
# GENERIC GITHUB GET
# =========================================================

async def github_get(
    endpoint: str,
):
    url = (
        f"{GITHUB_API_URL}"
        f"{endpoint}"
    )


    try:

        async with (
            httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            )
        ) as client:

            response = (
                await client.get(
                    url,
                    headers=
                        get_github_headers(),
                )
            )


    except httpx.TimeoutException as error:

        raise GitHubServiceError(
            status_code=504,
            detail=(
                "GitHub took too long to respond. "
                "Please try again."
            ),
        ) from error


    except httpx.RequestError as error:

        raise GitHubServiceError(
            status_code=503,
            detail=(
                "CodeLens could not connect to GitHub. "
                "Please try again later."
            ),
        ) from error


    raise_for_github_response(
        response
    )


    try:

        return response.json()


    except ValueError as error:

        raise GitHubServiceError(
            status_code=502,
            detail=(
                "GitHub returned an invalid response."
            ),
        ) from error


# =========================================================
# REPOSITORY METADATA
# =========================================================

async def get_repository_metadata(
    owner: str,
    repo_name: str,
):
    data = (
        await github_get(
            f"/repos/{owner}/{repo_name}"
        )
    )


    return {
        "repo_name":
            data.get(
                "name"
            ),

        "owner":
            data.get(
                "owner",
                {},
            ).get(
                "login"
            ),

        "description":
            data.get(
                "description"
            ),

        "default_branch":
            data.get(
                "default_branch"
            ),

        "language":
            data.get(
                "language"
            ),

        "stars":
            data.get(
                "stargazers_count",
                0,
            ),

        "forks":
            data.get(
                "forks_count",
                0,
            ),

        "open_issues":
            data.get(
                "open_issues_count",
                0,
            ),

        "visibility":
            data.get(
                "visibility"
            ),

        "is_private":
            data.get(
                "private",
                False,
            ),

        "github_url":
            data.get(
                "html_url"
            ),
    }


# =========================================================
# REPOSITORY TREE
# =========================================================

async def get_repository_tree(
    owner: str,
    repo_name: str,
    branch: str,
) -> List[dict]:
    data = (
        await github_get(
            f"/repos/{owner}/{repo_name}"
            f"/git/trees/{branch}"
            f"?recursive=1"
        )
    )


    tree = (
        data.get(
            "tree",
            [],
        )
    )


    if not isinstance(
        tree,
        list,
    ):

        raise GitHubServiceError(
            status_code=502,
            detail=(
                "GitHub returned an invalid "
                "repository tree."
            ),
        )


    return tree


# =========================================================
# PATH FILTERING
# =========================================================

def should_ignore_path(
    path: str,
) -> bool:
    pure_path = (
        PurePosixPath(
            path
        )
    )


    parts = (
        pure_path.parts
    )


    for part in parts:

        if (
            part
            in IGNORED_DIRECTORIES
        ):

            return True


    file_name = (
        pure_path.name
    )


    if (
        file_name
        in IGNORED_FILE_NAMES
    ):

        return True


    suffix = (
        pure_path
        .suffix
        .lower()
    )


    if (
        suffix
        in IGNORED_FILE_EXTENSIONS
    ):

        return True


    return False


def filter_repository_tree(
    tree: List[dict],
) -> List[dict]:
    filtered_tree = []


    for item in tree:

        path = (
            item.get(
                "path",
                "",
            )
        )


        if not path:
            continue


        if should_ignore_path(
            path
        ):
            continue


        filtered_tree.append(
            item
        )


    return filtered_tree


# =========================================================
# LANGUAGE PERCENTAGES
# =========================================================

async def get_language_percentages(
    owner: str,
    repo_name: str,
) -> Dict[
    str,
    float,
]:
    data = (
        await github_get(
            f"/repos/{owner}/{repo_name}"
            f"/languages"
        )
    )


    if not isinstance(
        data,
        dict,
    ):

        return {}


    total_bytes = sum(
        data.values()
    )


    if total_bytes == 0:

        return {}


    result = {}


    for (
        language,
        byte_count,
    ) in data.items():

        percentage = (
            byte_count
            / total_bytes
        ) * 100


        result[
            language
        ] = round(
            percentage,
            2,
        )


    return result


# =========================================================
# FILE CONTENT
# =========================================================

async def get_file_content(
    owner: str,
    repo_name: str,
    path: str,
) -> Optional[str]:
    endpoint = (
        f"/repos/{owner}/{repo_name}"
        f"/contents/{path}"
    )


    try:

        data = (
            await github_get(
                endpoint
            )
        )


    except GitHubServiceError as error:

        # A dependency/config file may disappear between
        # tree discovery and content fetching.
        if (
            error.status_code
            == 404
        ):

            return None

        raise


    if not isinstance(
        data,
        dict,
    ):

        return None


    download_url = (
        data.get(
            "download_url"
        )
    )


    if not download_url:

        return None


    try:

        async with (
            httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
            )
        ) as client:

            response = (
                await client.get(
                    download_url
                )
            )


    except httpx.TimeoutException as error:

        raise GitHubServiceError(
            status_code=504,
            detail=(
                "GitHub file download timed out."
            ),
        ) from error


    except httpx.RequestError as error:

        raise GitHubServiceError(
            status_code=503,
            detail=(
                "CodeLens could not download "
                "repository content from GitHub."
            ),
        ) from error


    if response.status_code == 404:

        return None


    if response.status_code == 429:

        raise GitHubServiceError(
            status_code=429,
            detail=(
                "GitHub API rate limit reached. "
                "Please try again later."
            ),
        )


    if (
        500
        <= response.status_code
        <= 599
    ):

        raise GitHubServiceError(
            status_code=503,
            detail=(
                "GitHub is temporarily unavailable."
            ),
        )


    if response.status_code != 200:

        return None


    return response.text


# =========================================================
# COUNTS
# =========================================================

def count_files(
    tree: List[dict],
) -> int:
    return sum(
        1

        for item
        in tree

        if (
            item.get(
                "type"
            )
            == "blob"
        )
    )


def count_directories(
    tree: List[dict],
) -> int:
    return sum(
        1

        for item
        in tree

        if (
            item.get(
                "type"
            )
            == "tree"
        )
    )


def count_root_modules(
    tree: List[dict],
) -> int:
    modules = set()


    for item in tree:

        if (
            item.get(
                "type"
            )
            != "tree"
        ):

            continue


        path = (
            item.get(
                "path",
                "",
            )
        )


        if "/" in path:
            continue


        modules.add(
            path
        )


    return len(
        modules
    )


def get_root_modules(
    tree: List[dict],
) -> List[str]:
    modules = set()


    for item in tree:

        if (
            item.get(
                "type"
            )
            != "tree"
        ):

            continue


        path = (
            item.get(
                "path",
                "",
            )
        )


        if "/" in path:
            continue


        modules.add(
            path
        )


    return sorted(
        modules
    )


# =========================================================
# DEPENDENCY DETECTION
# =========================================================

async def detect_dependencies(
    owner: str,
    repo_name: str,
    tree: List[dict],
) -> List[str]:
    file_paths = {
        item.get(
            "path"
        )

        for item
        in tree

        if (
            item.get(
                "type"
            )
            == "blob"
        )
    }


    dependencies = set()


    # -----------------------------------------------------
    # NODE / JAVASCRIPT
    # -----------------------------------------------------

    package_json_paths = [
        path

        for path
        in file_paths

        if (
            path
            and path.endswith(
                "package.json"
            )
        )
    ]


    for path in (
        package_json_paths
    ):

        content = (
            await get_file_content(
                owner,
                repo_name,
                path,
            )
        )


        if not content:
            continue


        try:

            package_data = (
                json.loads(
                    content
                )
            )


            dependencies.update(
                package_data.get(
                    "dependencies",
                    {},
                ).keys()
            )


            dependencies.update(
                package_data.get(
                    "devDependencies",
                    {},
                ).keys()
            )


        except json.JSONDecodeError:

            continue


    # -----------------------------------------------------
    # PYTHON
    # -----------------------------------------------------

    requirements_paths = [
        path

        for path
        in file_paths

        if (
            path
            and path.endswith(
                "requirements.txt"
            )
        )
    ]


    for path in (
        requirements_paths
    ):

        content = (
            await get_file_content(
                owner,
                repo_name,
                path,
            )
        )


        if not content:
            continue


        for line in (
            content.splitlines()
        ):

            line = (
                line.strip()
            )


            if not line:
                continue


            if line.startswith(
                "#"
            ):
                continue


            if line.startswith(
                "-"
            ):
                continue


            package_name = (
                re.split(
                    r"[=<>~!\[\]]",
                    line,
                )[0]
                .strip()
            )


            if package_name:

                dependencies.add(
                    package_name
                )


    return sorted(
        dependencies
    )


# =========================================================
# FRAMEWORK DETECTION
# =========================================================

def detect_framework(
    dependencies:
        List[str],
) -> Optional[str]:
    dependency_set = {
        item.lower()

        for item
        in dependencies
    }


    framework_map = {
        "next":
            "Next.js",

        "react":
            "React",

        "vue":
            "Vue",

        "@angular/core":
            "Angular",

        "express":
            "Express",

        "fastapi":
            "FastAPI",

        "django":
            "Django",

        "flask":
            "Flask",
    }


    for (
        dependency,
        framework,
    ) in framework_map.items():

        if (
            dependency
            in dependency_set
        ):

            return framework


    return None


# =========================================================
# BUILD TOOL DETECTION
# =========================================================

def detect_build_tool(
    dependencies:
        List[str],
) -> Optional[str]:
    dependency_set = {
        item.lower()

        for item
        in dependencies
    }


    tool_map = {
        "vite":
            "Vite",

        "webpack":
            "Webpack",

        "parcel":
            "Parcel",

        "rollup":
            "Rollup",
    }


    for (
        dependency,
        tool,
    ) in tool_map.items():

        if (
            dependency
            in dependency_set
        ):

            return tool


    return None


# =========================================================
# ARCHITECTURE TYPE
# =========================================================

def detect_architecture(
    tree: List[dict],
) -> str:
    paths = [
        item.get(
            "path",
            "",
        ).lower()

        for item
        in tree
    ]


    has_frontend = any(
        path.startswith(
            (
                "frontend/",
                "client/",
            )
        )

        for path
        in paths
    )


    has_backend = any(
        path.startswith(
            (
                "backend/",
                "server/",
                "api/",
            )
        )

        for path
        in paths
    )


    if (
        has_frontend
        and has_backend
    ):

        return (
            "Client-Server"
        )


    if has_frontend:

        return (
            "Frontend Application"
        )


    if has_backend:

        return (
            "Backend Application"
        )


    return (
        "Modular Application"
    )