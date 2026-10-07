import httpx


from fastapi import (
    APIRouter,
    HTTPException,
)


from models.insights import (
    InsightsRequest,
    InsightsResponse,
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


from services.insights_service import (
    analyze_insights,
)


router = APIRouter(
    prefix="/api/insights",
    tags=["Engineering Insights"],
)


@router.post(
    "/analyze",
    response_model=
        InsightsResponse,
)
async def analyze_repository_insights(
    request:
        InsightsRequest,
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
            metadata.get(
                "default_branch"
            )
            or "main"
        )


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
        # INSIGHTS CACHE HIT
        # =================================================

        cached_insights = (
            get_cached_analysis(
                owner=
                    owner,

                repo_name=
                    repo_name,

                analysis_type=
                    "insights",

                commit_sha=
                    commit_sha,
            )
        )


        if cached_insights:

            return (
                InsightsResponse(
                    repo_name=
                        metadata[
                            "repo_name"
                        ],

                    owner=
                        metadata[
                            "owner"
                        ],

                    architecture=
                        cached_insights[
                            "architecture"
                        ],

                    summary=
                        cached_insights[
                            "summary"
                        ],

                    route_coverage=
                        cached_insights[
                            "route_coverage"
                        ],

                    largest_files=
                        cached_insights[
                            "largest_files"
                        ],

                    most_imported_files=
                        cached_insights[
                            "most_imported_files"
                        ],

                    highest_outgoing_imports=
                        cached_insights[
                            "highest_outgoing_imports"
                        ],

                    findings=
                        cached_insights[
                            "findings"
                        ],

                    cached=
                        True,

                    commit_sha=
                        commit_sha,

                    status=
                        "insights cache current",
                )
            )


        # =================================================
        # TRY ARCHITECTURE CACHE
        # =================================================

        cached_architecture = (
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


        if cached_architecture:

            architecture_type = (
                cached_architecture[
                    "architecture"
                ]
            )


            architecture_data = {
                "nodes":
                    cached_architecture.get(
                        "nodes",
                        [],
                    ),

                "edges":
                    cached_architecture.get(
                        "edges",
                        [],
                    ),

                "external_dependencies":
                    cached_architecture.get(
                        "external_dependencies",
                        [],
                    ),

                "frontend_requests":
                    cached_architecture.get(
                        "frontend_requests",
                        [],
                    ),

                "external_api_calls":
                    cached_architecture.get(
                        "external_api_calls",
                        [],
                    ),

                "backend_routes":
                    cached_architecture.get(
                        "backend_routes",
                        [],
                    ),

                "request_flows":
                    cached_architecture.get(
                        "request_flows",
                        [],
                    ),

                "data_connections":
                    cached_architecture.get(
                        "data_connections",
                        [],
                    ),

                "end_to_end_flows":
                    cached_architecture.get(
                        "end_to_end_flows",
                        [],
                    ),

                "node_count":
                    cached_architecture.get(
                        "node_count",
                        0,
                    ),

                "edge_count":
                    cached_architecture.get(
                        "edge_count",
                        0,
                    ),
            }


        else:

            # =============================================
            # NO ARCHITECTURE CACHE
            # =============================================

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


            architecture_cache_data = {
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
                    architecture_cache_data,
            )


        # =================================================
        # INSIGHTS ANALYSIS
        # =================================================

        insights = (
            await analyze_insights(
                owner=
                    owner,

                repo_name=
                    repo_name,

                branch=
                    branch,

                architecture_data=
                    architecture_data,
            )
        )


        insights_cache_data = {
            "architecture":
                architecture_type,

            "summary":
                insights[
                    "summary"
                ],

            "route_coverage":
                insights[
                    "route_coverage"
                ],

            "largest_files":
                insights[
                    "largest_files"
                ],

            "most_imported_files":
                insights[
                    "most_imported_files"
                ],

            "highest_outgoing_imports":
                insights[
                    "highest_outgoing_imports"
                ],

            "findings":
                insights[
                    "findings"
                ],
        }


        save_cached_analysis(
            owner=
                owner,

            repo_name=
                repo_name,

            analysis_type=
                "insights",

            commit_sha=
                commit_sha,

            data=
                insights_cache_data,
        )


        return (
            InsightsResponse(
                repo_name=
                    metadata[
                        "repo_name"
                    ],

                owner=
                    metadata[
                        "owner"
                    ],

                architecture=
                    architecture_type,

                summary=
                    insights[
                        "summary"
                    ],

                route_coverage=
                    insights[
                        "route_coverage"
                    ],

                largest_files=
                    insights[
                        "largest_files"
                    ],

                most_imported_files=
                    insights[
                        "most_imported_files"
                    ],

                highest_outgoing_imports=
                    insights[
                        "highest_outgoing_imports"
                    ],

                findings=
                    insights[
                        "findings"
                    ],

                cached=
                    False,

                commit_sha=
                    commit_sha,

                status=
                    "insights analysis complete",
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
                "Insights analysis failed "
                "because of an unexpected "
                "server error."
            ),
        )
