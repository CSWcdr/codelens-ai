from pathlib import PurePosixPath

from typing import (
    Dict,
    List,
    Optional,
)


DATABASE_DEPENDENCIES = {
    "mongoose":
        "MongoDB",

    "mongodb":
        "MongoDB",

    "pg":
        "PostgreSQL",

    "psycopg":
        "PostgreSQL",

    "psycopg2":
        "PostgreSQL",

    "@neondatabase/serverless":
        "PostgreSQL",

    "prisma":
        "Prisma",

    "@prisma/client":
        "Prisma",

    "sequelize":
        "SQL database",

    "mysql2":
        "MySQL",

    "sqlite3":
        "SQLite",

    "sqlalchemy":
        "SQL database",

    "redis":
        "Redis",
}


AUTH_DEPENDENCIES = {
    "@clerk/clerk-react":
        "Clerk",

    "@clerk/express":
        "Clerk",

    "@clerk/backend":
        "Clerk",

    "jsonwebtoken":
        "JWT authentication",

    "passport":
        "Passport",

    "next-auth":
        "NextAuth",

    "firebase":
        "Firebase",

    "firebase-admin":
        "Firebase",
}


AI_DEPENDENCIES = {
    "openai":
        "OpenAI",

    "groq":
        "Groq",

    "@google/generative-ai":
        "Google Gemini",

    "@google/genai":
        "Google Gemini",

    "google-generativeai":
        "Google Gemini",

    "anthropic":
        "Anthropic",

    "@anthropic-ai/sdk":
        "Anthropic",

    "langchain":
        "LangChain",

    "@langchain/core":
        "LangChain",

    "transformers":
        "Transformers",

    "tensorflow":
        "TensorFlow",

    "torch":
        "PyTorch",
}


STORAGE_DEPENDENCIES = {
    "cloudinary":
        "Cloudinary",

    "multer":
        "file uploads",

    "@aws-sdk/client-s3":
        "Amazon S3",

    "aws-sdk":
        "AWS services",

    "firebase":
        "Firebase",
}


def normalize_dependencies(
    dependencies: List[str],
) -> set:
    return {
        dependency.lower()
        for dependency
        in dependencies
    }


def get_repository_paths(
    tree: List[dict],
) -> List[str]:
    paths = []

    for item in tree:
        path = item.get(
            "path",
            ""
        )

        if not path:
            continue

        paths.append(
            path
        )

    return paths


def detect_code_roles(
    tree: List[dict],
) -> List[str]:
    paths = (
        get_repository_paths(
            tree
        )
    )

    lower_paths = [
        path.lower()
        for path
        in paths
    ]

    detected = []

    role_checks = [
        (
            "pages",
            (
                "/pages/",
                "pages/",
            ),
        ),
        (
            "components",
            (
                "/components/",
                "components/",
            ),
        ),
        (
            "API routes",
            (
                "/routes/",
                "routes/",
                "/api/",
                "api/",
            ),
        ),
        (
            "controllers",
            (
                "/controllers/",
                "controllers/",
            ),
        ),
        (
            "services",
            (
                "/services/",
                "services/",
            ),
        ),
        (
            "models",
            (
                "/models/",
                "models/",
            ),
        ),
        (
            "middleware",
            (
                "/middleware/",
                "/middlewares/",
                "middleware/",
                "middlewares/",
            ),
        ),
        (
            "configuration",
            (
                "/config/",
                "/configs/",
                "config/",
                "configs/",
            ),
        ),
        (
            "tests",
            (
                "/tests/",
                "/test/",
                "__tests__",
                ".test.",
                ".spec.",
            ),
        ),
    ]

    for (
        label,
        patterns,
    ) in role_checks:
        if any(
            any(
                pattern
                in path
                for pattern
                in patterns
            )
            for path
            in lower_paths
        ):
            detected.append(
                label
            )

    return detected


def detect_path_capabilities(
    tree: List[dict],
) -> List[str]:
    paths = (
        get_repository_paths(
            tree
        )
    )

    lower_paths = [
        path.lower()
        for path
        in paths
    ]

    capabilities = []

    checks = [
        (
            "authentication",
            (
                "auth",
                "login",
                "signin",
                "signup",
            ),
        ),
        (
            "user management",
            (
                "user",
                "profile",
                "account",
            ),
        ),
        (
            "dashboard functionality",
            (
                "dashboard",
            ),
        ),
        (
            "image-related functionality",
            (
                "image",
                "photo",
                "background",
            ),
        ),
        (
            "AI-related functionality",
            (
                "ai",
                "generate",
                "gemini",
                "openai",
                "groq",
                "llm",
            ),
        ),
        (
            "payment-related functionality",
            (
                "payment",
                "checkout",
                "stripe",
                "razorpay",
            ),
        ),
        (
            "community or social functionality",
            (
                "community",
                "social",
                "comment",
            ),
        ),
        (
            "file upload handling",
            (
                "upload",
                "multer",
            ),
        ),
    ]

    for (
        label,
        keywords,
    ) in checks:
        if any(
            any(
                keyword
                in path
                for keyword
                in keywords
            )
            for path
            in lower_paths
        ):
            capabilities.append(
                label
            )

    return capabilities


def detect_dependency_signals(
    dependencies: List[str],
) -> Dict[
    str,
    List[str],
]:
    dependency_set = (
        normalize_dependencies(
            dependencies
        )
    )

    result = {
        "database": [],
        "authentication": [],
        "ai": [],
        "storage": [],
    }

    mappings = {
        "database":
            DATABASE_DEPENDENCIES,

        "authentication":
            AUTH_DEPENDENCIES,

        "ai":
            AI_DEPENDENCIES,

        "storage":
            STORAGE_DEPENDENCIES,
    }

    for (
        category,
        mapping,
    ) in mappings.items():
        found = []

        for (
            dependency,
            label,
        ) in mapping.items():
            if (
                dependency
                in dependency_set
            ):
                found.append(
                    label
                )

        result[
            category
        ] = sorted(
            set(
                found
            )
        )

    return result


def join_naturally(
    values: List[str],
) -> str:
    values = [
        value
        for value
        in values
        if value
    ]

    if not values:
        return ""

    if len(values) == 1:
        return values[0]

    if len(values) == 2:
        return (
            f"{values[0]} "
            f"and {values[1]}"
        )

    return (
        ", ".join(
            values[:-1]
        )
        +
        f", and {values[-1]}"
    )


def format_module_names(
    modules: List[str],
) -> str:
    cleaned = []

    for module in modules[
        :5
    ]:
        name = (
            PurePosixPath(
                module
            )
            .name
        )

        if name:
            cleaned.append(
                name
            )

    return join_naturally(
        cleaned
    )


def build_repository_overview(
    repo_name: str,
    description: Optional[str],
    primary_language: Optional[str],
    primary_framework: Optional[str],
    build_tool: Optional[str],
    architecture: str,
    modules: List[str],
    dependencies: List[str],
    total_files: int,
    tree: List[dict],
) -> Dict:
    code_roles = (
        detect_code_roles(
            tree
        )
    )

    path_capabilities = (
        detect_path_capabilities(
            tree
        )
    )

    dependency_signals = (
        detect_dependency_signals(
            dependencies
        )
    )


    # -----------------------------------------------------
    # PARAGRAPH 1
    # -----------------------------------------------------

    first_parts = []

    first_parts.append(
        (
            f"{repo_name} is a "
            f"{architecture.lower()} "
            "software repository"
        )
    )

    technology_parts = []

    if primary_framework:
        technology_parts.append(
            primary_framework
        )

    if (
        primary_language
        and
        primary_language
        not in technology_parts
    ):
        technology_parts.append(
            primary_language
        )

    if build_tool:
        technology_parts.append(
            build_tool
        )

    if technology_parts:
        first_parts.append(
            (
                " built primarily with "
                +
                join_naturally(
                    technology_parts
                )
            )
        )

    first_sentence = (
        "".join(
            first_parts
        )
        + "."
    )

    paragraph_one_parts = [
        first_sentence
    ]

    if description:
        cleaned_description = (
            description
            .strip()
            .rstrip(".")
        )

        if cleaned_description:
            paragraph_one_parts.append(
                (
                    "Its GitHub description identifies "
                    f"the project as {cleaned_description}."
                )
            )

    if modules:
        module_text = (
            format_module_names(
                modules
            )
        )

        if module_text:
            paragraph_one_parts.append(
                (
                    "The repository is organized into "
                    f"{len(modules)} root module"
                    f"{'' if len(modules) == 1 else 's'}, "
                    f"including {module_text}."
                )
            )


    # -----------------------------------------------------
    # PARAGRAPH 2
    # -----------------------------------------------------

    paragraph_two_parts = []

    if code_roles:
        role_text = (
            join_naturally(
                code_roles[
                    :6
                ]
            )
        )

        paragraph_two_parts.append(
            (
                "The detected code structure contains "
                f"{role_text}."
            )
        )

    integration_parts = []

    databases = (
        dependency_signals[
            "database"
        ]
    )

    auth = (
        dependency_signals[
            "authentication"
        ]
    )

    ai_tools = (
        dependency_signals[
            "ai"
        ]
    )

    storage = (
        dependency_signals[
            "storage"
        ]
    )

    if databases:
        integration_parts.append(
            (
                "data persistence through "
                +
                join_naturally(
                    databases
                )
            )
        )

    if auth:
        integration_parts.append(
            (
                "authentication through "
                +
                join_naturally(
                    auth
                )
            )
        )

    if ai_tools:
        integration_parts.append(
            (
                "AI integrations involving "
                +
                join_naturally(
                    ai_tools
                )
            )
        )

    if storage:
        integration_parts.append(
            (
                "storage or upload handling through "
                +
                join_naturally(
                    storage
                )
            )
        )

    if integration_parts:
        paragraph_two_parts.append(
            (
                "Dependency analysis also indicates "
                +
                join_naturally(
                    integration_parts
                )
                +
                "."
            )
        )

    if (
        path_capabilities
        and
        not integration_parts
    ):
        paragraph_two_parts.append(
            (
                "File and folder names indicate code "
                "associated with "
                +
                join_naturally(
                    path_capabilities[
                        :5
                    ]
                )
                +
                "."
            )
        )

    paragraph_two_parts.append(
        (
            f"CodeLens detected {total_files} source "
            f"file{'s' if total_files != 1 else ''} "
            f"and {len(dependencies)} declared "
            f"dependenc{'ies' if len(dependencies) != 1 else 'y'}."
        )
    )


    # -----------------------------------------------------
    # HIGHLIGHTS
    # -----------------------------------------------------

    highlights = []

    if primary_framework:
        highlights.append(
            f"{primary_framework} framework"
        )

    if build_tool:
        highlights.append(
            f"{build_tool} build tooling"
        )

    if databases:
        highlights.append(
            (
                join_naturally(
                    databases
                )
                +
                " data layer"
            )
        )

    if auth:
        highlights.append(
            (
                join_naturally(
                    auth
                )
                +
                " authentication"
            )
        )

    if ai_tools:
        highlights.append(
            (
                join_naturally(
                    ai_tools
                )
                +
                " AI integration"
            )
        )

    if storage:
        highlights.append(
            (
                join_naturally(
                    storage
                )
                +
                " storage/upload integration"
            )
        )

    for capability in (
        path_capabilities
    ):
        if len(highlights) >= 6:
            break

        label = (
            capability
            .capitalize()
        )

        if (
            label.lower()
            not in {
                item.lower()
                for item
                in highlights
            }
        ):
            highlights.append(
                label
            )


    paragraph_one = (
        " ".join(
            paragraph_one_parts
        )
    )

    paragraph_two = (
        " ".join(
            paragraph_two_parts
        )
    )


    return {
        "summary":
            (
                f"{paragraph_one}\n\n"
                f"{paragraph_two}"
            ),

        "highlights":
            highlights[
                :6
            ],
    }