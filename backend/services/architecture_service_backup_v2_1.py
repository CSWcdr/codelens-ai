import asyncio
import re

from pathlib import PurePosixPath

from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

from urllib.parse import (
    quote,
    urlparse,
)

import httpx


# =========================================================
# SOURCE / LANGUAGE CONFIG
# =========================================================

SOURCE_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".mts",
    ".cts",
    ".vue",
    ".svelte",
    ".py",
    ".java",
    ".kt",
    ".go",
    ".cs",
    ".php",
    ".rb",
}


LANGUAGE_MAP = {
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".mts": "TypeScript",
    ".cts": "TypeScript",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".py": "Python",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
}


JS_EXTENSIONS = (
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".mts",
    ".cts",
    ".vue",
    ".svelte",
)


CONFIG_FILE_NAMES = {
    "eslint.config.js",
    "eslint.config.mjs",
    "vite.config.js",
    "vite.config.ts",
    "webpack.config.js",
    "webpack.config.ts",
    "tailwind.config.js",
    "tailwind.config.ts",
    "postcss.config.js",
    "jest.config.js",
    "jest.config.ts",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
}


SUPPORT_FILE_NAMES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "pipfile",
    "schema.prisma",
    "docker-compose.yml",
    "docker-compose.yaml",
}


# =========================================================
# DATA LAYER PACKAGES
# =========================================================

DATA_PACKAGE_MAP = {
    "@neondatabase/serverless":
        "PostgreSQL",

    "pg":
        "PostgreSQL",

    "postgres":
        "PostgreSQL",

    "postgresql":
        "PostgreSQL",

    "psycopg":
        "PostgreSQL",

    "psycopg2":
        "PostgreSQL",

    "asyncpg":
        "PostgreSQL",

    "mongoose":
        "MongoDB / Mongoose",

    "mongodb":
        "MongoDB",

    "pymongo":
        "MongoDB / PyMongo",

    "@prisma/client":
        "Prisma",

    "prisma":
        "Prisma",

    "firebase":
        "Firebase",

    "firebase-admin":
        "Firebase",

    "@supabase/supabase-js":
        "Supabase",

    "supabase":
        "Supabase",

    "sqlalchemy":
        "SQLAlchemy",

    "sequelize":
        "Sequelize",

    "typeorm":
        "TypeORM",

    "mysql":
        "MySQL",

    "mysql2":
        "MySQL",

    "sqlite3":
        "SQLite",

    "better-sqlite3":
        "SQLite",

    "aiosqlite":
        "SQLite",

    "redis":
        "Redis",

    "ioredis":
        "Redis",

    "@upstash/redis":
        "Redis",

    "drizzle-orm":
        "Drizzle ORM",

    "knex":
        "Knex",

    "dynamodb":
        "DynamoDB",

    "@aws-sdk/client-dynamodb":
        "DynamoDB",

    "@aws-sdk/lib-dynamodb":
        "DynamoDB",

    "boto3":
        "AWS Data Service",
}


# =========================================================
# EXTERNAL PROVIDER PACKAGES
# =========================================================

PROVIDER_PACKAGE_MAP = {
    "groq-sdk":
        "Groq API",

    "groq":
        "Groq API",

    "openai":
        "OpenAI API",

    "@anthropic-ai/sdk":
        "Anthropic API",

    "anthropic":
        "Anthropic API",

    "@google/generative-ai":
        "Google Gemini API",

    "google-generativeai":
        "Google Gemini API",

    "google.generativeai":
        "Google Gemini API",

    "@google/genai":
        "Google Gemini API",

    "mistralai":
        "Mistral API",

    "cohere-ai":
        "Cohere API",

    "cohere":
        "Cohere API",

    "@huggingface/inference":
        "Hugging Face API",

    "huggingface_hub":
        "Hugging Face API",

    "stripe":
        "Stripe API",

    "@sendgrid/mail":
        "SendGrid API",

    "twilio":
        "Twilio API",
}


HTTP_METHODS = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
)


URLISH_WORDS = (
    "URL",
    "BASE",
    "HOST",
    "ORIGIN",
    "ENDPOINT",
)


FRONTEND_PATH_MARKERS = {
    "frontend",
    "client",
    "web",
    "ui",
}


BACKEND_PATH_MARKERS = {
    "backend",
    "server",
    "api",
}


FRONTEND_STRUCTURE_MARKERS = {
    "components",
    "pages",
    "views",
    "hooks",
    "layouts",
    "screens",
}


BACKEND_STRUCTURE_MARKERS = {
    "controllers",
    "controller",
    "routes",
    "route",
    "middleware",
    "middlewares",
    "services",
    "repositories",
    "validators",
}


# =========================================================
# RAW GITHUB SOURCE
# =========================================================

async def get_raw_file_content(
    owner: str,
    repo_name: str,
    branch: str,
    path: str,
    client: Optional[
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


    async def _request(
        active_client:
            httpx.AsyncClient,
    ) -> Optional[str]:

        try:
            response = (
                await active_client.get(
                    url
                )
            )

        except httpx.RequestError:
            return None


        if (
            response.status_code
            != 200
        ):
            return None


        return response.text


    if client is not None:
        return await _request(
            client
        )


    async with (
        httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
        )
    ) as temporary_client:

        return await _request(
            temporary_client
        )


async def fetch_repository_contents(
    owner: str,
    repo_name: str,
    branch: str,
    paths: List[str],
    concurrency: int = 12,
) -> Dict[str, str]:

    contents: Dict[
        str,
        str,
    ] = {}


    semaphore = asyncio.Semaphore(
        max(
            1,
            concurrency,
        )
    )


    async with (
        httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
        )
    ) as client:

        async def fetch_one(
            path: str,
        ) -> Tuple[
            str,
            Optional[str],
        ]:

            async with semaphore:
                content = (
                    await get_raw_file_content(
                        owner,
                        repo_name,
                        branch,
                        path,
                        client=client,
                    )
                )

                return (
                    path,
                    content,
                )


        results = await asyncio.gather(
            *[
                fetch_one(
                    path
                )
                for path in paths
            ]
        )


    for (
        path,
        content,
    ) in results:

        if content is not None:
            contents[
                path
            ] = content


    return contents


# =========================================================
# FILE DISCOVERY
# =========================================================

def get_source_files(
    tree: List[dict],
) -> List[str]:

    files = []


    for item in tree:

        if (
            item.get(
                "type"
            )
            != "blob"
        ):
            continue


        path = item.get(
            "path",
            "",
        )


        suffix = (
            PurePosixPath(
                path
            )
            .suffix
            .lower()
        )


        if suffix in (
            SOURCE_EXTENSIONS
        ):
            files.append(
                path
            )


    return sorted(
        files
    )


def get_support_files(
    tree: List[dict],
) -> List[str]:

    files = []


    for item in tree:

        if (
            item.get(
                "type"
            )
            != "blob"
        ):
            continue


        path = item.get(
            "path",
            "",
        )


        file_name = (
            PurePosixPath(
                path
            )
            .name
            .lower()
        )


        if (
            file_name
            in SUPPORT_FILE_NAMES
        ):
            files.append(
                path
            )


    return sorted(
        files
    )


def get_language_from_path(
    path: str,
) -> Optional[str]:

    suffix = (
        PurePosixPath(
            path
        )
        .suffix
        .lower()
    )


    return LANGUAGE_MAP.get(
        suffix
    )


# =========================================================
# LAYER DETECTION
# =========================================================

def get_file_layer(
    path: str,
    content: str = "",
) -> str:

    lower_path = (
        path
        .replace(
            "\\",
            "/",
        )
        .lower()
    )


    parts = [
        part

        for part in
        PurePosixPath(
            lower_path
        ).parts

        if part
    ]


    if any(
        part
        in FRONTEND_PATH_MARKERS

        for part in parts
    ):
        return "frontend"


    if any(
        part
        in BACKEND_PATH_MARKERS

        for part in parts
    ):
        return "backend"


    if any(
        part
        in FRONTEND_STRUCTURE_MARKERS

        for part in parts
    ):
        if not any(
            part
            in BACKEND_STRUCTURE_MARKERS

            for part in parts
        ):
            return "frontend"


    if any(
        part
        in BACKEND_STRUCTURE_MARKERS

        for part in parts
    ):
        return "backend"


    lowered_content = (
        content.lower()
        if content
        else ""
    )


    backend_signals = (
        'from "express"',
        "from 'express'",
        'require("express")',
        "require('express')",
        "from fastapi",
        "import fastapi",
        "apirouter(",
        "flask(",
        "blueprint(",
        "@restcontroller",
        "@controller",
        "httpserver",
        "listen(",
        "prismaclient",
        "sqlalchemy",
    )


    frontend_signals = (
        'from "react"',
        "from 'react'",
        'from "react-dom',
        "from 'react-dom",
        "createRoot(",
        "useState(",
        "useEffect(",
        "window.",
        "document.",
        "import.meta.env",
    )


    backend_score = sum(
        1

        for signal
        in backend_signals

        if signal
        in lowered_content
    )


    frontend_score = sum(
        1

        for signal
        in frontend_signals

        if signal
        in lowered_content
    )


    if (
        backend_score
        > frontend_score
    ):
        return "backend"


    if (
        frontend_score
        > backend_score
    ):
        return "frontend"


    return "shared"


# =========================================================
# NODE TYPE
# =========================================================

def get_node_type(
    path: str,
) -> str:

    lower_path = (
        path
        .replace(
            "\\",
            "/",
        )
        .lower()
    )


    file_name = (
        PurePosixPath(
            path
        )
        .name
        .lower()
    )


    if (
        file_name
        in CONFIG_FILE_NAMES
        or "/config/"
        in lower_path
        or "/configs/"
        in lower_path
        or lower_path.startswith(
            "config/"
        )
        or lower_path.startswith(
            "configs/"
        )
    ):
        return "configuration"


    if (
        "/pages/"
        in lower_path
        or lower_path.startswith(
            "pages/"
        )
        or "/views/"
        in lower_path
        or "/screens/"
        in lower_path
    ):
        return "page"


    if (
        "/components/"
        in lower_path
        or lower_path.startswith(
            "components/"
        )
    ):
        return "component"


    if (
        "/controllers/"
        in lower_path
        or "/controller/"
        in lower_path
        or lower_path.startswith(
            "controllers/"
        )
    ):
        return "controller"


    if (
        "/routes/"
        in lower_path
        or "/route/"
        in lower_path
        or lower_path.startswith(
            "routes/"
        )
        or "/api/"
        in lower_path
    ):
        return "api"


    if (
        "/middleware/"
        in lower_path
        or "/middlewares/"
        in lower_path
        or lower_path.startswith(
            "middleware/"
        )
        or lower_path.startswith(
            "middlewares/"
        )
    ):
        return "middleware"


    if (
        "/models/"
        in lower_path
        or lower_path.startswith(
            "models/"
        )
        or "/schemas/"
        in lower_path
        or "/entities/"
        in lower_path
    ):
        return "model"


    if (
        "/services/"
        in lower_path
        or lower_path.startswith(
            "services/"
        )
        or "/repositories/"
        in lower_path
    ):
        return "service"


    if (
        "/hooks/"
        in lower_path
        or lower_path.startswith(
            "hooks/"
        )
    ):
        return "hook"


    if (
        "/utils/"
        in lower_path
        or "/helpers/"
        in lower_path
        or "/lib/"
        in lower_path
    ):
        return "utility"


    if file_name in {
        "main.jsx",
        "main.tsx",
        "main.js",
        "main.ts",
        "app.jsx",
        "app.tsx",
        "app.js",
        "app.ts",
        "server.js",
        "server.ts",
        "index.js",
        "index.ts",
        "main.py",
        "app.py",
    }:
        return "entry"


    return "source"


# =========================================================
# IMPORT EXTRACTION
# =========================================================

def extract_javascript_imports(
    content: str,
) -> List[str]:

    imports: Set[str] = set()


    for match in re.finditer(
        r'\bfrom\s*["\']([^"\']+)["\']',
        content,
    ):
        imports.add(
            match.group(
                1
            )
        )


    for match in re.finditer(
        r'\bimport\s*["\']([^"\']+)["\']',
        content,
    ):
        imports.add(
            match.group(
                1
            )
        )


    for match in re.finditer(
        (
            r'\brequire\s*\(\s*'
            r'["\']([^"\']+)["\']'
            r'\s*\)'
        ),
        content,
    ):
        imports.add(
            match.group(
                1
            )
        )


    for match in re.finditer(
        (
            r'\bimport\s*\(\s*'
            r'["\']([^"\']+)["\']'
            r'\s*\)'
        ),
        content,
    ):
        imports.add(
            match.group(
                1
            )
        )


    return sorted(
        imports
    )


def extract_python_imports(
    content: str,
) -> List[str]:

    imports: Set[str] = set()


    for line in (
        content.splitlines()
    ):

        import_match = re.match(
            (
                r"^\s*import\s+"
                r"([a-zA-Z0-9_\.]+)"
            ),
            line,
        )


        if import_match:
            imports.add(
                import_match.group(
                    1
                )
            )


        from_match = re.match(
            (
                r"^\s*from\s+"
                r"([a-zA-Z0-9_\.]+)"
                r"\s+import\s+"
            ),
            line,
        )


        if from_match:
            imports.add(
                from_match.group(
                    1
                )
            )


    return sorted(
        imports
    )


def extract_imports(
    path: str,
    content: str,
) -> List[str]:

    suffix = (
        PurePosixPath(
            path
        )
        .suffix
        .lower()
    )


    if suffix in (
        JS_EXTENSIONS
    ):
        return (
            extract_javascript_imports(
                content
            )
        )


    if suffix == ".py":
        return (
            extract_python_imports(
                content
            )
        )


    return []


# =========================================================
# IMPORT BINDINGS
# =========================================================

def extract_js_import_bindings(
    content: str,
) -> Dict[str, dict]:

    result: Dict[
        str,
        dict,
    ] = {}


    import_pattern = re.compile(
        (
            r"\bimport\s+"
            r"(?:type\s+)?"
            r"([\s\S]*?)"
            r"\s+from\s+"
            r'["\']([^"\']+)["\']'
        ),
        re.MULTILINE,
    )


    for match in (
        import_pattern.finditer(
            content
        )
    ):

        specifier = (
            match.group(
                1
            ).strip()
        )


        source = (
            match.group(
                2
            ).strip()
        )


        if not specifier:
            continue


        namespace_match = (
            re.search(
                (
                    r"\*\s+as\s+"
                    r"([A-Za-z_$][\w$]*)"
                ),
                specifier,
            )
        )


        if namespace_match:

            local_name = (
                namespace_match.group(
                    1
                )
            )


            result[
                local_name
            ] = {
                "source":
                    source,

                "imported":
                    "*",
            }


        named_match = re.search(
            r"\{([\s\S]*?)\}",
            specifier,
        )


        if named_match:

            for raw_name in (
                named_match
                .group(
                    1
                )
                .split(",")
            ):

                raw_name = (
                    raw_name.strip()
                )


                if not raw_name:
                    continue


                raw_name = (
                    re.sub(
                        r"^type\s+",
                        "",
                        raw_name,
                    )
                    .strip()
                )


                if (
                    " as "
                    in raw_name
                ):

                    (
                        imported_name,
                        local_name,
                    ) = [
                        value.strip()

                        for value in
                        raw_name.split(
                            " as ",
                            1,
                        )
                    ]

                else:
                    imported_name = (
                        raw_name
                    )

                    local_name = (
                        raw_name
                    )


                if local_name:
                    result[
                        local_name
                    ] = {
                        "source":
                            source,

                        "imported":
                            imported_name,
                    }


        default_part = (
            re.sub(
                r"\{[\s\S]*?\}",
                "",
                specifier,
            )
        )


        default_part = re.sub(
            (
                r"\*\s+as\s+"
                r"[A-Za-z_$][\w$]*"
            ),
            "",
            default_part,
        )


        default_part = (
            default_part
            .strip()
            .strip(",")
            .strip()
        )


        if (
            default_part
            and re.fullmatch(
                r"[A-Za-z_$][\w$]*",
                default_part,
            )
        ):
            result[
                default_part
            ] = {
                "source":
                    source,

                "imported":
                    "default",
            }


    require_pattern = re.compile(
        (
            r"\b(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*=\s*"
            r"require\s*\(\s*"
            r'["\']([^"\']+)["\']'
            r"\s*\)"
        )
    )


    for match in (
        require_pattern.finditer(
            content
        )
    ):
        result[
            match.group(
                1
            )
        ] = {
            "source":
                match.group(
                    2
                ),

            "imported":
                "default",
        }


    return result


def extract_python_import_bindings(
    content: str,
) -> Dict[str, str]:

    bindings: Dict[
        str,
        str,
    ] = {}


    for line in (
        content.splitlines()
    ):

        from_match = re.match(
            (
                r"^\s*from\s+"
                r"([a-zA-Z0-9_\.]+)"
                r"\s+import\s+"
                r"(.+)$"
            ),
            line,
        )


        if from_match:

            module = (
                from_match.group(
                    1
                )
            )


            names = (
                from_match
                .group(
                    2
                )
                .split(
                    "#"
                )[0]
                .strip()
                .strip(
                    "()"
                )
            )


            for raw_name in (
                names.split(
                    ","
                )
            ):

                raw_name = (
                    raw_name.strip()
                )


                if not raw_name:
                    continue


                if (
                    " as "
                    in raw_name
                ):
                    (
                        imported_name,
                        local_name,
                    ) = [
                        value.strip()

                        for value in
                        raw_name.split(
                            " as ",
                            1,
                        )
                    ]

                else:
                    imported_name = (
                        raw_name
                    )

                    local_name = (
                        raw_name
                    )


                bindings[
                    local_name
                ] = (
                    f"{module}."
                    f"{imported_name}"
                )


        import_match = re.match(
            (
                r"^\s*import\s+"
                r"([a-zA-Z0-9_\.]+)"
                r"(?:\s+as\s+"
                r"([a-zA-Z0-9_]+))?"
            ),
            line,
        )


        if import_match:

            module = (
                import_match.group(
                    1
                )
            )


            local_name = (
                import_match.group(
                    2
                )
                or module.split(
                    "."
                )[0]
            )


            bindings[
                local_name
            ] = module


    return bindings


# =========================================================
# PATH RESOLUTION
# =========================================================

def normalize_path(
    path: str,
) -> str:

    parts = []


    for part in (
        PurePosixPath(
            path
        ).parts
    ):

        if part in {
            "",
            ".",
        }:
            continue


        if part == "..":

            if parts:
                parts.pop()

            continue


        parts.append(
            part
        )


    return "/".join(
        parts
    )


def candidate_js_paths(
    base: str,
) -> List[str]:

    possibilities = [
        base
    ]


    path_obj = (
        PurePosixPath(
            base
        )
    )


    suffix = (
        path_obj
        .suffix
        .lower()
    )


    if suffix in {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".mts",
        ".cts",
    }:

        without_suffix = str(
            path_obj.with_suffix(
                ""
            )
        )


        possibilities.extend(
            [
                without_suffix
                + extension

                for extension
                in JS_EXTENSIONS
            ]
        )

    else:
        possibilities.extend(
            [
                base
                + extension

                for extension
                in JS_EXTENSIONS
            ]
        )


    possibilities.extend(
        [
            (
                f"{base}/"
                f"index{extension}"
            )

            for extension
            in JS_EXTENSIONS
        ]
    )


    return list(
        dict.fromkeys(
            possibilities
        )
    )


def resolve_js_relative_import(
    source_path: str,
    imported_path: str,
    source_files: Set[str],
) -> Optional[str]:

    imported_path = (
        imported_path
        .split(
            "?"
        )[0]
        .split(
            "#"
        )[0]
    )


    source_directory = (
        PurePosixPath(
            source_path
        ).parent
    )


    candidate = (
        source_directory
        / imported_path
    )


    base = normalize_path(
        str(
            candidate
        )
    )


    for possibility in (
        candidate_js_paths(
            base
        )
    ):

        if (
            possibility
            in source_files
        ):
            return possibility


    return None


def resolve_js_import(
    source_path: str,
    imported_path: str,
    source_files: Set[str],
) -> Optional[str]:

    if imported_path.startswith(
        "."
    ):
        return (
            resolve_js_relative_import(
                source_path,
                imported_path,
                source_files,
            )
        )


    cleaned = (
        imported_path
        .split(
            "?"
        )[0]
        .split(
            "#"
        )[0]
    )


    alias_candidates = []


    if cleaned.startswith(
        "@/"
    ):
        tail = cleaned[
            2:
        ]

        alias_candidates.extend(
            [
                tail,
                f"src/{tail}",
            ]
        )


    elif cleaned.startswith(
        "~/"
    ):
        tail = cleaned[
            2:
        ]

        alias_candidates.extend(
            [
                tail,
                f"src/{tail}",
            ]
        )


    elif cleaned.startswith(
        "src/"
    ):
        alias_candidates.append(
            cleaned
        )


    elif cleaned.startswith(
        "/"
    ):
        alias_candidates.append(
            cleaned.lstrip(
                "/"
            )
        )


    for base in (
        alias_candidates
    ):

        for possibility in (
            candidate_js_paths(
                normalize_path(
                    base
                )
            )
        ):

            if (
                possibility
                in source_files
            ):
                return possibility


    if alias_candidates:

        tail = (
            alias_candidates[
                -1
            ]
            .removeprefix(
                "src/"
            )
        )


        matches = [
            path

            for path
            in source_files

            if any(
                path.endswith(
                    suffix
                )

                for suffix
                in candidate_js_paths(
                    tail
                )
            )
        ]


        if len(
            matches
        ) == 1:
            return matches[
                0
            ]


    return None


def resolve_python_import(
    source_path: str,
    imported_path: str,
    source_files: Set[str],
) -> Optional[str]:

    if not imported_path:
        return None


    source_directory = (
        PurePosixPath(
            source_path
        ).parent
    )


    leading_dots = (
        len(
            imported_path
        )
        -
        len(
            imported_path.lstrip(
                "."
            )
        )
    )


    module_name = (
        imported_path.lstrip(
            "."
        )
    )


    if leading_dots:

        base_directory = (
            source_directory
        )


        for _ in range(
            max(
                0,
                leading_dots - 1,
            )
        ):
            base_directory = (
                base_directory.parent
            )


        base = normalize_path(
            str(
                base_directory
                /
                module_name.replace(
                    ".",
                    "/",
                )
            )
        )


        possibilities = [
            f"{base}.py",
            (
                f"{base}/"
                "__init__.py"
            ),
        ]

    else:

        module_path = (
            module_name.replace(
                ".",
                "/",
            )
        )


        possibilities = [
            f"{module_path}.py",
            (
                f"{module_path}/"
                "__init__.py"
            ),
        ]


        local_base = normalize_path(
            str(
                source_directory
                /
                module_path
            )
        )


        possibilities.extend(
            [
                f"{local_base}.py",
                (
                    f"{local_base}/"
                    "__init__.py"
                ),
            ]
        )


    for possibility in (
        possibilities
    ):

        if (
            possibility
            in source_files
        ):
            return possibility


    return None


def resolve_python_binding(
    source_path: str,
    module_binding: str,
    source_files: Set[str],
) -> Optional[str]:

    current = (
        module_binding
    )


    while current:

        resolved = (
            resolve_python_import(
                source_path,
                current,
                source_files,
            )
        )


        if resolved:
            return resolved


        if (
            "."
            not in
            current.lstrip(
                "."
            )
        ):
            break


        current = (
            current.rsplit(
                ".",
                1,
            )[0]
        )


    return None


def get_external_package_name(
    imported_path: str,
) -> str:

    imported_path = (
        imported_path.strip()
    )


    if imported_path.startswith(
        "@"
    ):

        parts = (
            imported_path.split(
                "/"
            )
        )


        if len(
            parts
        ) >= 2:
            return (
                f"{parts[0]}/"
                f"{parts[1]}"
            )


    return (
        imported_path
        .split(
            "/"
        )[0]
        .split(
            "."
        )[0]
    )


# =========================================================
# BASIC PARSING UTILITIES
# =========================================================

def find_matching_parenthesis(
    content: str,
    opening_index: int,
) -> Optional[int]:

    depth = 0
    quote_char = None
    escaped = False


    for index in range(
        opening_index,
        len(
            content
        ),
    ):

        char = (
            content[
                index
            ]
        )


        if escaped:
            escaped = False
            continue


        if char == "\\":
            escaped = True
            continue


        if quote_char:

            if (
                char
                == quote_char
            ):
                quote_char = None

            continue


        if char in {
            "'",
            '"',
            "`",
        }:
            quote_char = char
            continue


        if char == "(":
            depth += 1


        elif char == ")":
            depth -= 1

            if depth == 0:
                return index


    return None


def split_top_level_arguments(
    text: str,
) -> List[str]:

    arguments = []
    current = []

    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0

    quote_char = None
    escaped = False


    for char in text:

        if escaped:

            current.append(
                char
            )

            escaped = False

            continue


        if char == "\\":

            current.append(
                char
            )

            escaped = True

            continue


        if quote_char:

            current.append(
                char
            )


            if (
                char
                == quote_char
            ):
                quote_char = None


            continue


        if char in {
            "'",
            '"',
            "`",
        }:

            quote_char = (
                char
            )

            current.append(
                char
            )

            continue


        if char == "(":
            paren_depth += 1


        elif char == ")":
            paren_depth -= 1


        elif char == "[":
            bracket_depth += 1


        elif char == "]":
            bracket_depth -= 1


        elif char == "{":
            brace_depth += 1


        elif char == "}":
            brace_depth -= 1


        if (
            char == ","
            and paren_depth == 0
            and bracket_depth == 0
            and brace_depth == 0
        ):
            arguments.append(
                "".join(
                    current
                ).strip()
            )

            current = []

            continue


        current.append(
            char
        )


    final_value = (
        "".join(
            current
        ).strip()
    )


    if final_value:
        arguments.append(
            final_value
        )


    return arguments


# =========================================================
# STRING / URL EXPRESSION RESOLUTION
# =========================================================

def extract_string_constants(
    content: str,
) -> Dict[str, str]:

    constants: Dict[
        str,
        str,
    ] = {}


    pattern = re.compile(
        (
            r"\b(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)"
            r"(?:\s*:\s*[^=;]+)?"
            r"\s*=\s*"
            r"([^;]+);"
        ),
        re.MULTILINE,
    )


    for _ in range(
        3
    ):

        changed = False


        for match in (
            pattern.finditer(
                content
            )
        ):

            name = (
                match.group(
                    1
                )
            )


            expression = (
                match.group(
                    2
                ).strip()
            )


            value = (
                parse_string_expression(
                    expression,
                    constants,
                )
            )


            if (
                value is not None
                and constants.get(
                    name
                )
                != value
            ):

                constants[
                    name
                ] = value

                changed = True


        if not changed:
            break


    return constants


def replace_template_expressions(
    value: str,
    constants: Dict[
        str,
        str,
    ],
) -> str:

    def replace(
        match: re.Match,
    ) -> str:

        expression = (
            match.group(
                1
            ).strip()
        )


        if (
            expression
            in constants
        ):
            return (
                constants[
                    expression
                ]
                .rstrip(
                    "/"
                )
            )


        upper_expression = (
            expression.upper()
        )


        if any(
            word
            in upper_expression

            for word
            in URLISH_WORDS
        ):
            return ""


        if (
            "IMPORT.META.ENV"
            in upper_expression
            or "PROCESS.ENV"
            in upper_expression
        ):
            return ""


        return "{param}"


    return re.sub(
        r"\$\{([^}]+)\}",
        replace,
        value,
    )


def parse_string_expression(
    expression: str,
    constants: Optional[
        Dict[str, str]
    ] = None,
) -> Optional[str]:

    constants = (
        constants
        or {}
    )


    expression = (
        expression.strip()
    )


    while (
        len(
            expression
        ) >= 2
        and expression[
            0
        ] == "("
        and expression[
            -1
        ] == ")"
    ):
        expression = (
            expression[
                1:-1
            ].strip()
        )


    if (
        expression
        in constants
    ):
        return constants[
            expression
        ]


    literal_match = (
        re.fullmatch(
            (
                r'(["\'])'
                r"([\s\S]*?)"
                r"\1"
            ),
            expression,
        )
    )


    if literal_match:
        return (
            literal_match.group(
                2
            )
        )


    template_match = (
        re.fullmatch(
            r"`([\s\S]*?)`",
            expression,
        )
    )


    if template_match:
        return (
            replace_template_expressions(
                template_match.group(
                    1
                ),
                constants,
            )
        )


    fallback_parts = re.split(
        r"\?\?|\|\|",
        expression,
    )


    if len(
        fallback_parts
    ) > 1:

        for part in reversed(
            fallback_parts
        ):

            parsed = (
                parse_string_expression(
                    part,
                    constants,
                )
            )


            if parsed:
                return parsed


    concat_parts = re.split(
        r"\s*\+\s*",
        expression,
    )


    if len(
        concat_parts
    ) > 1:

        output = []


        for part in (
            concat_parts
        ):

            parsed = (
                parse_string_expression(
                    part,
                    constants,
                )
            )


            if parsed is not None:
                output.append(
                    parsed
                )

            else:
                upper_part = (
                    part.upper()
                )


                if any(
                    word
                    in upper_part

                    for word
                    in URLISH_WORDS
                ):
                    continue


                output.append(
                    "{param}"
                )


        if output:
            return "".join(
                output
            )


    quoted_values = re.findall(
        r'["\']([^"\']+)["\']',
        expression,
    )


    for value in reversed(
        quoted_values
    ):

        if (
            value.startswith(
                "http://"
            )
            or value.startswith(
                "https://"
            )
            or value.startswith(
                "/"
            )
        ):
            return value


    return None


def extract_object_property(
    text: str,
    property_name: str,
) -> Optional[str]:

    pattern = re.compile(
        (
            rf"\b{re.escape(property_name)}"
            r"\s*:\s*"
            r"([^,\n}]+)"
        ),
        re.IGNORECASE,
    )


    match = pattern.search(
        text
    )


    if not match:
        return None


    return (
        match.group(
            1
        ).strip()
    )


# =========================================================
# HTTP CLIENT DETECTION
# =========================================================

def extract_http_client_definitions(
    path: str,
    content: str,
) -> List[dict]:

    definitions = []


    constants = (
        extract_string_constants(
            content
        )
    )


    pattern = re.compile(
        (
            r"(?:export\s+)?"
            r"(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)"
            r"(?:\s*:\s*[^=;]+)?"
            r"\s*=\s*"
            r"(axios|ky|wretch)"
            r"\.create\s*\("
        ),
        re.IGNORECASE,
    )


    for match in (
        pattern.finditer(
            content
        )
    ):

        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            content[
                opening_index + 1:
                closing_index
            ]
        )


        base_expression = (
            extract_object_property(
                arguments,
                "baseURL",
            )
            or
            extract_object_property(
                arguments,
                "prefixUrl",
            )
            or
            extract_object_property(
                arguments,
                "prefixURL",
            )
        )


        base_url = None


        if base_expression:

            base_url = (
                parse_string_expression(
                    base_expression,
                    constants,
                )
            )


        definitions.append(
            {
                "file":
                    path,

                "variable":
                    match.group(
                        1
                    ),

                "library":
                    match.group(
                        2
                    ).lower(),

                "base_url":
                    base_url,
            }
        )


    return definitions


def get_http_client_base_url(
    path: str,
    receiver: str,
    content: str,
    source_files: Set[str],
    client_definitions:
        Dict[
            str,
            List[dict],
        ],
) -> Optional[str]:

    root_receiver = (
        receiver.split(
            "."
        )[0]
    )


    for definition in (
        client_definitions.get(
            path,
            [],
        )
    ):

        if (
            definition[
                "variable"
            ]
            == root_receiver
        ):
            return (
                definition.get(
                    "base_url"
                )
            )


    bindings = (
        extract_js_import_bindings(
            content
        )
    )


    binding = bindings.get(
        root_receiver
    )


    if binding:

        resolved_file = (
            resolve_js_import(
                path,
                binding[
                    "source"
                ],
                source_files,
            )
        )


        if resolved_file:

            definitions = (
                client_definitions.get(
                    resolved_file,
                    [],
                )
            )


            imported_name = (
                binding.get(
                    "imported"
                )
            )


            for definition in (
                definitions
            ):

                if (
                    imported_name
                    not in {
                        None,
                        "default",
                        "*",
                    }
                    and definition[
                        "variable"
                    ]
                    != imported_name
                ):
                    continue


                return (
                    definition.get(
                        "base_url"
                    )
                )


            if (
                imported_name
                in {
                    "default",
                    "*",
                }
                and len(
                    definitions
                ) == 1
            ):
                return (
                    definitions[
                        0
                    ].get(
                        "base_url"
                    )
                )


    return None


def receiver_looks_like_http_client(
    receiver: str,
    path: str,
    content: str,
    source_files: Set[str],
    client_definitions:
        Dict[
            str,
            List[dict],
        ],
) -> bool:

    root = (
        receiver.split(
            "."
        )[0]
    )


    lowered = (
        root.lower()
    )


    if lowered in {
        "axios",
        "api",
        "client",
        "http",
        "httpclient",
        "apiclient",
        "request",
        "requests",
    }:
        return True


    if (
        get_http_client_base_url(
            path,
            receiver,
            content,
            source_files,
            client_definitions,
        )
        is not None
    ):
        return True


    bindings = (
        extract_js_import_bindings(
            content
        )
    )


    binding = (
        bindings.get(
            root
        )
    )


    if binding:

        source = (
            binding[
                "source"
            ].lower()
        )


        if any(
            marker
            in source

            for marker
            in {
                "api",
                "http",
                "client",
                "request",
                "axios",
            }
        ):
            return True


    return False


def combine_base_and_endpoint(
    base_url:
        Optional[str],
    endpoint: str,
) -> str:

    endpoint = (
        endpoint.strip()
    )


    if is_external_url(
        endpoint
    ):
        return endpoint


    if not base_url:
        return endpoint


    base_url = (
        base_url.strip()
    )


    if not base_url:
        return endpoint


    if is_external_url(
        base_url
    ):
        return (
            base_url.rstrip(
                "/"
            )
            +
            "/"
            +
            endpoint.lstrip(
                "/"
            )
        )


    return join_route_prefix(
        base_url,
        endpoint,
    )


def extract_fetch_method(
    second_argument: str,
) -> str:

    method_match = re.search(
        (
            r"\bmethod\s*:\s*"
            r'["\']'
            r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)"
            r'["\']'
        ),
        second_argument,
        re.IGNORECASE,
    )


    if not method_match:
        return "GET"


    return (
        method_match
        .group(
            1
        )
        .upper()
    )


def extract_request_object(
    object_text: str,
    constants:
        Dict[str, str],
) -> Optional[
    Tuple[
        str,
        str,
    ]
]:

    method_expression = (
        extract_object_property(
            object_text,
            "method",
        )
    )


    url_expression = (
        extract_object_property(
            object_text,
            "url",
        )
        or
        extract_object_property(
            object_text,
            "uri",
        )
        or
        extract_object_property(
            object_text,
            "endpoint",
        )
    )


    if not url_expression:
        return None


    endpoint = (
        parse_string_expression(
            url_expression,
            constants,
        )
    )


    if not endpoint:
        return None


    method = "GET"


    if method_expression:

        parsed_method = (
            parse_string_expression(
                method_expression,
                constants,
            )
        )


        if parsed_method:
            method = (
                parsed_method.upper()
            )


    if method not in {
        value.upper()

        for value
        in HTTP_METHODS
    }:
        method = "GET"


    return (
        method,
        endpoint,
    )


# =========================================================
# HTTP REQUEST EXTRACTION
# =========================================================

def extract_http_requests(
    path: str,
    content: str,
    source_files:
        Optional[
            Set[str]
        ] = None,
    client_definitions:
        Optional[
            Dict[
                str,
                List[dict],
            ]
        ] = None,
) -> List[dict]:

    source_files = (
        source_files
        or set()
    )


    client_definitions = (
        client_definitions
        or {}
    )


    requests = []


    constants = (
        extract_string_constants(
            content
        )
    )


    member_pattern = re.compile(
        (
            r"\b"
            r"([A-Za-z_$][\w$]*"
            r"(?:\.[A-Za-z_$][\w$]*)*)"
            r"\s*\.\s*"
            r"(get|post|put|patch|delete|head|options)"
            r"(?:\s*<[^;(){}]+>)?"
            r"\s*\("
        ),
        re.IGNORECASE,
    )


    for match in (
        member_pattern.finditer(
            content
        )
    ):

        receiver = (
            match.group(
                1
            )
        )


        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if not arguments:
            continue


        endpoint = (
            parse_string_expression(
                arguments[
                    0
                ],
                constants,
            )
        )


        if not endpoint:
            continue


        if (
            not endpoint.startswith(
                "/"
            )
            and not is_external_url(
                endpoint
            )
            and "{param}"
            not in endpoint
            and not (
                receiver_looks_like_http_client(
                    receiver,
                    path,
                    content,
                    source_files,
                    client_definitions,
                )
            )
        ):
            continue


        if (
            receiver.lower()
            in {
                "localstorage",
                "sessionstorage",
            }
        ):
            continue


        base_url = (
            get_http_client_base_url(
                path,
                receiver,
                content,
                source_files,
                client_definitions,
            )
        )


        full_endpoint = (
            combine_base_and_endpoint(
                base_url,
                endpoint,
            )
        )


        requests.append(
            {
                "file":
                    path,

                "method":
                    match.group(
                        2
                    ).upper(),

                "endpoint":
                    full_endpoint,

                "client":
                    receiver,
            }
        )


    fetch_pattern = re.compile(
        r"\bfetch\s*\(",
        re.IGNORECASE,
    )


    for match in (
        fetch_pattern.finditer(
            content
        )
    ):

        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if not arguments:
            continue


        endpoint = (
            parse_string_expression(
                arguments[
                    0
                ],
                constants,
            )
        )


        if not endpoint:
            continue


        method = "GET"


        if len(
            arguments
        ) > 1:

            method = (
                extract_fetch_method(
                    arguments[
                        1
                    ]
                )
            )


        requests.append(
            {
                "file":
                    path,

                "method":
                    method,

                "endpoint":
                    endpoint,

                "client":
                    "fetch",
            }
        )


    request_pattern = re.compile(
        (
            r"\b"
            r"([A-Za-z_$][\w$]*)"
            r"(?:\.request)?"
            r"\s*\(\s*\{"
        ),
        re.IGNORECASE,
    )


    for match in (
        request_pattern.finditer(
            content
        )
    ):

        receiver = (
            match.group(
                1
            )
        )


        if not (
            receiver_looks_like_http_client(
                receiver,
                path,
                content,
                source_files,
                client_definitions,
            )
            or receiver.lower()
            in {
                "axios",
                "request",
            }
        ):
            continue


        opening_index = (
            content.find(
                "(",
                match.start(),
            )
        )


        if (
            opening_index
            < 0
        ):
            continue


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if not arguments:
            continue


        request_data = (
            extract_request_object(
                arguments[
                    0
                ],
                constants,
            )
        )


        if not request_data:
            continue


        (
            method,
            endpoint,
        ) = request_data


        base_url = (
            get_http_client_base_url(
                path,
                receiver,
                content,
                source_files,
                client_definitions,
            )
        )


        requests.append(
            {
                "file":
                    path,

                "method":
                    method,

                "endpoint":
                    combine_base_and_endpoint(
                        base_url,
                        endpoint,
                    ),

                "client":
                    receiver,
            }
        )


    return deduplicate_dicts(
        requests,
        keys=(
            "file",
            "method",
            "endpoint",
        ),
    )


# =========================================================
# ENDPOINT HELPERS
# =========================================================

def is_external_url(
    endpoint: str,
) -> bool:

    return bool(
        re.match(
            r"^https?://",
            endpoint.strip(),
            re.IGNORECASE,
        )
    )


def is_local_url(
    endpoint: str,
) -> bool:

    if not is_external_url(
        endpoint
    ):
        return False


    try:
        host = (
            urlparse(
                endpoint
            ).hostname
            or ""
        ).lower()

    except ValueError:
        return False


    return (
        host in {
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
        }
        or host.endswith(
            ".localhost"
        )
    )


def get_external_service_name(
    endpoint: str,
) -> str:

    if endpoint.startswith(
        "sdk://"
    ):

        provider = (
            endpoint[
                len(
                    "sdk://"
                ):
            ]
            .strip(
                "/"
            )
        )


        if provider:
            return (
                provider
                .replace(
                    "-",
                    " ",
                )
                .title()
                +
                " API"
            )


    try:
        host = (
            urlparse(
                endpoint
            ).netloc
        )

    except ValueError:
        return "External API"


    host = (
        host
        .lower()
        .replace(
            "www.",
            "",
        )
    )


    service_map = (
        (
            "api.groq.com",
            "Groq API",
        ),
        (
            "groq.com",
            "Groq API",
        ),
        (
            "generativelanguage.googleapis.com",
            "Google Gemini API",
        ),
        (
            "googleapis.com",
            "Google API",
        ),
        (
            "api.openai.com",
            "OpenAI API",
        ),
        (
            "openai.com",
            "OpenAI API",
        ),
        (
            "api.anthropic.com",
            "Anthropic API",
        ),
        (
            "anthropic.com",
            "Anthropic API",
        ),
        (
            "api.mistral.ai",
            "Mistral API",
        ),
        (
            "cohere.ai",
            "Cohere API",
        ),
        (
            "huggingface.co",
            "Hugging Face API",
        ),
        (
            "clipdrop",
            "Clipdrop API",
        ),
        (
            "cloudinary.com",
            "Cloudinary",
        ),
        (
            "api.github.com",
            "GitHub API",
        ),
        (
            "githubusercontent.com",
            "GitHub Raw Content",
        ),
        (
            "api.stripe.com",
            "Stripe API",
        ),
    )


    for (
        marker,
        name,
    ) in service_map:

        if marker in host:
            return name


    if host:
        return host


    return "External API"


def normalize_endpoint(
    endpoint: str,
) -> str:

    endpoint = (
        endpoint
        .strip()
        .strip(
            "\"'"
        )
    )


    if not endpoint:
        return "/"


    if is_external_url(
        endpoint
    ):

        try:
            parsed = (
                urlparse(
                    endpoint
                )
            )


            endpoint = (
                parsed.path
                or "/"
            )


            if parsed.query:
                endpoint += (
                    "?"
                    +
                    parsed.query
                )

        except ValueError:
            pass


    endpoint = re.sub(
        r"^\$\{[^}]+\}",
        "",
        endpoint,
    )


    endpoint = (
        endpoint
        .split(
            "?"
        )[0]
        .split(
            "#"
        )[0]
    )


    endpoint = re.sub(
        r"\$\{[^}]+\}",
        "{param}",
        endpoint,
    )


    endpoint = re.sub(
        r"/+",
        "/",
        endpoint,
    )


    if not endpoint:
        return "/"


    if not endpoint.startswith(
        "/"
    ):
        endpoint = (
            "/"
            +
            endpoint
        )


    if endpoint != "/":
        endpoint = (
            endpoint.rstrip(
                "/"
            )
        )


    return endpoint


def join_route_prefix(
    prefix: str,
    route: str,
) -> str:

    prefix = (
        normalize_endpoint(
            prefix
        )
    )


    route = (
        normalize_endpoint(
            route
        )
    )


    if prefix == "/":
        return route


    if route == "/":
        return prefix


    return (
        prefix.rstrip(
            "/"
        )
        +
        "/"
        +
        route.lstrip(
            "/"
        )
    )


def route_to_regex(
    endpoint: str,
) -> str:

    endpoint = (
        normalize_endpoint(
            endpoint
        )
    )


    segments = (
        endpoint
        .strip(
            "/"
        )
        .split(
            "/"
        )
        if endpoint != "/"
        else []
    )


    regex_segments = []


    for segment in (
        segments
    ):

        if (
            re.fullmatch(
                r"\{[^/]+\}",
                segment,
            )
            or
            re.fullmatch(
                (
                    r":"
                    r"[A-Za-z_$]"
                    r"[\w$]*"
                ),
                segment,
            )
        ):
            regex_segments.append(
                r"[^/]+"
            )

        else:
            escaped = (
                re.escape(
                    segment
                )
            )


            escaped = re.sub(
                r"\\\{[^}]+\\\}",
                r"[^/]+",
                escaped,
            )


            regex_segments.append(
                escaped
            )


    if not regex_segments:
        return "/"


    return (
        "/"
        +
        "/".join(
            regex_segments
        )
    )


def routes_match(
    frontend_endpoint: str,
    backend_endpoint: str,
) -> bool:

    frontend = (
        normalize_endpoint(
            frontend_endpoint
        )
    )


    backend_regex = (
        route_to_regex(
            backend_endpoint
        )
    )


    if re.fullmatch(
        backend_regex,
        frontend,
    ):
        return True


    frontend_without_api = (
        re.sub(
            r"^/api(?=/|$)",
            "",
            frontend,
        )
        or "/"
    )


    backend = (
        normalize_endpoint(
            backend_endpoint
        )
    )


    backend_without_api = (
        re.sub(
            r"^/api(?=/|$)",
            "",
            backend,
        )
        or "/"
    )


    return bool(
        re.fullmatch(
            route_to_regex(
                backend_without_api
            ),
            frontend_without_api,
        )
    )


# =========================================================
# EXPRESS ANALYSIS
# =========================================================

def get_express_router_variables(
    content: str,
) -> Set[str]:

    variables = {
        "app",
        "router",
    }


    patterns = [
        (
            r"(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*=\s*"
            r"express\.Router\s*\("
        ),
        (
            r"(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*=\s*"
            r"Router\s*\("
        ),
        (
            r"(?:const|let|var)\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*=\s*"
            r"express\s*\("
        ),
    ]


    for pattern in patterns:

        for match in (
            re.finditer(
                pattern,
                content,
            )
        ):
            variables.add(
                match.group(
                    1
                )
            )


    return variables


def clean_route_path_argument(
    argument: str,
    constants:
        Optional[
            Dict[str, str]
        ] = None,
) -> Optional[str]:

    value = (
        parse_string_expression(
            argument,
            constants
            or {},
        )
    )


    if value is None:
        return None


    if is_external_url(
        value
    ):
        return normalize_endpoint(
            value
        )


    return normalize_endpoint(
        value
    )


def get_handler_identifier(
    expression: str,
) -> Optional[str]:

    expression = (
        expression.strip()
    )


    direct_match = (
        re.fullmatch(
            (
                r"([A-Za-z_$]"
                r"[\w$]*)"
            ),
            expression,
        )
    )


    if direct_match:
        return direct_match.group(
            1
        )


    member_match = (
        re.fullmatch(
            (
                r"([A-Za-z_$][\w$]*"
                r"(?:\.[A-Za-z_$][\w$]*)+)"
            ),
            expression,
        )
    )


    if member_match:
        return member_match.group(
            1
        )


    return None


def resolve_js_handler_file(
    path: str,
    handler: Optional[str],
    content: str,
    source_files: Set[str],
) -> Optional[str]:

    if not handler:
        return None


    root_identifier = (
        handler.split(
            "."
        )[0]
    )


    bindings = (
        extract_js_import_bindings(
            content
        )
    )


    binding = bindings.get(
        root_identifier
    )


    if binding:

        resolved = (
            resolve_js_import(
                path,
                binding[
                    "source"
                ],
                source_files,
            )
        )


        if resolved:
            return resolved


    function_pattern = re.compile(
        (
            r"\b(?:"
            rf"function\s+{re.escape(root_identifier)}\s*\("
            r"|"
            r"(?:const|let|var)\s+"
            rf"{re.escape(root_identifier)}\s*="
            r")"
        )
    )


    if function_pattern.search(
        content
    ):
        return path


    return None


def extract_express_routes(
    path: str,
    content: str,
    source_files: Set[str],
) -> List[dict]:

    routes = []


    if (
        get_file_layer(
            path,
            content,
        )
        != "backend"
    ):
        return routes


    router_variables = (
        get_express_router_variables(
            content
        )
    )


    constants = (
        extract_string_constants(
            content
        )
    )


    for router_variable in (
        router_variables
    ):

        for method in (
            HTTP_METHODS
        ):

            pattern = re.compile(
                (
                    rf"\b{re.escape(router_variable)}"
                    rf"\.{method}"
                    r"\s*\("
                ),
                re.IGNORECASE,
            )


            for match in (
                pattern.finditer(
                    content
                )
            ):

                opening_index = (
                    match.end()
                    - 1
                )


                closing_index = (
                    find_matching_parenthesis(
                        content,
                        opening_index,
                    )
                )


                if (
                    closing_index
                    is None
                ):
                    continue


                arguments = (
                    split_top_level_arguments(
                        content[
                            opening_index + 1:
                            closing_index
                        ]
                    )
                )


                if not arguments:
                    continue


                endpoint = (
                    clean_route_path_argument(
                        arguments[
                            0
                        ],
                        constants,
                    )
                )


                if endpoint is None:
                    continue


                handler = None
                controller_file = None


                for expression in reversed(
                    arguments[
                        1:
                    ]
                ):

                    candidate = (
                        get_handler_identifier(
                            expression
                        )
                    )


                    if not candidate:
                        continue


                    handler = (
                        candidate
                    )


                    controller_file = (
                        resolve_js_handler_file(
                            path,
                            candidate,
                            content,
                            source_files,
                        )
                    )


                    if controller_file:
                        break


                if (
                    controller_file
                    is None
                    and any(
                        (
                            "=>"
                            in expression
                            or "function"
                            in expression
                        )

                        for expression
                        in arguments[
                            1:
                        ]
                    )
                ):
                    controller_file = (
                        path
                    )


                routes.append(
                    {
                        "file":
                            path,

                        "method":
                            method.upper(),

                        "endpoint":
                            endpoint,

                        "framework":
                            "Express",

                        "handler":
                            handler,

                        "controller_file":
                            controller_file,
                    }
                )


    route_chain_pattern = re.compile(
        (
            r"\b"
            r"([A-Za-z_$][\w$]*)"
            r"\.route\s*\("
        ),
        re.IGNORECASE,
    )


    for match in (
        route_chain_pattern.finditer(
            content
        )
    ):

        router_variable = (
            match.group(
                1
            )
        )


        if (
            router_variable
            not in router_variables
        ):
            continue


        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        route_arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if not route_arguments:
            continue


        endpoint = (
            clean_route_path_argument(
                route_arguments[
                    0
                ],
                constants,
            )
        )


        if endpoint is None:
            continue


        tail = (
            content[
                closing_index + 1:
                closing_index + 1200
            ]
        )


        chain_pattern = re.compile(
            (
                r"\."
                r"(get|post|put|patch|delete|head|options)"
                r"\s*\("
            ),
            re.IGNORECASE,
        )


        for chain_match in (
            chain_pattern.finditer(
                tail
            )
        ):

            chain_open = (
                closing_index
                + 1
                + chain_match.end()
                - 1
            )


            chain_close = (
                find_matching_parenthesis(
                    content,
                    chain_open,
                )
            )


            if (
                chain_close
                is None
            ):
                continue


            arguments = (
                split_top_level_arguments(
                    content[
                        chain_open + 1:
                        chain_close
                    ]
                )
            )


            handler = None
            controller_file = None


            for expression in reversed(
                arguments
            ):

                candidate = (
                    get_handler_identifier(
                        expression
                    )
                )


                if not candidate:
                    continue


                handler = (
                    candidate
                )


                controller_file = (
                    resolve_js_handler_file(
                        path,
                        candidate,
                        content,
                        source_files,
                    )
                )


                if controller_file:
                    break


            routes.append(
                {
                    "file":
                        path,

                    "method":
                        chain_match
                        .group(
                            1
                        )
                        .upper(),

                    "endpoint":
                        endpoint,

                    "framework":
                        "Express",

                    "handler":
                        handler,

                    "controller_file":
                        controller_file,
                }
            )


    return deduplicate_dicts(
        routes,
        keys=(
            "file",
            "method",
            "endpoint",
            "handler",
        ),
    )


def extract_express_mounts(
    path: str,
    content: str,
    source_files: Set[str],
) -> List[dict]:

    mounts = []


    if (
        get_file_layer(
            path,
            content,
        )
        != "backend"
    ):
        return mounts


    bindings = (
        extract_js_import_bindings(
            content
        )
    )


    constants = (
        extract_string_constants(
            content
        )
    )


    router_variables = (
        get_express_router_variables(
            content
        )
    )


    pattern = re.compile(
        (
            r"\b"
            r"([A-Za-z_$][\w$]*)"
            r"\.use\s*\("
        ),
        re.IGNORECASE,
    )


    for match in (
        pattern.finditer(
            content
        )
    ):

        mounting_router = (
            match.group(
                1
            )
        )


        if (
            mounting_router
            not in router_variables
        ):
            continue


        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if len(
            arguments
        ) < 2:
            continue


        prefix = (
            clean_route_path_argument(
                arguments[
                    0
                ],
                constants,
            )
        )


        if prefix is None:
            continue


        target_expression = (
            arguments[
                -1
            ].strip()
        )


        target_identifier = (
            get_handler_identifier(
                target_expression
            )
        )


        if not target_identifier:
            continue


        root_identifier = (
            target_identifier
            .split(
                "."
            )[0]
        )


        binding = (
            bindings.get(
                root_identifier
            )
        )


        if not binding:
            continue


        resolved = (
            resolve_js_import(
                path,
                binding[
                    "source"
                ],
                source_files,
            )
        )


        if not resolved:
            continue


        mounts.append(
            {
                "mount_file":
                    path,

                "mounting_router":
                    mounting_router,

                "prefix":
                    prefix,

                "router_file":
                    resolved,
            }
        )


    return mounts


# =========================================================
# ROUTER PREFIX APPLICATION
# =========================================================

def apply_mount_prefixes(
    routes: List[dict],
    mounts: List[dict],
    framework: str,
) -> List[dict]:

    if not mounts:
        return routes


    target_files = {
        mount[
            "router_file"
        ]

        for mount
        in mounts
    }


    root_files = {
        mount[
            "mount_file"
        ]

        for mount
        in mounts

        if (
            mount[
                "mount_file"
            ]
            not in target_files
        )
    }


    prefixes: Dict[
        str,
        Set[str],
    ] = {
        root_file: {
            "/"
        }

        for root_file
        in root_files
    }


    changed = True
    iterations = 0


    while (
        changed
        and iterations < 20
    ):

        changed = False
        iterations += 1


        for mount in mounts:

            parent_prefixes = (
                prefixes.get(
                    mount[
                        "mount_file"
                    ],
                    set(),
                )
            )


            if not parent_prefixes:

                if (
                    mount[
                        "mount_file"
                    ]
                    not in target_files
                ):
                    parent_prefixes = {
                        "/"
                    }

                else:
                    continue


            for parent_prefix in (
                parent_prefixes
            ):

                combined = (
                    join_route_prefix(
                        parent_prefix,
                        mount[
                            "prefix"
                        ],
                    )
                )


                target_prefixes = (
                    prefixes.setdefault(
                        mount[
                            "router_file"
                        ],
                        set(),
                    )
                )


                if (
                    combined
                    not in target_prefixes
                ):

                    target_prefixes.add(
                        combined
                    )

                    changed = True


    result = []


    for route in routes:

        if (
            route.get(
                "framework"
            )
            != framework
        ):
            result.append(
                route
            )

            continue


        route_prefixes = (
            prefixes.get(
                route[
                    "file"
                ]
            )
        )


        if not route_prefixes:

            result.append(
                route
            )

            continue


        for prefix in sorted(
            route_prefixes
        ):

            updated = (
                route.copy()
            )


            updated[
                "endpoint"
            ] = join_route_prefix(
                prefix,
                route[
                    "endpoint"
                ],
            )


            result.append(
                updated
            )


    return deduplicate_dicts(
        result,
        keys=(
            "file",
            "method",
            "endpoint",
            "handler",
        ),
    )


# =========================================================
# FASTAPI ANALYSIS
# =========================================================

def extract_fastapi_router_prefixes(
    content: str,
) -> Dict[str, str]:

    prefixes = {}


    pattern = re.compile(
        (
            r"\b"
            r"([A-Za-z_][\w]*)"
            r"\s*=\s*"
            r"APIRouter\s*\("
        )
    )


    constants = (
        extract_string_constants(
            content
        )
    )


    for match in (
        pattern.finditer(
            content
        )
    ):

        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            content[
                opening_index + 1:
                closing_index
            ]
        )


        prefix_match = (
            re.search(
                (
                    r"\bprefix\s*=\s*"
                    r"([^,\n)]+)"
                ),
                arguments,
            )
        )


        prefix_expression = (
            prefix_match.group(
                1
            )
            if prefix_match
            else None
        )


        prefix = "/"


        if prefix_expression:

            parsed = (
                parse_string_expression(
                    prefix_expression,
                    constants,
                )
            )


            if parsed:
                prefix = (
                    normalize_endpoint(
                        parsed
                    )
                )


        prefixes[
            match.group(
                1
            )
        ] = prefix


    prefixes.setdefault(
        "app",
        "/",
    )


    prefixes.setdefault(
        "router",
        prefixes.get(
            "router",
            "/",
        ),
    )


    return prefixes


def extract_fastapi_routes(
    path: str,
    content: str,
) -> List[dict]:

    routes = []


    if (
        get_file_layer(
            path,
            content,
        )
        != "backend"
    ):
        return routes


    router_prefixes = (
        extract_fastapi_router_prefixes(
            content
        )
    )


    constants = (
        extract_string_constants(
            content
        )
    )


    pattern = re.compile(
        (
            r"@\s*"
            r"([A-Za-z_][\w]*)"
            r"\."
            r"(get|post|put|patch|delete|head|options)"
            r"\s*\("
        ),
        re.IGNORECASE,
    )


    for match in (
        pattern.finditer(
            content
        )
    ):

        router_variable = (
            match.group(
                1
            )
        )


        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if not arguments:
            continue


        endpoint = (
            clean_route_path_argument(
                arguments[
                    0
                ],
                constants,
            )
        )


        if endpoint is None:
            continue


        local_prefix = (
            router_prefixes.get(
                router_variable,
                "/",
            )
        )


        endpoint = (
            join_route_prefix(
                local_prefix,
                endpoint,
            )
        )


        following = (
            content[
                closing_index + 1:
                closing_index + 600
            ]
        )


        handler_match = (
            re.search(
                (
                    r"(?:async\s+)?"
                    r"def\s+"
                    r"([A-Za-z_][\w]*)"
                ),
                following,
            )
        )


        handler = (
            handler_match.group(
                1
            )
            if handler_match
            else None
        )


        routes.append(
            {
                "file":
                    path,

                "method":
                    match.group(
                        2
                    ).upper(),

                "endpoint":
                    endpoint,

                "framework":
                    "FastAPI",

                "handler":
                    handler,

                "controller_file":
                    path,
            }
        )


    api_route_pattern = re.compile(
        (
            r"@\s*"
            r"([A-Za-z_][\w]*)"
            r"\.api_route\s*\("
        ),
        re.IGNORECASE,
    )


    for match in (
        api_route_pattern.finditer(
            content
        )
    ):

        router_variable = (
            match.group(
                1
            )
        )


        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments_text = (
            content[
                opening_index + 1:
                closing_index
            ]
        )


        arguments = (
            split_top_level_arguments(
                arguments_text
            )
        )


        if not arguments:
            continue


        endpoint = (
            clean_route_path_argument(
                arguments[
                    0
                ],
                constants,
            )
        )


        if endpoint is None:
            continue


        method_values = re.findall(
            (
                r'["\']'
                r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)"
                r'["\']'
            ),
            arguments_text,
            re.IGNORECASE,
        )


        if not method_values:
            method_values = [
                "GET"
            ]


        endpoint = (
            join_route_prefix(
                router_prefixes.get(
                    router_variable,
                    "/",
                ),
                endpoint,
            )
        )


        following = (
            content[
                closing_index + 1:
                closing_index + 600
            ]
        )


        handler_match = re.search(
            (
                r"(?:async\s+)?"
                r"def\s+"
                r"([A-Za-z_][\w]*)"
            ),
            following,
        )


        handler = (
            handler_match.group(
                1
            )
            if handler_match
            else None
        )


        for method in (
            method_values
        ):

            routes.append(
                {
                    "file":
                        path,

                    "method":
                        method.upper(),

                    "endpoint":
                        endpoint,

                    "framework":
                        "FastAPI",

                    "handler":
                        handler,

                    "controller_file":
                        path,
                }
            )


    return deduplicate_dicts(
        routes,
        keys=(
            "file",
            "method",
            "endpoint",
            "handler",
        ),
    )


def extract_fastapi_mounts(
    path: str,
    content: str,
    source_files: Set[str],
) -> List[dict]:

    mounts = []


    if (
        get_file_layer(
            path,
            content,
        )
        != "backend"
    ):
        return mounts


    bindings = (
        extract_python_import_bindings(
            content
        )
    )


    constants = (
        extract_string_constants(
            content
        )
    )


    pattern = re.compile(
        (
            r"\b"
            r"([A-Za-z_][\w]*)"
            r"\.include_router\s*\("
        )
    )


    for match in (
        pattern.finditer(
            content
        )
    ):

        opening_index = (
            match.end()
            - 1
        )


        closing_index = (
            find_matching_parenthesis(
                content,
                opening_index,
            )
        )


        if (
            closing_index
            is None
        ):
            continue


        arguments = (
            split_top_level_arguments(
                content[
                    opening_index + 1:
                    closing_index
                ]
            )
        )


        if not arguments:
            continue


        router_expression = (
            arguments[
                0
            ].strip()
        )


        root_identifier = (
            router_expression.split(
                "."
            )[0]
        )


        module_binding = (
            bindings.get(
                root_identifier
            )
        )


        if not module_binding:
            continue


        resolved = (
            resolve_python_binding(
                path,
                module_binding,
                source_files,
            )
        )


        if not resolved:
            continue


        prefix = "/"


        prefix_match = (
            re.search(
                (
                    r"\bprefix\s*=\s*"
                    r"([^,\n)]+)"
                ),
                content[
                    opening_index + 1:
                    closing_index
                ],
            )
        )


        if prefix_match:

            parsed_prefix = (
                parse_string_expression(
                    prefix_match.group(
                        1
                    ),
                    constants,
                )
            )


            if parsed_prefix:
                prefix = (
                    normalize_endpoint(
                        parsed_prefix
                    )
                )


        mounts.append(
            {
                "mount_file":
                    path,

                "prefix":
                    prefix,

                "router_file":
                    resolved,
            }
        )


    return mounts


# =========================================================
# FLASK ANALYSIS
# =========================================================

def extract_flask_routes(
    path: str,
    content: str,
) -> List[dict]:

    routes = []


    if (
        get_file_layer(
            path,
            content,
        )
        != "backend"
    ):
        return routes


    pattern = re.compile(
        (
            r"@\s*"
            r"([A-Za-z_][\w]*)"
            r"\.route\s*\(\s*"
            r'(["\'])'
            r'([^"\']+)'
            r"\2"
            r"([\s\S]*?)"
            r"\)"
        ),
        re.IGNORECASE,
    )


    for match in (
        pattern.finditer(
            content
        )
    ):

        endpoint = (
            normalize_endpoint(
                match.group(
                    3
                )
            )
        )


        options = (
            match.group(
                4
            )
        )


        methods = re.findall(
            (
                r'["\']'
                r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)"
                r'["\']'
            ),
            options,
            re.IGNORECASE,
        )


        if not methods:
            methods = [
                "GET"
            ]


        following = (
            content[
                match.end():
                match.end() + 500
            ]
        )


        handler_match = (
            re.search(
                (
                    r"(?:async\s+)?"
                    r"def\s+"
                    r"([A-Za-z_][\w]*)"
                ),
                following,
            )
        )


        handler = (
            handler_match.group(
                1
            )
            if handler_match
            else None
        )


        for method in methods:

            routes.append(
                {
                    "file":
                        path,

                    "method":
                        method.upper(),

                    "endpoint":
                        endpoint,

                    "framework":
                        "Flask",

                    "handler":
                        handler,

                    "controller_file":
                        path,
                }
            )


    return deduplicate_dicts(
        routes,
        keys=(
            "file",
            "method",
            "endpoint",
            "handler",
        ),
    )


# =========================================================
# SPRING ANALYSIS
# =========================================================

def extract_spring_routes(
    path: str,
    content: str,
) -> List[dict]:

    suffix = (
        PurePosixPath(
            path
        )
        .suffix
        .lower()
    )


    if suffix not in {
        ".java",
        ".kt",
    }:
        return []


    routes = []


    class_prefix = "/"


    class_request_match = (
        re.search(
            (
                r"@RequestMapping"
                r"\s*\(\s*"
                r"(?:value\s*=\s*)?"
                r'["\']([^"\']+)["\']'
            ),
            content,
        )
    )


    if class_request_match:

        class_prefix = (
            normalize_endpoint(
                class_request_match.group(
                    1
                )
            )
        )


    method_map = {
        "GetMapping":
            "GET",

        "PostMapping":
            "POST",

        "PutMapping":
            "PUT",

        "PatchMapping":
            "PATCH",

        "DeleteMapping":
            "DELETE",
    }


    mapping_pattern = re.compile(
        (
            r"@("
            +
            "|".join(
                method_map
            )
            +
            r")"
            r"\s*\(\s*"
            r"(?:value\s*=\s*)?"
            r'(?:(["\'])'
            r'([^"\']*)'
            r"\2)?"
            r"\s*\)"
        )
    )


    for match in (
        mapping_pattern.finditer(
            content
        )
    ):

        route = (
            match.group(
                3
            )
            or "/"
        )


        endpoint = (
            join_route_prefix(
                class_prefix,
                route,
            )
        )


        following = (
            content[
                match.end():
                match.end() + 500
            ]
        )


        handler_match = re.search(
            (
                r"(?:public|private|protected)?"
                r"\s*"
                r"(?:suspend\s+)?"
                r"(?:[\w<>\[\],?]+\s+)+"
                r"([A-Za-z_][\w]*)"
                r"\s*\("
            ),
            following,
        )


        routes.append(
            {
                "file":
                    path,

                "method":
                    method_map[
                        match.group(
                            1
                        )
                    ],

                "endpoint":
                    endpoint,

                "framework":
                    "Spring",

                "handler":
                    (
                        handler_match.group(
                            1
                        )
                        if handler_match
                        else None
                    ),

                "controller_file":
                    path,
            }
        )


    request_mapping_pattern = re.compile(
        (
            r"@RequestMapping"
            r"\s*\(\s*"
            r"(?:value\s*=\s*)?"
            r'["\']([^"\']+)["\']'
            r"([\s\S]*?)"
            r"\)"
        )
    )


    for match in (
        request_mapping_pattern
        .finditer(
            content
        )
    ):

        options = (
            match.group(
                2
            )
        )


        method_match = (
            re.search(
                (
                    r"RequestMethod\."
                    r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)"
                ),
                options,
            )
        )


        if not method_match:
            continue


        endpoint = (
            join_route_prefix(
                class_prefix,
                match.group(
                    1
                ),
            )
        )


        routes.append(
            {
                "file":
                    path,

                "method":
                    method_match.group(
                        1
                    ),

                "endpoint":
                    endpoint,

                "framework":
                    "Spring",

                "handler":
                    None,

                "controller_file":
                    path,
            }
        )


    return deduplicate_dicts(
        routes,
        keys=(
            "file",
            "method",
            "endpoint",
            "handler",
        ),
    )


# =========================================================
# REQUEST FLOW MATCHING
# =========================================================

def choose_best_matching_route(
    request: dict,
    backend_routes:
        List[dict],
) -> Optional[dict]:

    matches = []


    for route in (
        backend_routes
    ):

        if (
            request[
                "method"
            ]
            != route[
                "method"
            ]
        ):
            continue


        if not routes_match(
            request[
                "endpoint"
            ],
            route[
                "endpoint"
            ],
        ):
            continue


        score = 0


        frontend_endpoint = (
            normalize_endpoint(
                request[
                    "endpoint"
                ]
            )
        )


        backend_endpoint = (
            normalize_endpoint(
                route[
                    "endpoint"
                ]
            )
        )


        if (
            frontend_endpoint
            == backend_endpoint
        ):
            score += 100


        score += len(
            backend_endpoint
        )


        matches.append(
            (
                score,
                route,
            )
        )


    if not matches:
        return None


    matches.sort(
        key=lambda item:
            item[
                0
            ],
        reverse=True,
    )


    return matches[
        0
    ][
        1
    ]


def build_request_flows(
    frontend_requests:
        List[dict],
    backend_routes:
        List[dict],
) -> List[dict]:

    flows = []


    for request in (
        frontend_requests
    ):

        matched_route = (
            choose_best_matching_route(
                request,
                backend_routes,
            )
        )


        flows.append(
            {
                "frontend_file":
                    request[
                        "file"
                    ],

                "backend_file":
                    (
                        matched_route[
                            "file"
                        ]
                        if matched_route
                        else None
                    ),

                "controller_file":
                    (
                        matched_route.get(
                            "controller_file"
                        )
                        if matched_route
                        else None
                    ),

                "method":
                    request[
                        "method"
                    ],

                "endpoint":
                    request[
                        "endpoint"
                    ],

                "handler":
                    (
                        matched_route.get(
                            "handler"
                        )
                        if matched_route
                        else None
                    ),

                "matched":
                    (
                        matched_route
                        is not None
                    ),
            }
        )


    return flows


# =========================================================
# DATA LAYER DETECTION
# =========================================================

def detect_data_connections(
    path: str,
    imports: List[str],
    content: str,
) -> List[dict]:

    connections = []


    layer = (
        get_file_layer(
            path,
            content,
        )
    )


    if layer == "frontend":
        return connections


    detected: Set[str] = set()


    lower_content = (
        content.lower()
    )


    file_name = (
        PurePosixPath(
            path
        )
        .name
        .lower()
    )


    # =====================================================
    # PRISMA
    #
    # IMPORTANT:
    # prisma.config.ts by itself is configuration.
    # We only count Prisma when the runtime client or
    # actual Prisma operations are visible.
    # =====================================================

    prisma_runtime = bool(
        re.search(
            r"\bnew\s+prismaclient\s*\(",
            content,
            re.IGNORECASE,
        )
        or re.search(
            (
                r"\b(?:prisma|db|database)\."
                r"[A-Za-z_$][\w$]*\."
                r"(?:"
                r"findMany|"
                r"findFirst|"
                r"findUnique|"
                r"create|"
                r"createMany|"
                r"update|"
                r"updateMany|"
                r"delete|"
                r"deleteMany|"
                r"upsert|"
                r"count|"
                r"aggregate|"
                r"groupBy"
                r")\s*\("
            ),
            content,
            re.IGNORECASE,
        )
        or re.search(
            (
                r"\b(?:prisma|db|database)\.\$"
                r"(?:"
                r"transaction|"
                r"queryRaw|"
                r"executeRaw"
                r")"
                r"\s*(?:<[^>]+>)?\s*\("
            ),
            content,
            re.IGNORECASE,
        )
    )


    if prisma_runtime:
        detected.add(
            "Prisma"
        )


    # =====================================================
    # REDIS
    #
    # REDIS_URL and redis:// are NOT enough anymore.
    #
    # We require real Redis client usage.
    # =====================================================

    redis_packages = {
        "redis",
        "ioredis",
        "@upstash/redis",
    }


    redis_imported = False


    for imported_path in imports:

        imported_lower = (
            imported_path.lower()
        )


        package_name = (
            get_external_package_name(
                imported_path
            )
            .lower()
        )


        if (
            imported_lower
            in redis_packages
            or package_name
            in redis_packages
        ):
            redis_imported = True
            break


    redis_runtime = bool(
        re.search(
            (
                r"\b(?:redis|redisClient|redis_client|cache)\."
                r"(?:"
                r"get|"
                r"set|"
                r"setex|"
                r"setEx|"
                r"del|"
                r"delete|"
                r"exists|"
                r"incr|"
                r"incrby|"
                r"decr|"
                r"expire|"
                r"ttl|"
                r"hget|"
                r"hset|"
                r"lpush|"
                r"rpush|"
                r"sadd|"
                r"srem|"
                r"publish|"
                r"subscribe|"
                r"multi|"
                r"pipeline"
                r")\s*\("
            ),
            content,
            re.IGNORECASE,
        )
        or (
            redis_imported
            and re.search(
                r"\bnew\s+Redis\s*\(",
                content,
                re.IGNORECASE,
            )
        )
        or (
            redis_imported
            and re.search(
                r"\bcreateClient\s*\(",
                content,
                re.IGNORECASE,
            )
        )
        or (
            redis_imported
            and re.search(
                (
                    r"\bRedis\."
                    r"(?:fromEnv|from_url)"
                    r"\s*\("
                ),
                content,
                re.IGNORECASE,
            )
        )
    )


    if redis_runtime:
        detected.add(
            "Redis"
        )


    # =====================================================
    # OTHER DATA PACKAGES
    # =====================================================

    for imported_path in imports:

        package_name = (
            get_external_package_name(
                imported_path
            )
        )


        technology = (
            DATA_PACKAGE_MAP.get(
                imported_path.lower()
            )
            or
            DATA_PACKAGE_MAP.get(
                package_name.lower()
            )
        )


        if not technology:
            continue


        # Prisma is handled above with stronger runtime
        # evidence.
        if technology == "Prisma":
            continue


        # Redis is handled above with stronger runtime
        # evidence.
        if technology == "Redis":
            continue


        detected.add(
            technology
        )


    # =====================================================
    # PRISMA SCHEMA DATABASE PROVIDER
    #
    # schema.prisma is legitimate repository-level DB
    # evidence.
    #
    # Unlike REDIS_URL, this is an explicit database
    # provider declaration.
    # =====================================================

    if file_name == "schema.prisma":

        provider_map = {
            "postgresql":
                "PostgreSQL",

            "postgres":
                "PostgreSQL",

            "mysql":
                "MySQL",

            "sqlite":
                "SQLite",

            "mongodb":
                "MongoDB",

            "sqlserver":
                "SQL Server",

            "cockroachdb":
                "CockroachDB",
        }


        providers = re.findall(
            (
                r"\bprovider\s*=\s*"
                r'["\']([^"\']+)["\']'
            ),
            content,
            re.IGNORECASE,
        )


        for provider in providers:

            technology = (
                provider_map.get(
                    provider
                    .strip()
                    .lower()
                )
            )


            if technology:

                detected.add(
                    technology
                )


    # =====================================================
    # DIRECT RUNTIME PATTERNS
    # =====================================================

    runtime_patterns = (
        (
            r"\bmongoose\.(?:connect|createConnection|model)\s*\(",
            "MongoDB / Mongoose",
        ),

        (
            r"\bnew\s+MongoClient\s*\(",
            "MongoDB",
        ),

        (
            r"\b(?:psycopg|psycopg2|asyncpg)\.connect\s*\(",
            "PostgreSQL",
        ),

        (
            r"\bnew\s+(?:Pool|Client)\s*\(",
            "PostgreSQL",
        ),

        (
            r"\bcreate_engine\s*\(",
            "SQLAlchemy",
        ),

        (
            r"\bnew\s+Sequelize\s*\(",
            "Sequelize",
        ),

        (
            r"\bnew\s+DataSource\s*\(",
            "TypeORM",
        ),

        (
            r"\bdrizzle\s*\(",
            "Drizzle ORM",
        ),
    )


    for (
        pattern,
        technology,
    ) in runtime_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE,
        ):

            detected.add(
                technology
            )


    # =====================================================
    # IMPORTANT:
    #
    # We intentionally DO NOT detect databases merely from:
    #
    # REDIS_URL
    # redis://
    # DATABASE_URL
    # postgres://
    # postgresql://
    # mysql://
    #
    # Environment variables are configuration references,
    # not proof of runtime usage.
    # =====================================================


    for technology in sorted(
        detected
    ):

        connections.append(
            {
                "file":
                    path,

                "technology":
                    technology,

                "connection_type":
                    "data-layer",
            }
        )


    return connections


# =========================================================
# FUNCTION RANGE DETECTION
# =========================================================

def get_function_ranges(
    content: str,
) -> List[dict]:

    patterns = [
        re.compile(
            (
                r"(?:export\s+)?"
                r"(?:default\s+)?"
                r"(?:async\s+)?"
                r"function\s+"
                r"([A-Za-z_$][\w$]*)"
                r"\s*\("
            )
        ),

        re.compile(
            (
                r"(?:export\s+)?"
                r"(?:const|let|var)\s+"
                r"([A-Za-z_$][\w$]*)"
                r"(?:\s*:\s*[^=;]+)?"
                r"\s*=\s*"
                r"(?:async\s*)?"
                r"(?:"
                r"\([^;=]*?\)"
                r"|"
                r"[A-Za-z_$][\w$]*"
                r")"
                r"\s*=>"
            )
        ),

        re.compile(
            (
                r"(?:async\s+)?"
                r"def\s+"
                r"([A-Za-z_][\w]*)"
                r"\s*\("
            )
        ),
    ]


    matches = []


    for pattern in patterns:

        for match in (
            pattern.finditer(
                content
            )
        ):

            matches.append(
                {
                    "name":
                        match.group(
                            1
                        ),

                    "start":
                        match.start(),
                }
            )


    matches.sort(
        key=lambda item:
            item[
                "start"
            ]
    )


    functions = []


    for (
        index,
        item,
    ) in enumerate(
        matches
    ):

        end = (
            matches[
                index + 1
            ][
                "start"
            ]
            if (
                index + 1
                < len(
                    matches
                )
            )
            else len(
                content
            )
        )


        functions.append(
            {
                "name":
                    item[
                        "name"
                    ],

                "start":
                    item[
                        "start"
                    ],

                "end":
                    end,
            }
        )


    return functions


def find_handler_for_position(
    function_ranges:
        List[dict],
    position: int,
) -> Optional[str]:

    for function in (
        function_ranges
    ):

        if (
            function[
                "start"
            ]
            <= position
            < function[
                "end"
            ]
        ):
            return function[
                "name"
            ]


    return None


# =========================================================
# EXTERNAL PROVIDER DETECTION
# =========================================================

def detect_provider_services(
    imports: List[str],
) -> Set[str]:

    services: Set[
        str
    ] = set()


    for imported_path in (
        imports
    ):

        package_name = (
            get_external_package_name(
                imported_path
            )
        )


        service = (
            PROVIDER_PACKAGE_MAP.get(
                imported_path.lower()
            )
            or
            PROVIDER_PACKAGE_MAP.get(
                package_name.lower()
            )
        )


        if service:
            services.add(
                service
            )


    return services


def service_to_sdk_endpoint(
    service: str,
) -> str:

    slug = (
        service
        .lower()
        .replace(
            " api",
            "",
        )
        .replace(
            " ",
            "-",
        )
    )


    return (
        f"sdk://{slug}"
    )


def extract_external_api_calls(
    path: str,
    content: str,
    imports:
        Optional[
            List[str]
        ] = None,
    source_files:
        Optional[
            Set[str]
        ] = None,
    client_definitions:
        Optional[
            Dict[
                str,
                List[dict],
            ]
        ] = None,
    provider_services_override:
        Optional[
            Set[str]
        ] = None,
) -> List[dict]:

    imports = (
        imports
        if imports is not None
        else extract_imports(
            path,
            content,
        )
    )


    source_files = (
        source_files
        or set()
    )


    client_definitions = (
        client_definitions
        or {}
    )


    calls = []


    if (
        get_file_layer(
            path,
            content,
        )
        == "frontend"
    ):
        return calls


    function_ranges = (
        get_function_ranges(
            content
        )
    )


    http_requests = (
        extract_http_requests(
            path,
            content,
            source_files,
            client_definitions,
        )
    )


    for request in (
        http_requests
    ):

        endpoint = (
            request[
                "endpoint"
            ]
        )


        if (
            not is_external_url(
                endpoint
            )
            or is_local_url(
                endpoint
            )
        ):
            continue


        position = (
            content.find(
                endpoint
            )
        )


        calls.append(
            {
                "file":
                    path,

                "method":
                    request[
                        "method"
                    ],

                "endpoint":
                    endpoint,

                "service":
                    get_external_service_name(
                        endpoint
                    ),

                "handler":
                    (
                        find_handler_for_position(
                            function_ranges,
                            max(
                                0,
                                position,
                            ),
                        )
                        if position >= 0
                        else None
                    ),
            }
        )


    provider_services = set(
        provider_services_override
        or set()
    )


    provider_services.update(
        detect_provider_services(
            imports
        )
    )


    provider_markers = {
        "Groq API": (
            "chat.completions.create",
            "responses.create",
            "groq.",
        ),

        "OpenAI API": (
            "chat.completions.create",
            "responses.create",
            "embeddings.create",
            "openai.",
        ),

        "Anthropic API": (
            "messages.create",
            "anthropic.",
        ),

        "Google Gemini API": (
            "generatecontent",
            "generativemodel",
            "models.generate",
        ),

        "Mistral API": (
            "chat.complete",
            "mistral.",
        ),

        "Cohere API": (
            ".chat(",
            ".embed(",
            "cohere.",
        ),

        "Hugging Face API": (
            "textgeneration",
            "featureextraction",
            "inference.",
        ),
    }


    lowered_content = (
        content.lower()
    )


    for service in sorted(
        provider_services
    ):

        markers = (
            provider_markers.get(
                service,
                (),
            )
        )


        if (
            markers
            and not any(
                marker.lower()
                in lowered_content

                for marker
                in markers
            )
        ):
            continue


        marker_position = 0


        for marker in (
            markers
        ):

            found = (
                lowered_content.find(
                    marker.lower()
                )
            )


            if found >= 0:

                marker_position = (
                    found
                )

                break


        calls.append(
            {
                "file":
                    path,

                "method":
                    "SDK",

                "endpoint":
                    service_to_sdk_endpoint(
                        service
                    ),

                "service":
                    service,

                "handler":
                    find_handler_for_position(
                        function_ranges,
                        marker_position,
                    ),
            }
        )


    return deduplicate_dicts(
        calls,
        keys=(
            "file",
            "method",
            "endpoint",
            "service",
            "handler",
        ),
    )


# =========================================================
# HANDLER-SPECIFIC DEPENDENCIES
# =========================================================

def build_handler_dependency_map(
    contents:
        Dict[
            str,
            str,
        ],
    source_files:
        Set[str],
) -> Dict[
    Tuple[
        str,
        str,
    ],
    Set[str],
]:

    dependency_map: Dict[
        Tuple[
            str,
            str,
        ],
        Set[str],
    ] = {}


    for (
        path,
        content,
    ) in contents.items():

        if (
            path
            not in source_files
        ):
            continue


        suffix = (
            PurePosixPath(
                path
            )
            .suffix
            .lower()
        )


        function_ranges = (
            get_function_ranges(
                content
            )
        )


        if not function_ranges:
            continue


        if suffix in (
            JS_EXTENSIONS
        ):

            bindings = (
                extract_js_import_bindings(
                    content
                )
            )


            resolved_bindings = {}


            for (
                local_name,
                binding,
            ) in bindings.items():

                resolved = (
                    resolve_js_import(
                        path,
                        binding[
                            "source"
                        ],
                        source_files,
                    )
                )


                if resolved:
                    resolved_bindings[
                        local_name
                    ] = resolved


        elif suffix == ".py":

            python_bindings = (
                extract_python_import_bindings(
                    content
                )
            )


            resolved_bindings = {}


            for (
                local_name,
                module,
            ) in python_bindings.items():

                resolved = (
                    resolve_python_binding(
                        path,
                        module,
                        source_files,
                    )
                )


                if resolved:
                    resolved_bindings[
                        local_name
                    ] = resolved


        else:
            continue


        for function in (
            function_ranges
        ):

            body = (
                content[
                    function[
                        "start"
                    ]:
                    function[
                        "end"
                    ]
                ]
            )


            dependencies = (
                set()
            )


            for (
                local_name,
                target,
            ) in (
                resolved_bindings
                .items()
            ):

                if re.search(
                    (
                        rf"\b"
                        rf"{re.escape(local_name)}"
                        rf"\b"
                    ),
                    body,
                ):
                    dependencies.add(
                        target
                    )


            dependency_map[
                (
                    path,
                    function[
                        "name"
                    ],
                )
            ] = dependencies


    return dependency_map


# =========================================================
# GRAPH TRAVERSAL
# =========================================================

def get_reachable_files(
    start_files:
        List[str],
    edges:
        List[dict],
    max_depth: int = 6,
) -> Set[str]:

    adjacency: Dict[
        str,
        Set[str],
    ] = {}


    for edge in edges:

        if (
            edge.get(
                "relationship"
            )
            not in {
                None,
                "imports",
                "calls",
                "uses",
            }
        ):
            continue


        source = (
            edge[
                "source"
            ]
        )


        target = (
            edge[
                "target"
            ]
        )


        adjacency.setdefault(
            source,
            set(),
        ).add(
            target
        )


    visited = {
        path

        for path
        in start_files

        if path
    }


    frontier = set(
        visited
    )


    for _ in range(
        max_depth
    ):

        next_frontier = (
            set()
        )


        for file_path in (
            frontier
        ):

            for target in (
                adjacency.get(
                    file_path,
                    set(),
                )
            ):

                if (
                    target
                    in visited
                ):
                    continue


                visited.add(
                    target
                )


                next_frontier.add(
                    target
                )


        if not next_frontier:
            break


        frontier = (
            next_frontier
        )


    return visited


def get_related_data_technologies(
    route_file:
        Optional[str],
    controller_file:
        Optional[str],
    handler:
        Optional[str],
    edges:
        List[dict],
    data_connections:
        List[dict],
    handler_dependencies:
        Optional[
            Dict[
                Tuple[
                    str,
                    str,
                ],
                Set[str],
            ]
        ] = None,
) -> List[str]:

    handler_dependencies = (
        handler_dependencies
        or {}
    )


    specific_dependencies = (
        set()
    )


    if (
        controller_file
        and handler
    ):

        specific_dependencies = (
            handler_dependencies.get(
                (
                    controller_file,
                    handler,
                ),
                set(),
            )
        )


    if specific_dependencies:

        start_files = list(
            specific_dependencies
        )

    else:
        start_files = [
            path

            for path
            in {
                route_file,
                controller_file,
            }

            if path
        ]


    reachable = (
        get_reachable_files(
            start_files,
            edges,
        )
    )


    technologies = {
        connection[
            "technology"
        ]

        for connection
        in data_connections

        if (
            connection[
                "file"
            ]
            in reachable
        )
    }


    return sorted(
        technologies
    )


def get_related_external_services(
    route_file:
        Optional[str],
    controller_file:
        Optional[str],
    handler:
        Optional[str],
    edges:
        List[dict],
    external_api_calls:
        List[dict],
    handler_dependencies:
        Optional[
            Dict[
                Tuple[
                    str,
                    str,
                ],
                Set[str],
            ]
        ] = None,
) -> List[str]:

    handler_dependencies = (
        handler_dependencies
        or {}
    )


    services = {
        call[
            "service"
        ]

        for call
        in external_api_calls

        if (
            controller_file
            and call[
                "file"
            ]
            == controller_file
            and handler
            and call.get(
                "handler"
            )
            == handler
        )
    }


    specific_dependencies = (
        set()
    )


    if (
        controller_file
        and handler
    ):

        specific_dependencies = (
            handler_dependencies.get(
                (
                    controller_file,
                    handler,
                ),
                set(),
            )
        )


    if specific_dependencies:

        start_files = list(
            specific_dependencies
        )

    else:
        start_files = [
            path

            for path
            in {
                route_file,
                controller_file,
            }

            if path
        ]


    reachable = (
        get_reachable_files(
            start_files,
            edges,
        )
    )


    for call in (
        external_api_calls
    ):

        if (
            call[
                "file"
            ]
            in reachable
        ):
            services.add(
                call[
                    "service"
                ]
            )


    return sorted(
        services
    )


# =========================================================
# END-TO-END FLOW GENERATION
# =========================================================

def build_end_to_end_flows(
    request_flows:
        List[dict],
    external_api_calls:
        List[dict],
    data_connections:
        List[dict],
    edges:
        List[dict],
    handler_dependencies:
        Optional[
            Dict[
                Tuple[
                    str,
                    str,
                ],
                Set[str],
            ]
        ] = None,
) -> List[dict]:

    flows = []


    for flow in (
        request_flows
    ):

        route_file = (
            flow.get(
                "backend_file"
            )
        )


        controller_file = (
            flow.get(
                "controller_file"
            )
        )


        handler = (
            flow.get(
                "handler"
            )
        )


        external_services = (
            get_related_external_services(
                route_file,
                controller_file,
                handler,
                edges,
                external_api_calls,
                handler_dependencies,
            )
        )


        data_technologies = (
            get_related_data_technologies(
                route_file,
                controller_file,
                handler,
                edges,
                data_connections,
                handler_dependencies,
            )
        )


        flows.append(
            {
                "frontend_file":
                    flow[
                        "frontend_file"
                    ],

                "method":
                    flow[
                        "method"
                    ],

                "endpoint":
                    flow[
                        "endpoint"
                    ],

                "route_file":
                    route_file,

                "controller_file":
                    controller_file,

                "handler":
                    handler,

                "external_services":
                    external_services,

                "data_technologies":
                    data_technologies,
            }
        )


    return flows


# =========================================================
# DEDUPLICATION
# =========================================================

def deduplicate_dicts(
    items:
        List[dict],
    keys:
        Tuple[str, ...],
) -> List[dict]:

    seen = set()
    result = []


    for item in items:

        identity = tuple(
            item.get(
                key
            )

            for key in keys
        )


        if identity in seen:
            continue


        seen.add(
            identity
        )


        result.append(
            item
        )


    return result


# =========================================================
# FRONTEND REQUEST CLASSIFICATION
# =========================================================

def classify_frontend_requests(
    requests:
        List[dict],
    backend_routes:
        List[dict],
) -> Tuple[
    List[dict],
    List[dict],
]:

    internal = []
    external = []


    for request in (
        requests
    ):

        endpoint = (
            request[
                "endpoint"
            ]
        )


        matching_route = (
            choose_best_matching_route(
                request,
                backend_routes,
            )
        )


        if matching_route:

            internal.append(
                request
            )

            continue


        if (
            is_external_url(
                endpoint
            )
            and not is_local_url(
                endpoint
            )
        ):

            external.append(
                {
                    "file":
                        request[
                            "file"
                        ],

                    "method":
                        request[
                            "method"
                        ],

                    "endpoint":
                        endpoint,

                    "service":
                        get_external_service_name(
                            endpoint
                        ),

                    "handler":
                        None,
                }
            )

            continue


        internal.append(
            request
        )


    return (
        internal,
        external,
    )


# =========================================================
# MAIN ARCHITECTURE ANALYZER
# =========================================================

async def analyze_architecture(
    owner: str,
    repo_name: str,
    branch: str,
    tree: List[dict],
    architecture: str,
) -> Dict:

    # -----------------------------------------------------
    # DISCOVER FILES
    # -----------------------------------------------------

    source_files = (
        get_source_files(
            tree
        )
    )


    support_files = (
        get_support_files(
            tree
        )
    )


    source_file_set = set(
        source_files
    )


    fetch_paths = sorted(
        set(
            source_files
            +
            support_files
        )
    )


    # -----------------------------------------------------
    # FETCH SOURCE IN PARALLEL
    # -----------------------------------------------------

    contents = (
        await fetch_repository_contents(
            owner,
            repo_name,
            branch,
            fetch_paths,
        )
    )


    # -----------------------------------------------------
    # BUILD SOURCE NODES
    # -----------------------------------------------------

    nodes = []


    for path in (
        source_files
    ):

        content = (
            contents.get(
                path,
                "",
            )
        )


        nodes.append(
            {
                "id":
                    path,

                "label":
                    PurePosixPath(
                        path
                    ).name,

                "path":
                    path,

                "node_type":
                    get_node_type(
                        path
                    ),

                "language":
                    get_language_from_path(
                        path
                    ),

                "layer":
                    get_file_layer(
                        path,
                        content,
                    ),
            }
        )


    # -----------------------------------------------------
    # IMPORT GRAPH
    # -----------------------------------------------------

    edges = []


    external_usage: Dict[
        str,
        Set[str],
    ] = {}


    imports_by_file: Dict[
        str,
        List[str],
    ] = {}


    client_definitions: Dict[
        str,
        List[dict],
    ] = {}


    for path in (
        source_files
    ):

        content = (
            contents.get(
                path
            )
        )


        if not content:
            continue


        imports = (
            extract_imports(
                path,
                content,
            )
        )


        imports_by_file[
            path
        ] = imports


        suffix = (
            PurePosixPath(
                path
            )
            .suffix
            .lower()
        )


        if suffix in (
            JS_EXTENSIONS
        ):

            client_definitions[
                path
            ] = (
                extract_http_client_definitions(
                    path,
                    content,
                )
            )


        for imported_path in (
            imports
        ):

            resolved_path = None


            if suffix in (
                JS_EXTENSIONS
            ):

                resolved_path = (
                    resolve_js_import(
                        path,
                        imported_path,
                        source_file_set,
                    )
                )


            elif suffix == ".py":

                resolved_path = (
                    resolve_python_import(
                        path,
                        imported_path,
                        source_file_set,
                    )
                )


            if resolved_path:

                edge = {
                    "source":
                        path,

                    "target":
                        resolved_path,

                    "relationship":
                        "imports",
                }


                if edge not in edges:
                    edges.append(
                        edge
                    )


                continue


            if (
                imported_path.startswith(
                    "."
                )
                or imported_path.startswith(
                    "@/"
                )
            ):
                continue


            package_name = (
                get_external_package_name(
                    imported_path
                )
            )


            if not package_name:
                continue


            external_usage.setdefault(
                package_name,
                set(),
            ).add(
                path
            )


    # -----------------------------------------------------
    # PROPAGATE PROVIDER KNOWLEDGE
    #
    # Example:
    #
    # llm.service.ts
    #   imports local groq config
    #
    # config/groq.ts
    #   imports groq-sdk
    #
    # This allows llm.service.ts to inherit knowledge that
    # the local client is backed by Groq.
    # -----------------------------------------------------

    provider_services_by_file: Dict[
        str,
        Set[str],
    ] = {
        path:
            detect_provider_services(
                imports_by_file.get(
                    path,
                    [],
                )
            )

        for path
        in source_files
    }


    for _ in range(
        8
    ):

        changed = False


        for edge in edges:

            if (
                edge.get(
                    "relationship"
                )
                != "imports"
            ):
                continue


            source = (
                edge[
                    "source"
                ]
            )


            target = (
                edge[
                    "target"
                ]
            )


            target_services = (
                provider_services_by_file.get(
                    target,
                    set(),
                )
            )


            if not target_services:
                continue


            source_services = (
                provider_services_by_file.setdefault(
                    source,
                    set(),
                )
            )


            before = len(
                source_services
            )


            source_services.update(
                target_services
            )


            if (
                len(
                    source_services
                )
                != before
            ):
                changed = True


        if not changed:
            break


    # -----------------------------------------------------
    # BACKEND ROUTE DETECTION
    # -----------------------------------------------------

    backend_routes = []
    express_mounts = []
    fastapi_mounts = []


    for path in (
        source_files
    ):

        content = (
            contents.get(
                path
            )
        )


        if not content:
            continue


        suffix = (
            PurePosixPath(
                path
            )
            .suffix
            .lower()
        )


        layer = (
            get_file_layer(
                path,
                content,
            )
        )


        if layer != "backend":
            continue


        if suffix in (
            JS_EXTENSIONS
        ):

            express_mounts.extend(
                extract_express_mounts(
                    path,
                    content,
                    source_file_set,
                )
            )


            backend_routes.extend(
                extract_express_routes(
                    path,
                    content,
                    source_file_set,
                )
            )


        if suffix == ".py":

            backend_routes.extend(
                extract_fastapi_routes(
                    path,
                    content,
                )
            )


            fastapi_mounts.extend(
                extract_fastapi_mounts(
                    path,
                    content,
                    source_file_set,
                )
            )


            backend_routes.extend(
                extract_flask_routes(
                    path,
                    content,
                )
            )


        if suffix in {
            ".java",
            ".kt",
        }:

            backend_routes.extend(
                extract_spring_routes(
                    path,
                    content,
                )
            )


    backend_routes = (
        apply_mount_prefixes(
            backend_routes,
            express_mounts,
            "Express",
        )
    )


    backend_routes = (
        apply_mount_prefixes(
            backend_routes,
            fastapi_mounts,
            "FastAPI",
        )
    )


    backend_routes = (
        deduplicate_dicts(
            backend_routes,
            keys=(
                "file",
                "method",
                "endpoint",
                "framework",
                "handler",
            ),
        )
    )


    # -----------------------------------------------------
    # FRONTEND HTTP REQUEST DETECTION
    # -----------------------------------------------------

    all_frontend_request_candidates = []


    for path in (
        source_files
    ):

        content = (
            contents.get(
                path
            )
        )


        if not content:
            continue


        layer = (
            get_file_layer(
                path,
                content,
            )
        )


        if layer != "frontend":
            continue


        suffix = (
            PurePosixPath(
                path
            )
            .suffix
            .lower()
        )


        if suffix not in (
            JS_EXTENSIONS
        ):
            continue


        all_frontend_request_candidates.extend(
            extract_http_requests(
                path,
                content,
                source_file_set,
                client_definitions,
            )
        )


    (
        frontend_requests,
        frontend_external_calls,
    ) = classify_frontend_requests(
        all_frontend_request_candidates,
        backend_routes,
    )


    # -----------------------------------------------------
    # EXTERNAL API + DATA LAYER ANALYSIS
    # -----------------------------------------------------

    external_api_calls = list(
        frontend_external_calls
    )


    data_connections = []


    for path in (
        fetch_paths
    ):

        content = (
            contents.get(
                path
            )
        )


        if not content:
            continue


        imports = (
            imports_by_file.get(
                path,
                [],
            )
        )


        if (
            path
            not in imports_by_file
            and PurePosixPath(
                path
            )
            .suffix
            .lower()
            in SOURCE_EXTENSIONS
        ):
            imports = (
                extract_imports(
                    path,
                    content,
                )
            )


        data_connections.extend(
            detect_data_connections(
                path,
                imports,
                content,
            )
        )


        if (
            path
            in source_file_set
        ):

            external_api_calls.extend(
                extract_external_api_calls(
                    path,
                    content,
                    imports,
                    source_file_set,
                    client_definitions,
                    provider_services_by_file.get(
                        path,
                        set(),
                    ),
                )
            )


    # -----------------------------------------------------
    # EXTERNAL DEPENDENCIES
    # -----------------------------------------------------

    external_dependencies = []


    for name in sorted(
        external_usage
    ):

        external_dependencies.append(
            {
                "name":
                    name,

                "used_by":
                    sorted(
                        external_usage[
                            name
                        ]
                    ),
            }
        )


    # -----------------------------------------------------
    # DEDUPLICATE
    # -----------------------------------------------------

    unique_frontend_requests = (
        deduplicate_dicts(
            frontend_requests,
            keys=(
                "file",
                "method",
                "endpoint",
            ),
        )
    )


    unique_external_calls = (
        deduplicate_dicts(
            external_api_calls,
            keys=(
                "file",
                "method",
                "endpoint",
                "service",
                "handler",
            ),
        )
    )


    unique_data_connections = (
        deduplicate_dicts(
            data_connections,
            keys=(
                "file",
                "technology",
                "connection_type",
            ),
        )
    )


    # -----------------------------------------------------
    # HANDLER DEPENDENCY GRAPH
    # -----------------------------------------------------

    handler_dependencies = (
        build_handler_dependency_map(
            contents,
            source_file_set,
        )
    )


    # -----------------------------------------------------
    # FRONTEND → BACKEND REQUEST FLOWS
    # -----------------------------------------------------

    request_flows = (
        build_request_flows(
            unique_frontend_requests,
            backend_routes,
        )
    )


    # -----------------------------------------------------
    # REQUEST → SERVICE → DB / PROVIDER FLOWS
    # -----------------------------------------------------

    end_to_end_flows = (
        build_end_to_end_flows(
            request_flows,
            unique_external_calls,
            unique_data_connections,
            edges,
            handler_dependencies,
        )
    )


    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {
        "architecture":
            architecture,

        "nodes":
            nodes,

        "edges":
            edges,

        "external_dependencies":
            external_dependencies,

        "frontend_requests":
            unique_frontend_requests,

        "external_api_calls":
            unique_external_calls,

        "backend_routes":
            backend_routes,

        "request_flows":
            request_flows,

        "data_connections":
            unique_data_connections,

        "end_to_end_flows":
            end_to_end_flows,

        "node_count":
            len(
                nodes
            ),

        "edge_count":
            len(
                edges
            ),

        "analyzer_version":
            "2.1",
    }