import asyncio
import hashlib
import os
import re

from pathlib import Path
from pathlib import PurePosixPath

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

from urllib.parse import quote

import chromadb
import httpx

from dotenv import load_dotenv


load_dotenv()


# =========================================================
# CHROMA
# =========================================================

CHROMA_PATH = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    / "chroma_db"
)


client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# =========================================================
# INDEXING PERFORMANCE
# =========================================================

MAX_CONCURRENT_DOWNLOADS = 8

CHROMA_BATCH_SIZE = 64

HTTP_TIMEOUT = 30.0


# =========================================================
# FILE SUPPORT
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".py": "Python",
    ".java": "Java",
    ".go": "Go",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".sql": "SQL",
    ".md": "Markdown",
}


EXCLUDED_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}


EXCLUDED_PATH_PARTS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "coverage",
    ".next",
    ".vite",
    "vendor",
    "__pycache__",
}


LOW_PRIORITY_PATH_PARTS = {
    "assets",
    "fixtures",
    "mocks",
    "mock",
    "dummy",
    "examples",
}


MAX_FILE_SIZE = 300_000

FALLBACK_CHUNK_LINES = 70

FALLBACK_CHUNK_OVERLAP = 12


# Number of vector candidates retrieved
# before our own reranker selects final results.
CANDIDATE_MULTIPLIER = 4

MAX_CANDIDATES = 25


# =========================================================
# GITHUB HELPERS
# =========================================================

def get_github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CodeLens-AI",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    github_token = os.getenv(
        "GITHUB_TOKEN"
    )

    if github_token:
        headers[
            "Authorization"
        ] = (
            f"Bearer {github_token}"
        )

    return headers


async def get_latest_commit_sha(
    owner: str,
    repo_name: str,
    branch: str,
    http_client: Optional[
        httpx.AsyncClient
    ] = None,
) -> Optional[str]:
    encoded_branch = quote(
        branch,
        safe="",
    )

    url = (
        "https://api.github.com/repos/"
        f"{owner}/"
        f"{repo_name}/"
        "commits/"
        f"{encoded_branch}"
    )

    owns_client = (
        http_client is None
    )

    if owns_client:
        http_client = (
            httpx.AsyncClient(
                timeout=HTTP_TIMEOUT,
                headers=
                    get_github_headers(),
            )
        )

    try:
        response = (
            await http_client.get(
                url
            )
        )

        if (
            response.status_code
            != 200
        ):
            return None

        data = response.json()

        commit_sha = (
            data.get(
                "sha"
            )
        )

        if not commit_sha:
            return None

        return str(
            commit_sha
        )

    except (
        httpx.RequestError,
        ValueError,
    ):
        return None

    finally:
        if owns_client:
            await http_client.aclose()


# =========================================================
# COLLECTION HELPERS
# =========================================================

def sanitize_collection_name(
    owner: str,
    repo_name: str,
) -> str:
    raw = (
        f"{owner}-{repo_name}"
        .lower()
    )

    cleaned = re.sub(
        r"[^a-z0-9_-]",
        "-",
        raw,
    )

    cleaned = re.sub(
        r"-+",
        "-",
        cleaned,
    )

    digest = (
        hashlib.sha1(
            raw.encode(
                "utf-8"
            )
        )
        .hexdigest()[:8]
    )

    name = (
        f"{cleaned}-{digest}"
    )

    return name[:63]


def get_repository_collection(
    owner: str,
    repo_name: str,
):
    name = (
        sanitize_collection_name(
            owner,
            repo_name,
        )
    )

    try:
        return (
            client.get_collection(
                name=name
            )
        )

    except Exception:
        raise ValueError(
            "Repository has not been indexed yet."
        )


def get_existing_repository_collection(
    owner: str,
    repo_name: str,
):
    name = (
        sanitize_collection_name(
            owner,
            repo_name,
        )
    )

    try:
        return (
            client.get_collection(
                name=name
            )
        )

    except Exception:
        return None


def reset_repository_collection(
    owner: str,
    repo_name: str,
    commit_sha: Optional[
        str
    ] = None,
):
    name = (
        sanitize_collection_name(
            owner,
            repo_name,
        )
    )

    try:
        client.delete_collection(
            name=name
        )

    except Exception:
        pass

    metadata = {
        "owner":
            owner,

        "repository":
            repo_name,
    }

    if commit_sha:
        metadata[
            "commit_sha"
        ] = commit_sha

    return (
        client.get_or_create_collection(
            name=name,
            metadata=metadata,
        )
    )


def get_collection_commit_sha(
    collection,
) -> Optional[str]:
    metadata = (
        collection.metadata
        or {}
    )

    commit_sha = (
        metadata.get(
            "commit_sha"
        )
    )

    if not commit_sha:
        return None

    return str(
        commit_sha
    )


def collection_is_current(
    collection,
    commit_sha: Optional[str],
) -> bool:
    if not collection:
        return False

    if not commit_sha:
        return False

    try:
        count = (
            collection.count()
        )

    except Exception:
        return False

    if count <= 0:
        return False

    stored_sha = (
        get_collection_commit_sha(
            collection
        )
    )

    return (
        stored_sha
        == commit_sha
    )


def repository_index_exists(
    owner: str,
    repo_name: str,
) -> bool:
    collection = (
        get_existing_repository_collection(
            owner,
            repo_name,
        )
    )

    if not collection:
        return False

    try:
        return (
            collection.count()
            > 0
        )

    except Exception:
        return False


# =========================================================
# FILE FILTERING
# =========================================================

def should_index_file(
    path: str,
) -> bool:
    pure_path = (
        PurePosixPath(
            path
        )
    )

    if (
        pure_path.name
        in EXCLUDED_FILE_NAMES
    ):
        return False

    lower_parts = {
        part.lower()
        for part
        in pure_path.parts
    }

    if (
        lower_parts
        & EXCLUDED_PATH_PARTS
    ):
        return False

    extension = (
        pure_path
        .suffix
        .lower()
    )

    return (
        extension
        in SUPPORTED_EXTENSIONS
    )


def get_language(
    path: str,
) -> Optional[str]:
    extension = (
        PurePosixPath(
            path
        )
        .suffix
        .lower()
    )

    return (
        SUPPORTED_EXTENSIONS.get(
            extension
        )
    )


# =========================================================
# RAW FILE FETCH
# =========================================================

async def fetch_raw_file(
    owner: str,
    repo_name: str,
    branch: str,
    path: str,
    http_client: Optional[
        httpx.AsyncClient
    ] = None,
) -> Optional[str]:
    encoded_path = quote(
        path,
        safe="/",
    )

    encoded_branch = quote(
        branch,
        safe="",
    )

    url = (
        "https://raw.githubusercontent.com/"
        f"{owner}/"
        f"{repo_name}/"
        f"{encoded_branch}/"
        f"{encoded_path}"
    )

    owns_client = (
        http_client is None
    )

    if owns_client:
        http_client = (
            httpx.AsyncClient(
                timeout=HTTP_TIMEOUT,
                headers=
                    get_github_headers(),
                follow_redirects=True,
            )
        )

    try:
        response = (
            await http_client.get(
                url
            )
        )

    except httpx.RequestError:
        return None

    finally:
        if (
            owns_client
            and http_client
        ):
            await http_client.aclose()

    if (
        response.status_code
        != 200
    ):
        return None

    content = (
        response.text
    )

    size = len(
        content.encode(
            "utf-8"
        )
    )

    if (
        size
        > MAX_FILE_SIZE
    ):
        return None

    return content


async def fetch_repository_files(
    owner: str,
    repo_name: str,
    branch: str,
    paths: List[str],
) -> List[
    Tuple[
        str,
        Optional[str],
    ]
]:
    semaphore = (
        asyncio.Semaphore(
            MAX_CONCURRENT_DOWNLOADS
        )
    )

    async with httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        headers=
            get_github_headers(),
        follow_redirects=True,
        limits=httpx.Limits(
            max_connections=
                MAX_CONCURRENT_DOWNLOADS,
            max_keepalive_connections=
                MAX_CONCURRENT_DOWNLOADS,
        ),
    ) as http_client:

        async def fetch_one(
            path: str,
        ):
            async with semaphore:
                content = (
                    await fetch_raw_file(
                        owner=
                            owner,

                        repo_name=
                            repo_name,

                        branch=
                            branch,

                        path=
                            path,

                        http_client=
                            http_client,
                    )
                )

                return (
                    path,
                    content,
                )

        tasks = [
            fetch_one(
                path
            )
            for path
            in paths
        ]

        return (
            await asyncio.gather(
                *tasks
            )
        )


# =========================================================
# GENERIC LINE CHUNKING
# =========================================================

def fallback_line_chunks(
    path: str,
    content: str,
) -> List[Dict]:
    lines = (
        content.splitlines()
    )

    if not lines:
        return []

    chunks = []

    step = (
        FALLBACK_CHUNK_LINES
        -
        FALLBACK_CHUNK_OVERLAP
    )

    start = 0

    while (
        start
        < len(lines)
    ):
        end = min(
            start
            +
            FALLBACK_CHUNK_LINES,
            len(lines),
        )

        text = "\n".join(
            lines[
                start:end
            ]
        ).strip()

        if text:
            chunks.append(
                {
                    "path":
                        path,

                    "language":
                        get_language(
                            path
                        ),

                    "start_line":
                        start + 1,

                    "end_line":
                        end,

                    "content":
                        text,

                    "symbol":
                        "",

                    "chunk_type":
                        "line",
                }
            )

        if (
            end
            >= len(lines)
        ):
            break

        start += step

    return chunks


# =========================================================
# JAVASCRIPT / TYPESCRIPT FUNCTION CHUNKING
# =========================================================

def find_matching_brace(
    content: str,
    opening_index: int,
) -> Optional[int]:
    depth = 0

    quote_char = None

    escaped = False

    index = (
        opening_index
    )

    while (
        index
        < len(content)
    ):
        char = (
            content[index]
        )

        next_char = (
            content[index + 1]
            if index + 1
            < len(content)
            else ""
        )

        if escaped:
            escaped = False
            index += 1
            continue

        if (
            char == "\\"
            and quote_char
        ):
            escaped = True
            index += 1
            continue

        if quote_char:
            if (
                char ==
                quote_char
            ):
                quote_char = None

            index += 1
            continue

        if (
            char == "/"
            and next_char == "/"
        ):
            newline = (
                content.find(
                    "\n",
                    index,
                )
            )

            if newline == -1:
                return None

            index = (
                newline + 1
            )

            continue

        if (
            char == "/"
            and next_char == "*"
        ):
            closing = (
                content.find(
                    "*/",
                    index + 2,
                )
            )

            if closing == -1:
                return None

            index = (
                closing + 2
            )

            continue

        if char in {
            "'",
            '"',
            "`",
        }:
            quote_char = (
                char
            )

            index += 1
            continue

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if (
                depth == 0
            ):
                return index

        index += 1

    return None


def character_to_line(
    content: str,
    character_index: int,
) -> int:
    return (
        content.count(
            "\n",
            0,
            character_index,
        )
        + 1
    )


def extract_javascript_functions(
    path: str,
    content: str,
) -> List[Dict]:
    matches = []

    patterns = [
        # export const foo = async (...) => {
        re.compile(
            (
                r"(?:export\s+)?"
                r"(?:const|let|var)\s+"
                r"([A-Za-z_$][\w$]*)"
                r"\s*=\s*"
                r"(?:async\s*)?"
                r"\([^)]*\)"
                r"\s*=>\s*\{"
            )
        ),

        # export const foo = async x => {
        re.compile(
            (
                r"(?:export\s+)?"
                r"(?:const|let|var)\s+"
                r"([A-Za-z_$][\w$]*)"
                r"\s*=\s*"
                r"(?:async\s*)?"
                r"[A-Za-z_$][\w$]*"
                r"\s*=>\s*\{"
            )
        ),

        # async function foo(...) {
        re.compile(
            (
                r"(?:export\s+)?"
                r"(?:async\s+)?"
                r"function\s+"
                r"([A-Za-z_$][\w$]*)"
                r"\s*\([^)]*\)"
                r"\s*\{"
            )
        ),
    ]

    seen = set()

    for pattern in patterns:
        for match in (
            pattern.finditer(
                content
            )
        ):
            symbol = (
                match.group(1)
            )

            brace_index = (
                content.find(
                    "{",
                    match.start(),
                    match.end(),
                )
            )

            if (
                brace_index
                == -1
            ):
                continue

            closing_index = (
                find_matching_brace(
                    content,
                    brace_index,
                )
            )

            if (
                closing_index
                is None
            ):
                continue

            key = (
                match.start(),
                closing_index,
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            start_line = (
                character_to_line(
                    content,
                    match.start(),
                )
            )

            end_line = (
                character_to_line(
                    content,
                    closing_index,
                )
            )

            function_content = (
                content[
                    match.start():
                    closing_index + 1
                ]
                .strip()
            )

            if not function_content:
                continue

            matches.append(
                {
                    "path":
                        path,

                    "language":
                        get_language(
                            path
                        ),

                    "start_line":
                        start_line,

                    "end_line":
                        end_line,

                    "content":
                        function_content,

                    "symbol":
                        symbol,

                    "chunk_type":
                        "function",
                }
            )

    matches.sort(
        key=lambda item:
            item[
                "start_line"
            ]
    )

    return matches


# =========================================================
# PYTHON FUNCTION CHUNKING
# =========================================================

def extract_python_functions(
    path: str,
    content: str,
) -> List[Dict]:
    lines = (
        content.splitlines()
    )

    chunks = []

    definition_pattern = (
        re.compile(
            (
                r"^(\s*)"
                r"(?:async\s+)?"
                r"def\s+"
                r"([A-Za-z_][\w]*)"
                r"\s*\("
            )
        )
    )

    index = 0

    while (
        index
        < len(lines)
    ):
        match = (
            definition_pattern.match(
                lines[index]
            )
        )

        if not match:
            index += 1
            continue

        indentation = len(
            match.group(1)
        )

        symbol = (
            match.group(2)
        )

        start = index

        end = (
            index + 1
        )

        while (
            end
            < len(lines)
        ):
            line = (
                lines[end]
            )

            if (
                not line.strip()
            ):
                end += 1
                continue

            current_indent = (
                len(line)
                -
                len(
                    line.lstrip()
                )
            )

            if (
                current_indent
                <= indentation
                and
                definition_pattern.match(
                    line
                )
            ):
                break

            if (
                current_indent
                < indentation
            ):
                break

            end += 1

        function_content = (
            "\n".join(
                lines[
                    start:end
                ]
            )
            .strip()
        )

        if function_content:
            chunks.append(
                {
                    "path":
                        path,

                    "language":
                        get_language(
                            path
                        ),

                    "start_line":
                        start + 1,

                    "end_line":
                        end,

                    "content":
                        function_content,

                    "symbol":
                        symbol,

                    "chunk_type":
                        "function",
                }
            )

        index = (
            max(
                index + 1,
                end,
            )
        )

    return chunks


# =========================================================
# CODE-AWARE CHUNKING
# =========================================================

def chunk_file(
    path: str,
    content: str,
) -> List[Dict]:
    suffix = (
        PurePosixPath(
            path
        )
        .suffix
        .lower()
    )

    function_chunks = []

    if suffix in {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
    }:
        function_chunks = (
            extract_javascript_functions(
                path,
                content,
            )
        )

    elif suffix == ".py":
        function_chunks = (
            extract_python_functions(
                path,
                content,
            )
        )

    fallback_chunks = (
        fallback_line_chunks(
            path,
            content,
        )
    )

    if not function_chunks:
        return (
            fallback_chunks
        )

    combined = []

    combined.extend(
        function_chunks
    )

    # Keep file-level context as well because
    # imports/routes can live outside functions.
    combined.extend(
        fallback_chunks
    )

    return combined


# =========================================================
# DOCUMENT TEXT FOR EMBEDDINGS
# =========================================================

def build_embedding_document(
    chunk: Dict,
) -> str:
    path = (
        chunk["path"]
    )

    language = (
        chunk.get(
            "language"
        )
        or "Unknown"
    )

    symbol = (
        chunk.get(
            "symbol"
        )
        or ""
    )

    chunk_type = (
        chunk.get(
            "chunk_type"
        )
        or "code"
    )

    header_parts = [
        f"File: {path}",
        f"Language: {language}",
        f"Chunk type: {chunk_type}",
    ]

    if symbol:
        header_parts.append(
            f"Function: {symbol}"
        )

    header = "\n".join(
        header_parts
    )

    return (
        f"{header}\n\n"
        f"{chunk['content']}"
    )


# =========================================================
# IDS
# =========================================================

def create_chunk_id(
    path: str,
    start_line: int,
    content: str,
    symbol: str = "",
) -> str:
    raw = (
        f"{path}:"
        f"{symbol}:"
        f"{start_line}:"
        f"{content}"
    )

    return (
        hashlib.sha1(
            raw.encode(
                "utf-8"
            )
        )
        .hexdigest()
    )


# =========================================================
# BATCH HELPERS
# =========================================================

def split_batches(
    values: List,
    batch_size: int,
):
    for start in range(
        0,
        len(values),
        batch_size,
    ):
        yield values[
            start:
            start + batch_size
        ]


# =========================================================
# INDEXING
# =========================================================

async def index_repository(
    owner: str,
    repo_name: str,
    branch: str,
    tree: List[dict],
    force: bool = False,
):
    async with httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        headers=
            get_github_headers(),
        follow_redirects=True,
    ) as http_client:
        commit_sha = (
            await get_latest_commit_sha(
                owner=
                    owner,

                repo_name=
                    repo_name,

                branch=
                    branch,

                http_client=
                    http_client,
            )
        )

    existing_collection = (
        get_existing_repository_collection(
            owner,
            repo_name,
        )
    )

    if (
        not force
        and
        collection_is_current(
            existing_collection,
            commit_sha,
        )
    ):
        existing_count = (
            existing_collection.count()
        )

        return {
            "collection_name":
                existing_collection.name,

            "indexed_files":
                0,

            "indexed_chunks":
                existing_count,

            "files":
                [],

            "cached":
                True,

            "commit_sha":
                commit_sha,

            "status":
                "repository index already current",
        }

    indexable_paths = []

    for item in tree:
        if (
            item.get("type")
            != "blob"
        ):
            continue

        path = (
            item.get(
                "path",
                ""
            )
        )

        if not path:
            continue

        if not should_index_file(
            path
        ):
            continue

        indexable_paths.append(
            path
        )

    downloaded_files = (
        await fetch_repository_files(
            owner=
                owner,

            repo_name=
                repo_name,

            branch=
                branch,

            paths=
                indexable_paths,
        )
    )

    collection = (
        reset_repository_collection(
            owner=
                owner,

            repo_name=
                repo_name,

            commit_sha=
                commit_sha,
        )
    )

    indexed_files = []

    all_ids = []

    all_documents = []

    all_metadatas = []

    total_chunks = 0

    for (
        path,
        content,
    ) in downloaded_files:
        if not content:
            continue

        chunks = (
            chunk_file(
                path,
                content,
            )
        )

        if not chunks:
            continue

        indexed_files.append(
            {
                "path":
                    path,

                "chunk_count":
                    len(chunks),
            }
        )

        total_chunks += (
            len(chunks)
        )

        for chunk in chunks:
            symbol = (
                chunk.get(
                    "symbol"
                )
                or ""
            )

            chunk_id = (
                create_chunk_id(
                    path=
                        chunk[
                            "path"
                        ],

                    start_line=
                        chunk[
                            "start_line"
                        ],

                    content=
                        chunk[
                            "content"
                        ],

                    symbol=
                        symbol,
                )
            )

            all_ids.append(
                chunk_id
            )

            all_documents.append(
                build_embedding_document(
                    chunk
                )
            )

            all_metadatas.append(
                {
                    "path":
                        chunk[
                            "path"
                        ],

                    "language":
                        chunk[
                            "language"
                        ]
                        or "Unknown",

                    "start_line":
                        chunk[
                            "start_line"
                        ],

                    "end_line":
                        chunk[
                            "end_line"
                        ],

                    "symbol":
                        symbol,

                    "chunk_type":
                        chunk.get(
                            "chunk_type",
                            "code",
                        ),
                }
            )

    if all_ids:
        for batch_start in range(
            0,
            len(all_ids),
            CHROMA_BATCH_SIZE,
        ):
            batch_end = (
                batch_start
                +
                CHROMA_BATCH_SIZE
            )

            collection.add(
                ids=
                    all_ids[
                        batch_start:
                        batch_end
                    ],

                documents=
                    all_documents[
                        batch_start:
                        batch_end
                    ],

                metadatas=
                    all_metadatas[
                        batch_start:
                        batch_end
                    ],
            )

    final_metadata = {
        "owner":
            owner,

        "repository":
            repo_name,

        "branch":
            branch,

        "indexed_files":
            len(
                indexed_files
            ),

        "indexed_chunks":
            total_chunks,
    }

    if commit_sha:
        final_metadata[
            "commit_sha"
        ] = commit_sha

    try:
        collection.modify(
            metadata=
                final_metadata
        )

    except Exception:
        pass

    return {
        "collection_name":
            collection.name,

        "indexed_files":
            len(
                indexed_files
            ),

        "indexed_chunks":
            total_chunks,

        "files":
            indexed_files,

        "cached":
            False,

        "commit_sha":
            commit_sha,

        "status":
            "repository indexed",
    }


async def check_repository_index_freshness(
    owner: str,
    repo_name: str,
    branch: str,
) -> Dict:
    collection = (
        get_existing_repository_collection(
            owner,
            repo_name,
        )
    )

    if not collection:
        return {
            "indexed":
                False,

            "fresh":
                False,

            "indexed_chunks":
                0,

            "commit_sha":
                None,

            "stored_commit_sha":
                None,
        }

    try:
        indexed_chunks = (
            collection.count()
        )

    except Exception:
        indexed_chunks = 0

    latest_commit_sha = (
        await get_latest_commit_sha(
            owner=
                owner,

            repo_name=
                repo_name,

            branch=
                branch,
        )
    )

    stored_commit_sha = (
        get_collection_commit_sha(
            collection
        )
    )

    fresh = (
        indexed_chunks > 0
        and
        latest_commit_sha
        is not None
        and
        stored_commit_sha
        ==
        latest_commit_sha
    )

    return {
        "indexed":
            indexed_chunks
            > 0,

        "fresh":
            fresh,

        "indexed_chunks":
            indexed_chunks,

        "commit_sha":
            latest_commit_sha,

        "stored_commit_sha":
            stored_commit_sha,
    }


# =========================================================
# QUERY PROCESSING
# =========================================================

def tokenize_query(
    question: str,
) -> List[str]:
    raw_tokens = re.findall(
        r"[A-Za-z0-9_-]+",
        question.lower(),
    )

    stop_words = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "how",
        "what",
        "where",
        "when",
        "why",
        "which",
        "who",
        "does",
        "do",
        "did",
        "this",
        "that",
        "these",
        "those",
        "in",
        "on",
        "at",
        "to",
        "from",
        "for",
        "of",
        "with",
        "and",
        "or",
        "as",
        "it",
        "its",
        "work",
        "works",
    }

    return [
        token
        for token
        in raw_tokens
        if (
            len(token) > 1
            and token
            not in stop_words
        )
    ]


def normalize_identifier(
    value: str,
) -> str:
    value = re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1 \2",
        value,
    )

    value = value.replace(
        "_",
        " ",
    )

    value = value.replace(
        "-",
        " ",
    )

    return (
        value.lower()
    )


def lexical_score(
    question: str,
    path: str,
    symbol: str,
    content: str,
) -> float:
    tokens = (
        tokenize_query(
            question
        )
    )

    if not tokens:
        return 0.0

    normalized_path = (
        normalize_identifier(
            path
        )
    )

    normalized_symbol = (
        normalize_identifier(
            symbol
        )
    )

    normalized_content = (
        normalize_identifier(
            content
        )
    )

    score = 0.0

    for token in tokens:
        if (
            token
            in normalized_symbol
        ):
            score += 3.5

        if (
            token
            in normalized_path
        ):
            score += 2.5

        if (
            token
            in normalized_content
        ):
            score += 1.0

    return score


def architecture_role_score(
    question: str,
    path: str,
    symbol: str,
) -> float:
    question_lower = (
        question.lower()
    )

    path_lower = (
        path.lower()
    )

    symbol_lower = (
        symbol.lower()
    )

    score = 0.0

    implementation_words = {
        "how",
        "work",
        "works",
        "implemented",
        "implementation",
        "generate",
        "generation",
        "remove",
        "store",
        "stored",
        "retrieve",
        "retrieved",
    }

    if any(
        word in question_lower
        for word
        in implementation_words
    ):
        if (
            "/controllers/"
            in path_lower
        ):
            score += 3.0

        if (
            "/routes/"
            in path_lower
        ):
            score += 2.0

        if (
            "/pages/"
            in path_lower
        ):
            score += 1.5

        if (
            "/services/"
            in path_lower
        ):
            score += 2.5

        if (
            "/configs/"
            in path_lower
            or "/config/"
            in path_lower
        ):
            score += 0.8

    if (
        "image"
        in question_lower
    ):
        if (
            "image"
            in path_lower
        ):
            score += 2.5

        if (
            "image"
            in symbol_lower
        ):
            score += 3.5

    if (
        "database"
        in question_lower
        or "stored"
        in question_lower
        or "storage"
        in question_lower
    ):
        if (
            "db."
            in path_lower
            or "/models/"
            in path_lower
            or "/controllers/"
            in path_lower
        ):
            score += 2.5

    return score


def noise_penalty(
    path: str,
) -> float:
    lower_path = (
        path.lower()
    )

    parts = {
        part.lower()
        for part
        in PurePosixPath(
            lower_path
        ).parts
    }

    penalty = 0.0

    if (
        parts
        & LOW_PRIORITY_PATH_PARTS
    ):
        penalty += 3.0

    if (
        "testimonial"
        in lower_path
    ):
        penalty += 3.0

    if (
        "dummy"
        in lower_path
    ):
        penalty += 2.0

    if (
        "eslint.config"
        in lower_path
        or "vite.config"
        in lower_path
    ):
        penalty += 2.0

    return penalty


# =========================================================
# SEMANTIC + HYBRID SCORING
# =========================================================

def semantic_score_from_distance(
    distance: Optional[float],
) -> float:
    if distance is None:
        return 0.0

    return (
        1.0
        /
        (
            1.0
            +
            max(
                float(distance),
                0.0,
            )
        )
    )


def rerank_result(
    question: str,
    result: Dict,
) -> float:
    semantic = (
        semantic_score_from_distance(
            result.get(
                "distance"
            )
        )
    )

    lexical = (
        lexical_score(
            question=
                question,

            path=
                result[
                    "path"
                ],

            symbol=
                result.get(
                    "symbol",
                    "",
                ),

            content=
                result[
                    "content"
                ],
        )
    )

    architecture = (
        architecture_role_score(
            question=
                question,

            path=
                result[
                    "path"
                ],

            symbol=
                result.get(
                    "symbol",
                    "",
                ),
        )
    )

    penalty = (
        noise_penalty(
            result[
                "path"
            ]
        )
    )

    chunk_bonus = 0.0

    if (
        result.get(
            "chunk_type"
        )
        == "function"
    ):
        chunk_bonus = 1.5

    score = (
        semantic * 4.0
        +
        lexical
        +
        architecture
        +
        chunk_bonus
        -
        penalty
    )

    return score


# =========================================================
# RESULT DIVERSIFICATION
# =========================================================

def diversify_results(
    ranked_results: List[Dict],
    limit: int,
) -> List[Dict]:
    selected = []

    per_file_count: Dict[
        str,
        int,
    ] = {}

    # Maximum two chunks from one file.
    for result in (
        ranked_results
    ):
        path = (
            result[
                "path"
            ]
        )

        current_count = (
            per_file_count.get(
                path,
                0,
            )
        )

        if (
            current_count >= 2
        ):
            continue

        selected.append(
            result
        )

        per_file_count[
            path
        ] = (
            current_count + 1
        )

        if (
            len(selected)
            >= limit
        ):
            break

    return selected


# =========================================================
# RETRIEVAL
# =========================================================

def retrieve_repository_context(
    owner: str,
    repo_name: str,
    question: str,
    limit: int = 6,
):
    collection = (
        get_repository_collection(
            owner,
            repo_name,
        )
    )

    count = (
        collection.count()
    )

    if count == 0:
        raise ValueError(
            "Repository has not been indexed yet."
        )

    safe_limit = max(
        1,
        min(
            limit,
            10,
        ),
    )

    candidate_count = min(
        count,
        MAX_CANDIDATES,
        max(
            safe_limit
            *
            CANDIDATE_MULTIPLIER,
            12,
        ),
    )

    results = (
        collection.query(
            query_texts=[
                question
            ],

            n_results=
                candidate_count,

            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )
    )

    ids = (
        results.get(
            "ids",
            [[]],
        )[0]
    )

    documents = (
        results.get(
            "documents",
            [[]],
        )[0]
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]],
        )[0]
    )

    distances = (
        results.get(
            "distances",
            [[]],
        )[0]
    )

    candidates = []

    for index in range(
        len(ids)
    ):
        metadata = (
            metadatas[
                index
            ]
            or {}
        )

        distance = None

        if (
            index
            < len(distances)
        ):
            distance = (
                distances[
                    index
                ]
            )

        document = (
            documents[
                index
            ]
        )

        # Remove embedding metadata header
        # before returning code to caller.
        if "\n\n" in document:
            code_content = (
                document
                .split(
                    "\n\n",
                    1,
                )[1]
            )

        else:
            code_content = (
                document
            )

        candidate = {
            "chunk_id":
                ids[
                    index
                ],

            "path":
                metadata.get(
                    "path",
                    "Unknown",
                ),

            "language":
                metadata.get(
                    "language"
                ),

            "start_line":
                int(
                    metadata.get(
                        "start_line",
                        0,
                    )
                ),

            "end_line":
                int(
                    metadata.get(
                        "end_line",
                        0,
                    )
                ),

            "content":
                code_content,

            "distance":
                distance,

            "symbol":
                metadata.get(
                    "symbol",
                    "",
                ),

            "chunk_type":
                metadata.get(
                    "chunk_type",
                    "code",
                ),
        }

        candidate[
            "_rerank_score"
        ] = (
            rerank_result(
                question,
                candidate,
            )
        )

        candidates.append(
            candidate
        )

    candidates.sort(
        key=lambda item:
            item[
                "_rerank_score"
            ],
        reverse=True,
    )

    selected = (
        diversify_results(
            candidates,
            safe_limit,
        )
    )

    final_results = []

    for result in (
        selected
    ):
        final_results.append(
            {
                "chunk_id":
                    result[
                        "chunk_id"
                    ],

                "path":
                    result[
                        "path"
                    ],

                "language":
                    result[
                        "language"
                    ],

                "start_line":
                    result[
                        "start_line"
                    ],

                "end_line":
                    result[
                        "end_line"
                    ],

                "content":
                    result[
                        "content"
                    ],

                "distance":
                    result[
                        "distance"
                    ],
            }
        )

    return final_results