from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
)


class RepositoryIndexRequest(BaseModel):
    repo_url: str


class IndexedFile(BaseModel):
    path: str
    chunk_count: int


class RepositoryIndexResponse(BaseModel):
    repo_name: str
    owner: str

    collection_name: str

    indexed_files: int
    indexed_chunks: int

    files: List[
        IndexedFile
    ]

    cached: bool

    commit_sha: Optional[str]

    status: str


class RepositoryIndexStatusResponse(BaseModel):
    repo_name: str
    owner: str

    indexed: bool
    fresh: bool

    indexed_chunks: int

    commit_sha: Optional[str]
    stored_commit_sha: Optional[str]

    status: str


class RetrievalRequest(BaseModel):
    repo_url: str

    question: str = Field(
        min_length=2,
        max_length=2000,
    )

    limit: int = Field(
        default=6,
        ge=1,
        le=10,
    )


class RetrievedChunk(BaseModel):
    chunk_id: str

    path: str
    language: Optional[str]

    start_line: int
    end_line: int

    content: str

    distance: Optional[float]


class RetrievalResponse(BaseModel):
    repo_name: str

    question: str

    results: List[
        RetrievedChunk
    ]

    result_count: int

    status: str


class AskRequest(BaseModel):
    repo_url: str

    question: str = Field(
        min_length=2,
        max_length=4000,
    )

    limit: int = Field(
        default=6,
        ge=1,
        le=10,
    )


class AnswerSource(BaseModel):
    source_id: int

    path: str

    language: Optional[str]

    start_line: int
    end_line: int


class AskResponse(BaseModel):
    repo_name: str

    question: str

    answer: str

    sources: List[
        AnswerSource
    ]

    source_count: int

    model: str

    status: str