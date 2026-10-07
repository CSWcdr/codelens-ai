from typing import (
    Dict,
    List,
    Optional,
)

from pydantic import BaseModel


class InsightsRequest(
    BaseModel
):
    repo_url: str


class FileMetric(
    BaseModel
):
    path: str

    language: Optional[
        str
    ] = None

    node_type: str

    layer: str

    lines: int

    imports: int

    imported_by: int


class Hotspot(
    BaseModel
):
    path: str

    reason: str

    value: int

    metric: str


class InsightFinding(
    BaseModel
):
    category: str

    title: str

    description: str

    severity: str

    files: List[
        str
    ]


class RouteCoverage(
    BaseModel
):
    frontend_requests: int

    backend_routes: int

    matched_requests: int

    unmatched_requests: int

    coverage_percentage: Optional[
        float
    ] = None

    coverage_status: str


class InsightsSummary(
    BaseModel
):
    # Number of files analyzed by the
    # architecture/source analyzer.
    source_files: int

    analyzed_source_files: int

    file_metric_scope: str

    frontend_files: int

    backend_files: int

    shared_files: int

    total_imports: int

    external_dependencies: int

    external_api_calls: int

    data_connections: int

    data_technology_count: int

    data_technologies: List[
        str
    ]

    node_types: Dict[
        str,
        int,
    ]


class InsightsResponse(
    BaseModel
):
    repo_name: str

    owner: str

    architecture: str

    summary: InsightsSummary

    route_coverage: RouteCoverage

    largest_files: List[
        FileMetric
    ]

    most_imported_files: List[
        Hotspot
    ]

    highest_outgoing_imports: List[
        Hotspot
    ]

    findings: List[
        InsightFinding
    ]

    cached: bool = False

    commit_sha: Optional[
        str
    ] = None

    status: str