from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from models.history import (
    RepositoryHistoryClearResponse,
    RepositoryHistoryCreate,
    RepositoryHistoryDeleteResponse,
    RepositoryHistoryItem,
    RepositoryHistoryResponse,
)

from services.history_service import (
    clear_repository_history,
    delete_repository_history_item,
    get_repository_history,
    get_repository_history_item,
    save_repository_history,
)


router = APIRouter(
    prefix="/api/history",
    tags=["Repository History"],
)


@router.post(
    "",
    response_model=
        RepositoryHistoryItem,
)
async def save_history(
    request:
        RepositoryHistoryCreate,
):
    try:
        data = (
            save_repository_history(
                repo_url=
                    request.repo_url,

                repo_name=
                    request.repo_name,

                owner=
                    request.owner,

                description=
                    request.description,

                primary_language=
                    request.primary_language,

                primary_framework=
                    request.primary_framework,

                architecture=
                    request.architecture,

                default_branch=
                    request.default_branch,

                commit_sha=
                    request.commit_sha,
            )
        )

        return (
            RepositoryHistoryItem(
                **data
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save repository history: "
                f"{str(error)}"
            ),
        )


@router.get(
    "",
    response_model=
        RepositoryHistoryResponse,
)
async def list_history(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    try:
        repositories = (
            get_repository_history(
                limit=limit
            )
        )

        return (
            RepositoryHistoryResponse(
                repositories=
                    repositories,

                total=
                    len(
                        repositories
                    ),
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not load repository history: "
                f"{str(error)}"
            ),
        )


@router.get(
    "/repository",
    response_model=
        RepositoryHistoryItem,
)
async def get_history_item(
    repo_url: str,
):
    item = (
        get_repository_history_item(
            repo_url
        )
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail=(
                "Repository not found in history."
            ),
        )

    return (
        RepositoryHistoryItem(
            **item
        )
    )


@router.delete(
    "/repository",
    response_model=
        RepositoryHistoryDeleteResponse,
)
async def delete_history_item(
    repo_url: str,
):
    deleted = (
        delete_repository_history_item(
            repo_url
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=(
                "Repository not found in history."
            ),
        )

    return (
        RepositoryHistoryDeleteResponse(
            deleted=True,
            repo_url=repo_url,
            status=(
                "repository removed from history"
            ),
        )
    )


@router.delete(
    "",
    response_model=
        RepositoryHistoryClearResponse,
)
async def clear_history():
    deleted_count = (
        clear_repository_history()
    )

    return (
        RepositoryHistoryClearResponse(
            deleted_count=
                deleted_count,

            status=(
                "repository history cleared"
            ),
        )
    )