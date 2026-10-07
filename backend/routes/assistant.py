from fastapi import (
    APIRouter,
    HTTPException,
)

from models.assistant import (
    AnswerSource,
    AskRequest,
    AskResponse,
    RepositoryIndexRequest,
    RepositoryIndexResponse,
    RepositoryIndexStatusResponse,
    RetrievalRequest,
    RetrievalResponse,
)

from services.github_service import (
    filter_repository_tree,
    get_repository_metadata,
    get_repository_tree,
    parse_github_url,
)

from services.llm_service import (
    generate_grounded_answer,
)

from services.rag_service import (
    check_repository_index_freshness,
    index_repository,
    retrieve_repository_context,
)


router = APIRouter(
    prefix="/api/assistant",
    tags=["AI Assistant"],
)


# =========================================================
# INDEX STATUS
# =========================================================

@router.post(
    "/status",
    response_model=
        RepositoryIndexStatusResponse,
)
async def repository_index_status(
    request:
        RepositoryIndexRequest,
):
    try:
        owner, repo_name = (
            parse_github_url(
                request.repo_url
            )
        )


        metadata = (
            await get_repository_metadata(
                owner,
                repo_name,
            )
        )


        branch = (
            metadata[
                "default_branch"
            ]
            or "main"
        )


        freshness = (
            await check_repository_index_freshness(
                owner=
                    owner,

                repo_name=
                    repo_name,

                branch=
                    branch,
            )
        )


        indexed = (
            freshness[
                "indexed"
            ]
        )


        fresh = (
            freshness[
                "fresh"
            ]
        )


        if (
            indexed
            and
            fresh
        ):
            status = (
                "repository index current"
            )

        elif indexed:
            status = (
                "repository index stale"
            )

        else:
            status = (
                "repository not indexed"
            )


        return (
            RepositoryIndexStatusResponse(
                repo_name=
                    repo_name,

                owner=
                    owner,

                indexed=
                    indexed,

                fresh=
                    fresh,

                indexed_chunks=
                    freshness[
                        "indexed_chunks"
                    ],

                commit_sha=
                    freshness[
                        "commit_sha"
                    ],

                stored_commit_sha=
                    freshness[
                        "stored_commit_sha"
                    ],

                status=
                    status,
            )
        )


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not check repository index: "
                f"{str(error)}"
            ),
        )


# =========================================================
# INDEX REPOSITORY
# =========================================================

@router.post(
    "/index",
    response_model=
        RepositoryIndexResponse,
)
async def index_repository_route(
    request:
        RepositoryIndexRequest,
):
    try:
        owner, repo_name = (
            parse_github_url(
                request.repo_url
            )
        )


        metadata = (
            await get_repository_metadata(
                owner,
                repo_name,
            )
        )


        branch = (
            metadata[
                "default_branch"
            ]
            or "main"
        )


        raw_tree = (
            await get_repository_tree(
                owner,
                repo_name,
                branch,
            )
        )


        clean_tree = (
            filter_repository_tree(
                raw_tree
            )
        )


        result = (
            await index_repository(
                owner=
                    owner,

                repo_name=
                    repo_name,

                branch=
                    branch,

                tree=
                    clean_tree,
            )
        )


        return (
            RepositoryIndexResponse(
                repo_name=
                    metadata[
                        "repo_name"
                    ],

                owner=
                    metadata[
                        "owner"
                    ],

                collection_name=
                    result[
                        "collection_name"
                    ],

                indexed_files=
                    result[
                        "indexed_files"
                    ],

                indexed_chunks=
                    result[
                        "indexed_chunks"
                    ],

                files=
                    result[
                        "files"
                    ],

                cached=
                    result.get(
                        "cached",
                        False,
                    ),

                commit_sha=
                    result.get(
                        "commit_sha"
                    ),

                status=
                    result.get(
                        "status",
                        "repository indexed",
                    ),
            )
        )


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Repository indexing failed: "
                f"{str(error)}"
            ),
        )


# =========================================================
# RETRIEVAL
# =========================================================

@router.post(
    "/retrieve",
    response_model=
        RetrievalResponse,
)
async def retrieve_repository_route(
    request:
        RetrievalRequest,
):
    try:
        owner, repo_name = (
            parse_github_url(
                request.repo_url
            )
        )


        results = (
            retrieve_repository_context(
                owner=
                    owner,

                repo_name=
                    repo_name,

                question=
                    request.question,

                limit=
                    request.limit,
            )
        )


        return RetrievalResponse(
            repo_name=
                repo_name,

            question=
                request.question,

            results=
                results,

            result_count=
                len(
                    results
                ),

            status=
                "context retrieved",
        )


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Repository retrieval failed: "
                f"{str(error)}"
            ),
        )


# =========================================================
# ASK
# =========================================================

@router.post(
    "/ask",
    response_model=
        AskResponse,
)
async def ask_repository_route(
    request:
        AskRequest,
):
    try:
        owner, repo_name = (
            parse_github_url(
                request.repo_url
            )
        )


        chunks = (
            retrieve_repository_context(
                owner=
                    owner,

                repo_name=
                    repo_name,

                question=
                    request.question,

                limit=
                    request.limit,
            )
        )


        if not chunks:
            raise ValueError(
                "No relevant repository context was found."
            )


        generation = (
            await generate_grounded_answer(
                repository_name=
                    repo_name,

                question=
                    request.question,

                chunks=
                    chunks,
            )
        )


        sources = []


        for index, chunk in (
            enumerate(
                chunks,
                start=1,
            )
        ):
            sources.append(
                AnswerSource(
                    source_id=
                        index,

                    path=
                        chunk[
                            "path"
                        ],

                    language=
                        chunk.get(
                            "language"
                        ),

                    start_line=
                        chunk[
                            "start_line"
                        ],

                    end_line=
                        chunk[
                            "end_line"
                        ],
                )
            )


        return AskResponse(
            repo_name=
                repo_name,

            question=
                request.question,

            answer=
                generation[
                    "answer"
                ],

            sources=
                sources,

            source_count=
                len(
                    sources
                ),

            model=
                generation[
                    "model"
                ],

            status=
                "answer generated",
        )


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Assistant request failed: "
                f"{str(error)}"
            ),
        )