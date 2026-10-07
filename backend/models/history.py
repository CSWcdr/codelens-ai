from typing import List, Optional

from pydantic import BaseModel


class RepositoryHistoryCreate(BaseModel):
    repo_url: str
    repo_name: str
    owner: str

    description: Optional[str] = None
    primary_language: Optional[str] = None
    primary_framework: Optional[str] = None
    architecture: Optional[str] = None
    default_branch: Optional[str] = None
    commit_sha: Optional[str] = None


class RepositoryHistoryItem(BaseModel):
    id: int

    repo_url: str
    repo_name: str
    owner: str

    description: Optional[str] = None
    primary_language: Optional[str] = None
    primary_framework: Optional[str] = None
    architecture: Optional[str] = None
    default_branch: Optional[str] = None
    commit_sha: Optional[str] = None

    analysis_count: int

    first_analyzed_at: str
    last_analyzed_at: str


class RepositoryHistoryResponse(BaseModel):
    repositories: List[RepositoryHistoryItem]
    total: int


class RepositoryHistoryDeleteResponse(BaseModel):
    deleted: bool
    repo_url: str
    status: str


class RepositoryHistoryClearResponse(BaseModel):
    deleted_count: int
    status: str