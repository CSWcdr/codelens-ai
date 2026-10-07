import asyncio

from collections import Counter

from typing import (
    Dict,
    List,
)


from services.architecture_service import (
    get_raw_file_content,
)


# =========================================================
# INSIGHTS CONFIGURATION
# =========================================================

LARGE_FILE_LINES = 250

VERY_LARGE_FILE_LINES = 400

HIGH_IMPORT_COUNT = 5

HIGH_IMPORTED_BY_COUNT = 4

FILE_FETCH_CONCURRENCY = 10


# =========================================================
# EDGE METRICS
# =========================================================

def build_edge_counts(
    edges: List[dict],
):
    outgoing = Counter()
    incoming = Counter()


    for edge in edges:

        # Only internal repository import relationships
        # should contribute to import metrics.
        if (
            edge.get(
                "relationship"
            )
            != "imports"
        ):
            continue


        source = edge.get(
            "source"
        )

        target = edge.get(
            "target"
        )


        if source:

            outgoing[
                source
            ] += 1


        if target:

            incoming[
                target
            ] += 1


    return (
        outgoing,
        incoming,
    )


# =========================================================
# FILE METRICS
# =========================================================

async def build_file_metrics(
    owner: str,
    repo_name: str,
    branch: str,
    nodes: List[dict],
    edges: List[dict],
):
    outgoing, incoming = (
        build_edge_counts(
            edges
        )
    )


    semaphore = (
        asyncio.Semaphore(
            FILE_FETCH_CONCURRENCY
        )
    )


    async def build_single_metric(
        node: dict,
    ):

        path = node[
            "path"
        ]


        async with semaphore:

            try:

                content = (
                    await get_raw_file_content(
                        owner,
                        repo_name,
                        branch,
                        path,
                    )
                )

            except Exception:

                content = None


        line_count = 0


        if content:

            line_count = len(
                content.splitlines()
            )


        return {
            "path":
                path,

            "language":
                node.get(
                    "language"
                ),

            "node_type":
                node.get(
                    "node_type",
                    "source",
                ),

            "layer":
                node.get(
                    "layer",
                    "shared",
                ),

            "lines":
                line_count,

            "imports":
                outgoing.get(
                    path,
                    0,
                ),

            "imported_by":
                incoming.get(
                    path,
                    0,
                ),
        }


    if not nodes:
        return []


    metrics = (
        await asyncio.gather(
            *[
                build_single_metric(
                    node
                )

                for node
                in nodes
            ]
        )
    )


    return list(
        metrics
    )


# =========================================================
# SUMMARY
# =========================================================

def build_summary(
    nodes: List[dict],
    edges: List[dict],
    external_dependencies: List[dict],
    external_api_calls: List[dict],
    data_connections: List[dict],
):
    node_types = Counter()

    frontend_files = 0
    backend_files = 0
    shared_files = 0


    for node in nodes:

        node_types[
            node.get(
                "node_type",
                "source",
            )
        ] += 1


        layer = node.get(
            "layer",
            "shared",
        )


        if layer == "frontend":

            frontend_files += 1


        elif layer == "backend":

            backend_files += 1


        else:

            shared_files += 1


    internal_imports = sum(
        1

        for edge
        in edges

        if (
            edge.get(
                "relationship"
            )
            == "imports"
        )
    )


    technologies = sorted(
        {
            item.get(
                "technology"
            )

            for item
            in data_connections

            if item.get(
                "technology"
            )
        }
    )


    return {
        # -------------------------------------------------
        # IMPORTANT:
        #
        # This is intentionally the number of files that
        # entered the architecture/source analyzer.
        #
        # It is NOT necessarily the total number of files
        # in the GitHub repository.
        # -------------------------------------------------

        "source_files":
            len(
                nodes
            ),

        "analyzed_source_files":
            len(
                nodes
            ),

        "file_metric_scope":
            "analyzed_source_files",

        "frontend_files":
            frontend_files,

        "backend_files":
            backend_files,

        "shared_files":
            shared_files,

        "total_imports":
            internal_imports,

        "external_dependencies":
            len(
                external_dependencies
            ),

        "external_api_calls":
            len(
                external_api_calls
            ),

        "data_connections":
            len(
                data_connections
            ),

        "data_technology_count":
            len(
                technologies
            ),

        "data_technologies":
            technologies,

        "node_types":
            dict(
                node_types
            ),
    }


# =========================================================
# ROUTE COVERAGE
# =========================================================

def build_route_coverage(
    frontend_requests: List[dict],
    backend_routes: List[dict],
    request_flows: List[dict],
):
    frontend_request_count = (
        len(
            frontend_requests
        )
    )


    backend_route_count = (
        len(
            backend_routes
        )
    )


    matched = sum(
        1

        for flow
        in request_flows

        if flow.get(
            "matched"
        )
    )


    # Protect against duplicate flow records producing
    # impossible values such as 18/17.
    matched = min(
        matched,
        frontend_request_count,
    )


    unmatched = max(
        frontend_request_count
        - matched,
        0,
    )


    # =====================================================
    # ZERO REQUEST CASE
    #
    # 0 / 0 should not be treated as 0% coverage,
    # 100% coverage, or "all requests matched".
    #
    # There was simply nothing to evaluate.
    # =====================================================

    if (
        frontend_request_count
        == 0
    ):

        coverage_percentage = None

        coverage_status = (
            "no_frontend_requests"
        )


    else:

        coverage_percentage = round(
            (
                matched
                /
                frontend_request_count
            )
            * 100,
            2,
        )


        if unmatched == 0:

            coverage_status = (
                "complete"
            )


        elif matched == 0:

            coverage_status = (
                "none"
            )


        else:

            coverage_status = (
                "partial"
            )


    return {
        "frontend_requests":
            frontend_request_count,

        "backend_routes":
            backend_route_count,

        "matched_requests":
            matched,

        "unmatched_requests":
            unmatched,

        "coverage_percentage":
            coverage_percentage,

        "coverage_status":
            coverage_status,
    }


# =========================================================
# LARGEST FILES
# =========================================================

def build_largest_files(
    metrics: List[dict],
    limit: int = 8,
):
    ranked = sorted(
        metrics,
        key=lambda item:
            item[
                "lines"
            ],
        reverse=True,
    )


    return ranked[
        :limit
    ]


# =========================================================
# MOST IMPORTED FILES
# =========================================================

def build_most_imported_files(
    metrics: List[dict],
    limit: int = 8,
):
    ranked = sorted(
        metrics,
        key=lambda item:
            item[
                "imported_by"
            ],
        reverse=True,
    )


    results = []


    for item in ranked:

        if (
            item[
                "imported_by"
            ]
            <= 0
        ):
            continue


        results.append(
            {
                "path":
                    item[
                        "path"
                    ],

                "reason":
                    (
                        "Referenced by multiple "
                        "repository source files."
                    ),

                "value":
                    item[
                        "imported_by"
                    ],

                "metric":
                    "imported_by",
            }
        )


        if (
            len(
                results
            )
            >= limit
        ):
            break


    return results


# =========================================================
# HIGHEST OUTGOING IMPORTS
# =========================================================

def build_highest_outgoing_imports(
    metrics: List[dict],
    limit: int = 8,
):
    ranked = sorted(
        metrics,
        key=lambda item:
            item[
                "imports"
            ],
        reverse=True,
    )


    results = []


    for item in ranked:

        if (
            item[
                "imports"
            ]
            <= 0
        ):
            continue


        results.append(
            {
                "path":
                    item[
                        "path"
                    ],

                "reason":
                    (
                        "Imports several internal "
                        "repository modules."
                    ),

                "value":
                    item[
                        "imports"
                    ],

                "metric":
                    "imports",
            }
        )


        if (
            len(
                results
            )
            >= limit
        ):
            break


    return results


# =========================================================
# FINDINGS
# =========================================================

def build_findings(
    metrics: List[dict],
    route_coverage: Dict,
    external_api_calls: List[dict],
    data_connections: List[dict],
):
    findings = []


    # =====================================================
    # FILE SIZE
    # =====================================================

    very_large_files = [
        item

        for item
        in metrics

        if (
            item[
                "lines"
            ]
            >=
            VERY_LARGE_FILE_LINES
        )
    ]


    large_files = [
        item

        for item
        in metrics

        if (
            LARGE_FILE_LINES
            <= item[
                "lines"
            ]
            <
            VERY_LARGE_FILE_LINES
        )
    ]


    if very_large_files:

        findings.append(
            {
                "category":
                    "maintainability",

                "title":
                    "Very large source files detected",

                "description":
                    (
                        "Some analyzed source files exceed "
                        f"{VERY_LARGE_FILE_LINES} lines. "
                        "Large files can contain several "
                        "responsibilities and may be worth "
                        "reviewing for decomposition."
                    ),

                "severity":
                    "high",

                "files": [
                    item[
                        "path"
                    ]

                    for item
                    in very_large_files
                ][:6],
            }
        )


    if large_files:

        findings.append(
            {
                "category":
                    "maintainability",

                "title":
                    "Large source files detected",

                "description":
                    (
                        "Some analyzed source files exceed "
                        f"{LARGE_FILE_LINES} lines. "
                        "These files may be useful candidates "
                        "for a maintainability review."
                    ),

                "severity":
                    "medium",

                "files": [
                    item[
                        "path"
                    ]

                    for item
                    in large_files
                ][:6],
            }
        )


    # =====================================================
    # COUPLING
    # =====================================================

    high_outgoing = [
        item

        for item
        in metrics

        if (
            item[
                "imports"
            ]
            >=
            HIGH_IMPORT_COUNT
        )
    ]


    if high_outgoing:

        findings.append(
            {
                "category":
                    "coupling",

                "title":
                    "High outgoing dependency files",

                "description":
                    (
                        "These files import many internal "
                        "repository modules and may act as "
                        "coordination points in the codebase."
                    ),

                "severity":
                    "medium",

                "files": [
                    item[
                        "path"
                    ]

                    for item
                    in high_outgoing
                ][:6],
            }
        )


    high_incoming = [
        item

        for item
        in metrics

        if (
            item[
                "imported_by"
            ]
            >=
            HIGH_IMPORTED_BY_COUNT
        )
    ]


    if high_incoming:

        findings.append(
            {
                "category":
                    "coupling",

                "title":
                    "Shared dependency hotspots",

                "description":
                    (
                        "These files are imported by many "
                        "other repository modules. Changes "
                        "to them may affect a broader part "
                        "of the codebase."
                    ),

                "severity":
                    "medium",

                "files": [
                    item[
                        "path"
                    ]

                    for item
                    in high_incoming
                ][:6],
            }
        )


    # =====================================================
    # REQUEST FLOW
    # =====================================================

    frontend_request_count = (
        route_coverage.get(
            "frontend_requests",
            0,
        )
    )


    unmatched_request_count = (
        route_coverage.get(
            "unmatched_requests",
            0,
        )
    )


    coverage_status = (
        route_coverage.get(
            "coverage_status"
        )
    )


    if (
        frontend_request_count
        == 0
    ):

        findings.append(
            {
                "category":
                    "request-flow",

                "title":
                    "No frontend API requests detected",

                "description":
                    (
                        "No frontend API requests were "
                        "detected, so frontend-to-backend "
                        "route coverage is not applicable "
                        "for this repository."
                    ),

                "severity":
                    "info",

                "files":
                    [],
            }
        )


    elif (
        unmatched_request_count
        > 0
    ):

        findings.append(
            {
                "category":
                    "request-flow",

                "title":
                    "Unmatched frontend requests",

                "description":
                    (
                        f"{unmatched_request_count} detected "
                        "frontend API request(s) could not "
                        "be matched to a backend route."
                    ),

                "severity":
                    "medium",

                "files":
                    [],
            }
        )


    elif (
        coverage_status
        == "complete"
    ):

        findings.append(
            {
                "category":
                    "request-flow",

                "title":
                    "Frontend requests map to backend routes",

                "description":
                    (
                        "All detected frontend API requests "
                        "were matched to backend routes."
                    ),

                "severity":
                    "info",

                "files":
                    [],
            }
        )


    # =====================================================
    # EXTERNAL APIs
    # =====================================================

    if external_api_calls:

        external_files = sorted(
            {
                item[
                    "file"
                ]

                for item
                in external_api_calls

                if item.get(
                    "file"
                )
            }
        )


        external_services = sorted(
            {
                item.get(
                    "service"
                )

                for item
                in external_api_calls

                if item.get(
                    "service"
                )
            }
        )


        if external_services:

            service_text = (
                ", ".join(
                    external_services
                )
            )

        else:

            service_text = (
                "external services"
            )


        findings.append(
            {
                "category":
                    "integration",

                "title":
                    "External service integrations detected",

                "description":
                    (
                        f"{len(external_api_calls)} external "
                        "API call(s) were detected. "
                        f"Services: {service_text}."
                    ),

                "severity":
                    "info",

                "files":
                    external_files[
                        :6
                    ],
            }
        )


    # =====================================================
    # DATA LAYER
    # =====================================================

    if data_connections:

        data_files = sorted(
            {
                item[
                    "file"
                ]

                for item
                in data_connections

                if item.get(
                    "file"
                )
            }
        )


        technologies = sorted(
            {
                item[
                    "technology"
                ]

                for item
                in data_connections

                if item.get(
                    "technology"
                )
            }
        )


        findings.append(
            {
                "category":
                    "data-layer",

                "title":
                    "Data technologies detected",

                "description":
                    (
                        "Detected data-layer technologies: "
                        +
                        ", ".join(
                            technologies
                        )
                        +
                        "."
                    ),

                "severity":
                    "info",

                "files":
                    data_files[
                        :6
                    ],
            }
        )


    return findings


# =========================================================
# MAIN INSIGHTS ANALYZER
# =========================================================

async def analyze_insights(
    owner: str,
    repo_name: str,
    branch: str,
    architecture_data: Dict,
):
    nodes = (
        architecture_data.get(
            "nodes",
            [],
        )
    )


    edges = (
        architecture_data.get(
            "edges",
            [],
        )
    )


    external_dependencies = (
        architecture_data.get(
            "external_dependencies",
            [],
        )
    )


    external_api_calls = (
        architecture_data.get(
            "external_api_calls",
            [],
        )
    )


    frontend_requests = (
        architecture_data.get(
            "frontend_requests",
            [],
        )
    )


    backend_routes = (
        architecture_data.get(
            "backend_routes",
            [],
        )
    )


    request_flows = (
        architecture_data.get(
            "request_flows",
            [],
        )
    )


    data_connections = (
        architecture_data.get(
            "data_connections",
            [],
        )
    )


    # =====================================================
    # FILE METRICS
    # =====================================================

    metrics = (
        await build_file_metrics(
            owner=
                owner,

            repo_name=
                repo_name,

            branch=
                branch,

            nodes=
                nodes,

            edges=
                edges,
        )
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    summary = (
        build_summary(
            nodes=
                nodes,

            edges=
                edges,

            external_dependencies=
                external_dependencies,

            external_api_calls=
                external_api_calls,

            data_connections=
                data_connections,
        )
    )


    # =====================================================
    # ROUTE COVERAGE
    # =====================================================

    route_coverage = (
        build_route_coverage(
            frontend_requests=
                frontend_requests,

            backend_routes=
                backend_routes,

            request_flows=
                request_flows,
        )
    )


    # =====================================================
    # RANKED FILE METRICS
    # =====================================================

    largest_files = (
        build_largest_files(
            metrics
        )
    )


    most_imported_files = (
        build_most_imported_files(
            metrics
        )
    )


    highest_outgoing_imports = (
        build_highest_outgoing_imports(
            metrics
        )
    )


    # =====================================================
    # FINDINGS
    # =====================================================

    findings = (
        build_findings(
            metrics=
                metrics,

            route_coverage=
                route_coverage,

            external_api_calls=
                external_api_calls,

            data_connections=
                data_connections,
        )
    )


    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "summary":
            summary,

        "route_coverage":
            route_coverage,

        "largest_files":
            largest_files,

        "most_imported_files":
            most_imported_files,

        "highest_outgoing_imports":
            highest_outgoing_imports,

        "findings":
            findings,

        "insights_version":
            "2.3",
    }