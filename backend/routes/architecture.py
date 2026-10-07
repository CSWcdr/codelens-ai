import httpx


from fastapi import (
    APIRouter,
    HTTPException,
)


from models.architecture import (
    ArchitectureRequest,
    ArchitectureResponse,
)


from services.analysis_cache_service import (
    get_cached_analysis,
    get_repository_commit_sha,
    save_cached_analysis,
)


from services.architecture_service import (
    analyze_architecture,
)


from services.github_service import (
    GitHubServiceError,
    detect_architecture,
    filter_repository_tree,
    get_repository_metadata,
    get_repository_tree,
    parse_github_url,
)


router = APIRouter(
    prefix="/api/architecture",
    tags=["Architecture"],
)


@router.post(
    "/analyze",
    response_model=
        ArchitectureResponse,
)
async def analyze_repository_architecture(
    request:
        ArchitectureRequest,
):
    try:

        # =================================================
        # VALIDATE REPOSITORY URL
        # =================================================

        owner, repo_name = (
            parse_github_url(
                request.repo_url
            )
        )


        # =================================================
        # REPOSITORY METADATA
        # =================================================

        metadata = (
            await get_repository_metadata(
                owner,
                repo_name,
            )
        )


        branch = (
            metadata.get(
                "default_branch"
            )
            or "main"
        )


        # =================================================
        # CURRENT COMMIT
        # =================================================

        commit_sha = (
            await get_repository_commit_sha(
                owner=
                    owner,

                repo_name=
                    repo_name,

                branch=
                    branch,
            )
        )


        # =================================================
        # CACHE HIT
        # =================================================

        cached_data = (
            get_cached_analysis(
                owner=
                    owner,

                repo_name=
                    repo_name,

                analysis_type=
                    "architecture",

                commit_sha=
                    commit_sha,
            )
        )


        if cached_data:

            return (
                ArchitectureResponse(
                    repo_name=
                        metadata[
                            "repo_name"
                        ],

                    owner=
                        metadata[
                            "owner"
                        ],

                    architecture=
                        cached_data[
                            "architecture"
                        ],

                    nodes=
                        cached_data[
                            "nodes"
                        ],

                    edges=
                        cached_data[
                            "edges"
                        ],

                    external_dependencies=
                        cached_data[
                            "external_dependencies"
                        ],

                    frontend_requests=
                        cached_data[
                            "frontend_requests"
                        ],

                    external_api_calls=
                        cached_data[
                            "external_api_calls"
                        ],

                    backend_routes=
                        cached_data[
                            "backend_routes"
                        ],

                    request_flows=
                        cached_data[
                            "request_flows"
                        ],

                    data_connections=
                        cached_data[
                            "data_connections"
                        ],

                    end_to_end_flows=
                        cached_data[
                            "end_to_end_flows"
                        ],

                    node_count=
                        cached_data[
                            "node_count"
                        ],

                    edge_count=
                        cached_data[
                            "edge_count"
                        ],

                    cached=
                        True,

                    commit_sha=
                        commit_sha,

                    status=
                        "architecture cache current",
                )
            )


        # =================================================
        # CACHE MISS
        # =================================================

        raw_tree = (
            await get_repository_tree(
                owner,
                repo_name,
                branch,
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


        architecture_type = (
            detect_architecture(
                clean_tree
            )
        )


        # =================================================
        # ARCHITECTURE ANALYSIS
        # =================================================

        architecture_data = (
            await analyze_architecture(
                owner=
                    owner,

                repo_name=
                    repo_name,

                branch=
                    branch,

                tree=
                    clean_tree,

                architecture=
                    architecture_type,
            )
        )


        response_data = {
            "architecture":
                architecture_type,

            "nodes":
                architecture_data.get(
                    "nodes",
                    [],
                ),

            "edges":
                architecture_data.get(
                    "edges",
                    [],
                ),

            "external_dependencies":
                architecture_data.get(
                    "external_dependencies",
                    [],
                ),

            "frontend_requests":
                architecture_data.get(
                    "frontend_requests",
                    [],
                ),

            "external_api_calls":
                architecture_data.get(
                    "external_api_calls",
                    [],
                ),

            "backend_routes":
                architecture_data.get(
                    "backend_routes",
                    [],
                ),

            "request_flows":
                architecture_data.get(
                    "request_flows",
                    [],
                ),

            "data_connections":
                architecture_data.get(
                    "data_connections",
                    [],
                ),

            "end_to_end_flows":
                architecture_data.get(
                    "end_to_end_flows",
                    [],
                ),

            "node_count":
                architecture_data.get(
                    "node_count",
                    len(
                        architecture_data.get(
                            "nodes",
                            [],
                        )
                    ),
                ),

            "edge_count":
                architecture_data.get(
                    "edge_count",
                    len(
                        architecture_data.get(
                            "edges",
                            [],
                        )
                    ),
                ),
        }


        # =================================================
        # SAVE CACHE
        # =================================================

        save_cached_analysis(
            owner=
                owner,

            repo_name=
                repo_name,

            analysis_type=
                "architecture",

            commit_sha=
                commit_sha,

            data=
                response_data,
        )


        # =================================================
        # RESPONSE
        # =================================================

        return (
            ArchitectureResponse(
                repo_name=
                    metadata[
                        "repo_name"
                    ],

                owner=
                    metadata[
                        "owner"
                    ],

                **response_data,

                cached=
                    False,

                commit_sha=
                    commit_sha,

                status=
                    "architecture analysis complete",
            )
        )


    # =====================================================
    # GITHUB-SPECIFIC FAILURE
    # =====================================================

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


    # =====================================================
    # EXISTING FASTAPI ERROR
    # =====================================================

    except HTTPException:

        raise


    # =====================================================
    # INVALID USER INPUT
    # =====================================================

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )


    # =====================================================
    # NETWORK TIMEOUT
    # =====================================================

    except httpx.TimeoutException:

        raise HTTPException(
            status_code=504,
            detail=(
                "A remote service took too long "
                "to respond. Please try again."
            ),
        )


    # =====================================================
    # NETWORK FAILURE
    # =====================================================

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail=(
                "A required external service "
                "could not be reached."
            ),
        )


    # =====================================================
    # UNKNOWN SERVER ERROR
    # =====================================================

    except Exception:

        # Do NOT expose raw Python errors to the browser.
        raise HTTPException(
            status_code=500,
            detail=(
                "Architecture analysis failed "
                "because of an unexpected "
                "server error."
            ),
        )