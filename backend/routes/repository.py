import httpx


from fastapi import (
    APIRouter,
    HTTPException,
)


from models.repository import (
    RepositoryOverview,
    RepositoryRequest,
    RepositoryResponse,
)


from services.github_service import (
    GitHubServiceError,
    count_directories,
    count_files,
    count_root_modules,
    detect_architecture,
    detect_build_tool,
    detect_dependencies,
    detect_framework,
    filter_repository_tree,
    get_language_percentages,
    get_repository_metadata,
    get_repository_tree,
    get_root_modules,
    parse_github_url,
)


from services.overview_service import (
    build_repository_overview,
)


router = APIRouter(
    prefix="/api/repository",
    tags=["Repository"],
)


@router.post(
    "/analyze",
    response_model=
        RepositoryResponse,
)
async def analyze_repository(
    request:
        RepositoryRequest,
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


        default_branch = (
            metadata.get(
                "default_branch"
            )
            or "main"
        )


        raw_tree = (
            await get_repository_tree(
                owner,
                repo_name,
                default_branch,
            )
        )


        if not raw_tree:

            raise HTTPException(
                status_code=422,
                detail=(
                    "The repository does not contain "
                    "an analyzable file tree."
                ),
            )


        clean_tree = (
            filter_repository_tree(
                raw_tree
            )
        )


        if not clean_tree:

            raise HTTPException(
                status_code=422,
                detail=(
                    "No analyzable repository files "
                    "were found after filtering."
                ),
            )


        languages = (
            await get_language_percentages(
                owner,
                repo_name,
            )
        )


        dependencies = (
            await detect_dependencies(
                owner,
                repo_name,
                clean_tree,
            )
        )


        total_files = (
            count_files(
                clean_tree
            )
        )


        total_folders = (
            count_directories(
                clean_tree
            )
        )


        total_modules = (
            count_root_modules(
                clean_tree
            )
        )


        modules = (
            get_root_modules(
                clean_tree
            )
        )


        primary_language = None


        if languages:

            primary_language = (
                max(
                    languages,
                    key=
                        languages.get,
                )
            )


        primary_framework = (
            detect_framework(
                dependencies
            )
        )


        build_tool = (
            detect_build_tool(
                dependencies
            )
        )


        architecture = (
            detect_architecture(
                clean_tree
            )
        )


        overview_data = (
            build_repository_overview(
                repo_name=
                    metadata[
                        "repo_name"
                    ],

                description=
                    metadata[
                        "description"
                    ],

                primary_language=
                    primary_language,

                primary_framework=
                    primary_framework,

                build_tool=
                    build_tool,

                architecture=
                    architecture,

                modules=
                    modules,

                dependencies=
                    dependencies,

                total_files=
                    total_files,

                tree=
                    clean_tree,
            )
        )


        return (
            RepositoryResponse(
                repo_url=
                    request.repo_url,

                repo_name=
                    metadata[
                        "repo_name"
                    ],

                owner=
                    metadata[
                        "owner"
                    ],

                description=
                    metadata[
                        "description"
                    ],

                default_branch=
                    default_branch,

                primary_language=
                    primary_language,

                languages=
                    languages,

                stars=
                    metadata[
                        "stars"
                    ],

                forks=
                    metadata[
                        "forks"
                    ],

                open_issues=
                    metadata[
                        "open_issues"
                    ],

                visibility=
                    metadata[
                        "visibility"
                    ],

                is_private=
                    metadata[
                        "is_private"
                    ],

                github_url=
                    metadata[
                        "github_url"
                    ],

                total_files=
                    total_files,

                total_folders=
                    total_folders,

                total_modules=
                    total_modules,

                modules=
                    modules,

                dependencies=
                    dependencies,

                dependency_count=
                    len(
                        dependencies
                    ),

                primary_framework=
                    primary_framework,

                build_tool=
                    build_tool,

                architecture=
                    architecture,

                overview=
                    RepositoryOverview(
                        summary=
                            overview_data[
                                "summary"
                            ],

                        highlights=
                            overview_data[
                                "highlights"
                            ],
                    ),

                status=
                    "analysis complete",
            )
        )


    except GitHubServiceError as error:

        headers = None


        if error.retry_after:

            headers = {
                "Retry-After":
                    error.retry_after
            }


        raise HTTPException(
            status_code=
                error.status_code,

            detail=
                error.detail,

            headers=
                headers,
        )


    except HTTPException:

        raise


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )


    except httpx.TimeoutException:

        raise HTTPException(
            status_code=504,
            detail=(
                "A remote service took too long "
                "to respond. Please try again."
            ),
        )


    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail=(
                "A required external service "
                "could not be reached."
            ),
        )


    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Repository analysis failed "
                "because of an unexpected "
                "server error."
            ),
        )