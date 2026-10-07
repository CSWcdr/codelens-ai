from typing import (
    List,
    Optional,
)

from pydantic import BaseModel


class ArchitectureRequest(
    BaseModel
):
    repo_url: str


class ArchitectureNode(
    BaseModel
):
    id: str

    label: str

    path: str

    node_type: str

    language: Optional[str] = None

    layer: str


class ArchitectureEdge(
    BaseModel
):
    source: str

    target: str

    relationship: str


class ExternalDependency(
    BaseModel
):
    name: str

    used_by: List[str]


class ApiRequest(
    BaseModel
):
    file: str

    method: str

    endpoint: str


class ExternalApiCall(
    BaseModel
):
    file: str

    method: str

    endpoint: str

    service: str

    handler: Optional[str] = None


class BackendRoute(
    BaseModel
):
    file: str

    method: str

    endpoint: str

    framework: str

    handler: Optional[str] = None

    controller_file: Optional[str] = None


class RequestFlow(
    BaseModel
):
    frontend_file: str

    backend_file: Optional[str] = None

    controller_file: Optional[str] = None

    method: str

    endpoint: str

    handler: Optional[str] = None

    matched: bool


class DataConnection(
    BaseModel
):
    file: str

    technology: str

    connection_type: Optional[str] = None


class EndToEndFlow(
    BaseModel
):
    frontend_file: str

    method: str

    endpoint: str

    route_file: str

    controller_file: Optional[str] = None

    handler: Optional[str] = None

    external_services: List[str] = []

    data_technologies: List[str] = []


class ArchitectureResponse(
    BaseModel
):
    repo_name: str

    owner: str

    architecture: str

    nodes: List[
        ArchitectureNode
    ]

    edges: List[
        ArchitectureEdge
    ]

    external_dependencies: List[
        ExternalDependency
    ]

    frontend_requests: List[
        ApiRequest
    ]

    external_api_calls: List[
        ExternalApiCall
    ]

    backend_routes: List[
        BackendRoute
    ]

    request_flows: List[
        RequestFlow
    ]

    data_connections: List[
        DataConnection
    ]

    end_to_end_flows: List[
        EndToEndFlow
    ]

    node_count: int

    edge_count: int

    cached: bool = False

    commit_sha: Optional[str] = None

    status: str