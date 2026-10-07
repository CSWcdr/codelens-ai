from typing import (
    Dict,
    List,
    Optional,
)

from pydantic import BaseModel


class RepositoryRequest(
    BaseModel
):
    repo_url: str


class RepositoryOverview(
    BaseModel
):
    summary: str

    highlights: List[str]


class RepositoryResponse(
    BaseModel
):
    repo_url: str

    repo_name: str

    owner: str

    description: Optional[str]

    default_branch: Optional[str]

    primary_language: Optional[str]

    languages: Dict[
        str,
        float,
    ]

    stars: int

    forks: int

    open_issues: int

    visibility: Optional[str]

    is_private: bool

    github_url: Optional[str]

    total_files: int

    total_folders: int

    total_modules: int

    modules: List[str]

    dependencies: List[str]

    dependency_count: int

    primary_framework: Optional[str]

    build_tool: Optional[str]

    architecture: str

    overview: RepositoryOverview

    status: str