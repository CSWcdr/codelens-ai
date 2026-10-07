import os
import sqlite3

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from typing import (
    Dict,
    List,
    Optional,
)


BASE_DIRECTORY = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


STORAGE_DIRECTORY = Path(
    os.getenv(
        "CODELENS_STORAGE_DIR",
        str(BASE_DIRECTORY),
    )
)


DATABASE_DIRECTORY = (
    STORAGE_DIRECTORY
    / "data"
)


DATABASE_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


DATABASE_PATH = (
    DATABASE_DIRECTORY
    / "codelens.db"
)


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def utc_now_iso():
    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


def initialize_history_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repository_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                repo_url TEXT NOT NULL UNIQUE,
                repo_name TEXT NOT NULL,
                owner TEXT NOT NULL,

                description TEXT,
                primary_language TEXT,
                primary_framework TEXT,
                architecture TEXT,
                default_branch TEXT,
                commit_sha TEXT,

                analysis_count INTEGER NOT NULL DEFAULT 1,

                first_analyzed_at TEXT NOT NULL,
                last_analyzed_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_repository_history_last_analyzed
            ON repository_history(last_analyzed_at)
            """
        )

        connection.commit()


def normalize_repo_url(
    repo_url: str,
) -> str:
    cleaned = (
        repo_url
        .strip()
        .rstrip("/")
    )

    if cleaned.endswith(
        ".git"
    ):
        cleaned = (
            cleaned[:-4]
        )

    return cleaned


def save_repository_history(
    repo_url: str,
    repo_name: str,
    owner: str,
    description: Optional[str] = None,
    primary_language: Optional[str] = None,
    primary_framework: Optional[str] = None,
    architecture: Optional[str] = None,
    default_branch: Optional[str] = None,
    commit_sha: Optional[str] = None,
) -> Dict:
    initialize_history_database()

    normalized_url = (
        normalize_repo_url(
            repo_url
        )
    )

    now = utc_now_iso()

    with get_connection() as connection:
        existing = (
            connection.execute(
                """
                SELECT *
                FROM repository_history
                WHERE repo_url = ?
                """,
                (
                    normalized_url,
                ),
            )
            .fetchone()
        )

        if existing:
            connection.execute(
                """
                UPDATE repository_history

                SET
                    repo_name = ?,
                    owner = ?,
                    description = ?,
                    primary_language = ?,
                    primary_framework = ?,
                    architecture = ?,
                    default_branch = ?,
                    commit_sha = ?,
                    analysis_count = analysis_count + 1,
                    last_analyzed_at = ?

                WHERE repo_url = ?
                """,
                (
                    repo_name,
                    owner,
                    description,
                    primary_language,
                    primary_framework,
                    architecture,
                    default_branch,
                    commit_sha,
                    now,
                    normalized_url,
                ),
            )

        else:
            connection.execute(
                """
                INSERT INTO repository_history (
                    repo_url,
                    repo_name,
                    owner,
                    description,
                    primary_language,
                    primary_framework,
                    architecture,
                    default_branch,
                    commit_sha,
                    analysis_count,
                    first_analyzed_at,
                    last_analyzed_at
                )

                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    1, ?, ?
                )
                """,
                (
                    normalized_url,
                    repo_name,
                    owner,
                    description,
                    primary_language,
                    primary_framework,
                    architecture,
                    default_branch,
                    commit_sha,
                    now,
                    now,
                ),
            )

        connection.commit()

        row = (
            connection.execute(
                """
                SELECT *
                FROM repository_history
                WHERE repo_url = ?
                """,
                (
                    normalized_url,
                ),
            )
            .fetchone()
        )

    return dict(
        row
    )


def get_repository_history(
    limit: int = 20,
) -> List[Dict]:
    initialize_history_database()

    safe_limit = max(
        1,
        min(
            limit,
            100,
        ),
    )

    with get_connection() as connection:
        rows = (
            connection.execute(
                """
                SELECT *
                FROM repository_history

                ORDER BY
                    last_analyzed_at DESC

                LIMIT ?
                """,
                (
                    safe_limit,
                ),
            )
            .fetchall()
        )

    return [
        dict(row)
        for row in rows
    ]


def get_repository_history_item(
    repo_url: str,
) -> Optional[Dict]:
    initialize_history_database()

    normalized_url = (
        normalize_repo_url(
            repo_url
        )
    )

    with get_connection() as connection:
        row = (
            connection.execute(
                """
                SELECT *
                FROM repository_history
                WHERE repo_url = ?
                """,
                (
                    normalized_url,
                ),
            )
            .fetchone()
        )

    if not row:
        return None

    return dict(
        row
    )


def delete_repository_history_item(
    repo_url: str,
) -> bool:
    initialize_history_database()

    normalized_url = (
        normalize_repo_url(
            repo_url
        )
    )

    with get_connection() as connection:
        cursor = (
            connection.execute(
                """
                DELETE FROM repository_history
                WHERE repo_url = ?
                """,
                (
                    normalized_url,
                ),
            )
        )

        connection.commit()

        return (
            cursor.rowcount > 0
        )


def clear_repository_history() -> int:
    initialize_history_database()

    with get_connection() as connection:
        cursor = (
            connection.execute(
                """
                DELETE FROM repository_history
                """
            )
        )

        deleted_count = (
            cursor.rowcount
        )

        connection.commit()

    return deleted_count