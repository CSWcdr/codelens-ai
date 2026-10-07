import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  Boxes,
  Braces,
  CheckCircle2,
  Cloud,
  Code2,
  Database,
  FileCode2,
  GitBranch,
  Network,
  Package,
  RefreshCw,
  Route,
  ServerCog,
  Settings2,
  ShieldCheck,
} from "lucide-react";

import AppLayout from "../components/AppLayout";

import {
  useRepo,
} from "../context/RepoContext";

import {
  analyzeArchitectureApi,
} from "../services/api";

import "../styles/architecture.css";


const NODE_BUILT_INS = new Set([
  "fs",
  "path",
  "http",
  "https",
  "url",
  "crypto",
  "stream",
  "util",
  "events",
  "buffer",
  "os",
]);


const CONFIG_DEPENDENCIES = new Set([
  "eslint",
  "@eslint/js",
  "eslint-plugin-react-hooks",
  "eslint-plugin-react-refresh",
  "globals",
  "vite",
  "@vitejs/plugin-react",
  "@tailwindcss/vite",
]);


function Architecture() {
  const [
    activeTab,
    setActiveTab,
  ] = useState("component");

  const [
    architectureData,
    setArchitectureData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const {
    repoName,
    repoUrl,
  } = useRepo();

  const displayedName =
    repoName || "Repository";


  const loadArchitecture =
    async () => {
      if (!repoUrl) {
        setLoading(false);

        setError(
          "No repository is currently selected."
        );

        return;
      }

      setLoading(true);
      setError("");

      try {
        const data =
          await analyzeArchitectureApi(
            repoUrl
          );

        setArchitectureData(
          data
        );
      } catch (requestError) {
        let message =
          "Could not analyze repository architecture.";

        if (
          requestError.response?.data
            ?.detail
        ) {
          message =
            requestError.response.data.detail;
        } else if (
          requestError.code ===
          "ECONNABORTED"
        ) {
          message =
            "Architecture analysis timed out.";
        } else if (
          requestError.message ===
          "Network Error"
        ) {
          message =
            "Could not connect to the CodeLens AI backend.";
        }

        setError(
          message
        );
      } finally {
        setLoading(
          false
        );
      }
    };


  useEffect(() => {
    loadArchitecture();
  }, [repoUrl]);


  return (
    <AppLayout>
      <div className="arch-page">

        <section className="arch-header">
          <div>
            <p className="small-label">
              CODEBASE ARCHITECTURE
            </p>

            <h1>
              Architecture Visualization
            </h1>

            <p className="arch-subtitle">
              Explore source relationships,
              request lifecycles, backend
              controllers, external services,
              databases, and dependencies
              across{" "}
              <strong>
                {displayedName}
              </strong>
              .
            </p>
          </div>


          <div
            className={`arch-generated ${
              loading
                ? "loading"
                : error
                ? "error"
                : "ready"
            }`}
          >
            {loading ? (
              <>
                <RefreshCw
                  size={15}
                  className="arch-spin"
                />

                Analyzing
              </>
            ) : error ? (
              <>
                <AlertTriangle
                  size={15}
                />

                Analysis Failed
              </>
            ) : (
              <>
                <CheckCircle2
                  size={15}
                />

                Live Analysis
              </>
            )}
          </div>
        </section>


        {loading && (
          <ArchitectureLoading
            repoName={
              displayedName
            }
          />
        )}


        {!loading &&
          error && (
            <ArchitectureError
              message={error}
              onRetry={
                loadArchitecture
              }
            />
          )}


        {!loading &&
          !error &&
          architectureData && (
            <>
              <div className="arch-tabs">

                <button
                  className={
                    activeTab ===
                    "component"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setActiveTab(
                      "component"
                    )
                  }
                >
                  Component Graph
                </button>

                <button
                  className={
                    activeTab ===
                    "request"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setActiveTab(
                      "request"
                    )
                  }
                >
                  Request Flow
                </button>

                <button
                  className={
                    activeTab ===
                    "data"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setActiveTab(
                      "data"
                    )
                  }
                >
                  Data Flow
                </button>

                <button
                  className={
                    activeTab ===
                    "dependencies"
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setActiveTab(
                      "dependencies"
                    )
                  }
                >
                  Dependencies
                </button>
              </div>


              {activeTab ===
                "component" && (
                <ComponentGraph
                  repoName={
                    displayedName
                  }
                  data={
                    architectureData
                  }
                />
              )}


              {activeTab ===
                "request" && (
                <RequestFlow
                  data={
                    architectureData
                  }
                />
              )}


              {activeTab ===
                "data" && (
                <DataFlow
                  data={
                    architectureData
                  }
                />
              )}


              {activeTab ===
                "dependencies" && (
                <Dependencies
                  repoName={
                    displayedName
                  }
                  data={
                    architectureData
                  }
                />
              )}
            </>
          )}
      </div>
    </AppLayout>
  );
}


function ArchitectureLoading({
  repoName,
}) {
  return (
    <section className="arch-loading-panel">

      <div className="arch-loading-icon">
        <RefreshCw
          size={24}
          className="arch-spin"
        />
      </div>

      <div>
        <h2>
          Analyzing architecture
        </h2>

        <p>
          Inspecting imports,
          routes, controllers,
          services, and data
          relationships inside{" "}
          <strong>
            {repoName}
          </strong>
          .
        </p>
      </div>
    </section>
  );
}


function ArchitectureError({
  message,
  onRetry,
}) {
  return (
    <section className="arch-error-panel">

      <div className="arch-error-icon">
        <AlertTriangle
          size={22}
        />
      </div>

      <div className="arch-error-copy">
        <h2>
          Architecture analysis failed
        </h2>

        <p>
          {message}
        </p>
      </div>

      <button
        type="button"
        onClick={onRetry}
      >
        <RefreshCw
          size={14}
        />

        Try Again
      </button>
    </section>
  );
}


function ComponentGraph({
  repoName,
  data,
}) {
  const allNodes =
    data.nodes || [];

  const edges =
    data.edges || [];


  const visibleNodes =
    useMemo(
      () =>
        allNodes.filter(
          (node) =>
            node.node_type !==
              "configuration" &&
            !isTestFile(
              node.path
            )
        ),
      [allNodes]
    );


  const initialNode =
    visibleNodes.find(
      (node) =>
        node.label ===
        "App.jsx"
    ) ||
    visibleNodes.find(
      (node) =>
        node.label ===
        "main.jsx"
    ) ||
    visibleNodes.find(
      (node) =>
        node.node_type ===
        "entry"
    ) ||
    visibleNodes[0] ||
    null;


  const [
    selectedNodeId,
    setSelectedNodeId,
  ] = useState(
    initialNode?.id || ""
  );


  useEffect(() => {
    const preferred =
      visibleNodes.find(
        (node) =>
          node.label ===
          "App.jsx"
      ) ||
      visibleNodes.find(
        (node) =>
          node.label ===
          "main.jsx"
      ) ||
      visibleNodes.find(
        (node) =>
          node.node_type ===
          "entry"
      ) ||
      visibleNodes[0];

    if (
      preferred &&
      !visibleNodes.some(
        (node) =>
          node.id ===
          selectedNodeId
      )
    ) {
      setSelectedNodeId(
        preferred.id
      );
    }
  }, [
    visibleNodes,
    selectedNodeId,
  ]);


  const selectedNode =
    visibleNodes.find(
      (node) =>
        node.id ===
        selectedNodeId
    ) ||
    initialNode;


  const incomingEdges =
    edges.filter(
      (edge) =>
        edge.target ===
        selectedNode?.id
    );


  const outgoingEdges =
    edges.filter(
      (edge) =>
        edge.source ===
        selectedNode?.id
    );


  const getNode = (
    id
  ) =>
    allNodes.find(
      (node) =>
        node.id === id
    );


  const nodeTypes =
    new Set(
      visibleNodes.map(
        (node) =>
          node.node_type
      )
    ).size;


  const hiddenCount =
    allNodes.length -
    visibleNodes.length;


  return (
    <section className="arch-grid">

      <div className="arch-canvas-card">

        <div className="canvas-toolbar">
          <div>
            <span className="toolbar-dot"></span>

            Repository relationship graph
          </div>

          <span>
            {visibleNodes.length} architecture files
            {" · "}
            {data.edge_count} imports
          </span>
        </div>


        <div className="component-graph-layout">

          {selectedNode && (
            <div className="relationship-explorer">

              <RelationshipColumn
                title="Imported By"
                nodes={
                  incomingEdges
                    .map(
                      (edge) =>
                        getNode(
                          edge.source
                        )
                    )
                    .filter(Boolean)
                }
                onSelect={
                  setSelectedNodeId
                }
              />


              <div className="relationship-center">

                <div className="relation-line-top">
                  <ArrowRight
                    size={16}
                  />
                </div>

                <button
                  type="button"
                  className="central-node"
                  onClick={() =>
                    setSelectedNodeId(
                      selectedNode.id
                    )
                  }
                >
                  <div className="central-node-icon">
                    <NodeIcon
                      type={
                        selectedNode.node_type
                      }
                    />
                  </div>

                  <span>
                    {
                      selectedNode.node_type
                    }
                  </span>

                  <strong>
                    {
                      selectedNode.label
                    }
                  </strong>

                  <small>
                    {
                      selectedNode.layer
                    }
                  </small>
                </button>

                <div className="relation-line-bottom">
                  <ArrowRight
                    size={16}
                  />
                </div>
              </div>


              <RelationshipColumn
                title="Imports"
                nodes={
                  outgoingEdges
                    .map(
                      (edge) =>
                        getNode(
                          edge.target
                        )
                    )
                    .filter(Boolean)
                }
                onSelect={
                  setSelectedNodeId
                }
              />
            </div>
          )}


          <div className="graph-file-section">

            <div className="graph-file-heading">
              <div>
                <p className="small-label">
                  ARCHITECTURE FILES
                </p>

                <h3>
                  Repository modules
                </h3>
              </div>

              {hiddenCount > 0 && (
                <span>
                  {hiddenCount} config/test{" "}
                  {hiddenCount === 1
                    ? "file"
                    : "files"}{" "}
                  hidden
                </span>
              )}
            </div>


            <div className="real-architecture-map">

              {visibleNodes.map(
                (node) => (
                  <button
                    type="button"
                    key={
                      node.id
                    }
                    className={`real-node real-node-${node.node_type} ${
                      selectedNode?.id ===
                      node.id
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      setSelectedNodeId(
                        node.id
                      )
                    }
                  >
                    <div className="real-node-icon">
                      <NodeIcon
                        type={
                          node.node_type
                        }
                      />
                    </div>

                    <div className="real-node-copy">
                      <strong>
                        {
                          node.label
                        }
                      </strong>

                      <span>
                        {
                          node.node_type
                        }
                      </span>

                      <small>
                        {
                          node.layer
                        }
                      </small>
                    </div>
                  </button>
                )
              )}
            </div>
          </div>
        </div>
      </div>


      <aside className="arch-side-panel">

        <div className="arch-panel-card">
          <p className="small-label">
            SELECTED FILE
          </p>

          {selectedNode && (
            <>
              <div className="selected-module-title">

                <div className="selected-icon">
                  <NodeIcon
                    type={
                      selectedNode.node_type
                    }
                  />
                </div>

                <div>
                  <h2>
                    {
                      selectedNode.label
                    }
                  </h2>

                  <span>
                    {
                      selectedNode.node_type
                    }
                  </span>
                </div>
              </div>


              <p className="selected-description">
                {
                  selectedNode.path
                }
              </p>


              <div className="module-meta">

                <div>
                  <span>
                    Repository
                  </span>

                  <strong>
                    {repoName}
                  </strong>
                </div>

                <div>
                  <span>
                    Layer
                  </span>

                  <strong>
                    {
                      selectedNode.layer
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Language
                  </span>

                  <strong>
                    {selectedNode.language ||
                      "Unknown"}
                  </strong>
                </div>

                <div>
                  <span>
                    Connections
                  </span>

                  <strong>
                    {
                      incomingEdges.length +
                      outgoingEdges.length
                    }
                  </strong>
                </div>
              </div>
            </>
          )}
        </div>


        <div className="arch-panel-card">
          <p className="small-label">
            CONNECTION SUMMARY
          </p>

          <ConnectedSummary
            label="Imports"
            value={
              outgoingEdges.length
            }
          />

          <ConnectedSummary
            label="Imported by"
            value={
              incomingEdges.length
            }
          />
        </div>


        <div className="arch-panel-card compact">

          <p className="small-label">
            GRAPH STATUS
          </p>

          <div className="graph-summary">

            <div>
              <strong>
                {
                  visibleNodes.length
                }
              </strong>

              <span>
                Files
              </span>
            </div>

            <div>
              <strong>
                {
                  data.edge_count
                }
              </strong>

              <span>
                Imports
              </span>
            </div>

            <div>
              <strong>
                {
                  nodeTypes
                }
              </strong>

              <span>
                Types
              </span>
            </div>
          </div>
        </div>
      </aside>
    </section>
  );
}


function RelationshipColumn({
  title,
  nodes,
  onSelect,
}) {
  return (
    <div className="relationship-column">

      <span className="relationship-label">
        {title}
      </span>

      {nodes.length > 0 ? (
        nodes
          .slice(
            0,
            5
          )
          .map(
            (node) => (
              <button
                type="button"
                key={
                  node.id
                }
                onClick={() =>
                  onSelect(
                    node.id
                  )
                }
              >
                <NodeIcon
                  type={
                    node.node_type
                  }
                />

                <div>
                  <strong>
                    {
                      node.label
                    }
                  </strong>

                  <span>
                    {
                      node.node_type
                    }
                  </span>
                </div>
              </button>
            )
          )
      ) : (
        <div className="relationship-empty">
          None detected
        </div>
      )}
    </div>
  );
}


function RequestFlow({
  data,
}) {
  const flows =
    data.end_to_end_flows ||
    [];

  const requests =
    data.frontend_requests ||
    [];

  const routes =
    data.backend_routes ||
    [];

  const externalCalls =
    data.external_api_calls ||
    [];


  return (
    <section className="architecture-single-view">

      <div className="flow-header">
        <div>
          <p className="small-label">
            REQUEST LIFECYCLE
          </p>

          <h2>
            End-to-end application requests
          </h2>
        </div>

        <span>
          {flows.length} flows
        </span>
      </div>


      {flows.length > 0 ? (
        <div className="e2e-flow-list">

          {flows.map(
            (
              flow,
              index
            ) => (
              <EndToEndFlowCard
                key={`${flow.frontend_file}-${flow.endpoint}-${index}`}
                flow={flow}
              />
            )
          )}
        </div>
      ) : (
        <EmptyArchitectureState
          icon={
            <Route
              size={24}
            />
          }
          title="No request flows detected"
          text="No supported frontend API requests could be connected to backend routes."
        />
      )}


      <div className="architecture-info-grid architecture-info-grid-four">

        <ArchitectureInfoCard
          label="FRONTEND REQUESTS"
          title={
            requests.length
          }
          value="Detected"
          text="Client-side Axios and fetch requests."
        />

        <ArchitectureInfoCard
          label="BACKEND ROUTES"
          title={
            routes.length
          }
          value="Detected"
          text="Express or FastAPI endpoints."
        />

        <ArchitectureInfoCard
          label="MATCHED FLOWS"
          title={
            (
              data.request_flows ||
              []
            ).filter(
              (flow) =>
                flow.matched
            ).length
          }
          value="Connected"
          text="Requests mapped to backend handlers."
        />

        <ArchitectureInfoCard
          label="EXTERNAL API CALLS"
          title={
            externalCalls.length
          }
          value="Detected"
          text="Backend calls to third-party services."
        />
      </div>


      <div className="route-table-card">

        <div className="route-table-heading">
          <div>
            <p className="small-label">
              BACKEND ENDPOINTS
            </p>

            <h3>
              Route → controller mapping
            </h3>
          </div>

          <span>
            {routes.length} routes
          </span>
        </div>


        <div className="route-table">

          {routes.map(
            (
              route,
              index
            ) => (
              <div
                className="route-table-row route-table-row-expanded"
                key={`${route.file}-${route.method}-${route.endpoint}-${index}`}
              >
                <span className="route-method">
                  {
                    route.method
                  }
                </span>

                <strong>
                  {
                    route.endpoint
                  }
                </strong>

                <span>
                  {
                    route.handler ||
                    "Inline handler"
                  }
                </span>

                <small>
                  {
                    route.controller_file ||
                    route.file
                  }
                </small>
              </div>
            )
          )}
        </div>
      </div>
    </section>
  );
}


function EndToEndFlowCard({
  flow,
}) {
  const outputs = [
    ...(
      flow.external_services ||
      []
    ).map(
      (service) => ({
        type:
          "External Service",

        name:
          service,

        icon:
          <Cloud
            size={17}
          />,
      })
    ),

    ...(
      flow.data_technologies ||
      []
    ).map(
      (technology) => ({
        type:
          "Data Layer",

        name:
          technology,

        icon:
          <Database
            size={17}
          />,
      })
    ),
  ];


  return (
    <article className="e2e-flow-card">

      <div className="e2e-flow-top">

        <span className="flow-method-badge">
          {
            flow.method
          }
        </span>

        <code>
          {
            flow.endpoint
          }
        </code>
      </div>


      <div className="e2e-flow-track">

        <ArchitectureStage
          label="Frontend"
          title={
            getFileName(
              flow.frontend_file
            )
          }
          detail={
            flow.frontend_file
          }
          icon={
            <FileCode2
              size={18}
            />
          }
        />

        <StageArrow />

        <ArchitectureStage
          label="Route"
          title={
            getFileName(
              flow.route_file
            )
          }
          detail={
            flow.route_file ||
            "No route matched"
          }
          icon={
            <Route
              size={18}
            />
          }
        />

        <StageArrow />

        <ArchitectureStage
          label="Controller"
          title={
            flow.handler ||
            getFileName(
              flow.controller_file
            )
          }
          detail={
            flow.controller_file ||
            "No controller detected"
          }
          icon={
            <ServerCog
              size={18}
            />
          }
        />


        {outputs.length >
          0 && (
          <>
            <StageArrow />

            <div className="flow-output-stack">

              {outputs.map(
                (
                  output,
                  index
                ) => (
                  <ArchitectureStage
                    key={`${output.type}-${output.name}-${index}`}
                    label={
                      output.type
                    }
                    title={
                      output.name
                    }
                    detail={
                      output.type ===
                      "External Service"
                        ? "Third-party API"
                        : "Persistence layer"
                    }
                    icon={
                      output.icon
                    }
                    compact
                  />
                )
              )}
            </div>
          </>
        )}
      </div>
    </article>
  );
}


function ArchitectureStage({
  label,
  title,
  detail,
  icon,
  compact = false,
}) {
  return (
    <div
      className={`architecture-stage ${
        compact
          ? "compact"
          : ""
      }`}
    >
      <div className="architecture-stage-icon">
        {icon}
      </div>

      <div>
        <span>
          {label}
        </span>

        <strong>
          {title ||
            "Not detected"}
        </strong>

        <small>
          {detail}
        </small>
      </div>
    </div>
  );
}


function StageArrow() {
  return (
    <div className="stage-arrow">
      <ArrowRight
        size={17}
      />
    </div>
  );
}


function DataFlow({
  data,
}) {
  const flows =
    (
      data.end_to_end_flows ||
      []
    ).filter(
      (flow) =>
        (
          flow.data_technologies ||
          []
        ).length > 0 ||
        (
          flow.external_services ||
          []
        ).length > 0
    );

  const directConnections =
    data.data_connections ||
    [];


  return (
    <section className="architecture-single-view">

      <div className="flow-header">
        <div>
          <p className="small-label">
            DATA FLOW
          </p>

          <h2>
            How application data moves
          </h2>
        </div>

        <span>
          {flows.length} flows
        </span>
      </div>


      {flows.length > 0 ? (
        <div className="data-flow-list">

          {flows.map(
            (
              flow,
              index
            ) => (
              <DataFlowCard
                key={`${flow.frontend_file}-${flow.endpoint}-${index}`}
                flow={flow}
              />
            )
          )}
        </div>
      ) : (
        <EmptyArchitectureState
          icon={
            <Database
              size={24}
            />
          }
          title="No end-to-end data flows detected"
          text="CodeLens AI did not find any request path connected to a supported database or external service."
        />
      )}


      <div className="data-layer-summary">

        <div className="data-layer-summary-heading">
          <div>
            <p className="small-label">
              DETECTED DATA LAYER
            </p>

            <h3>
              Database connections
            </h3>
          </div>

          <span>
            {
              directConnections.length
            }{" "}
            detected
          </span>
        </div>


        {directConnections.length >
        0 ? (
          <div className="data-layer-grid">

            {directConnections.map(
              (
                connection,
                index
              ) => (
                <div
                  className="data-layer-card"
                  key={`${connection.file}-${connection.technology}-${index}`}
                >
                  <div className="data-layer-source">
                    <Settings2
                      size={17}
                    />

                    <div>
                      <strong>
                        {getFileName(
                          connection.file
                        )}
                      </strong>

                      <span>
                        {
                          connection.file
                        }
                      </span>
                    </div>
                  </div>

                  <ArrowRight
                    size={16}
                  />

                  <div className="data-layer-target">
                    <Database
                      size={17}
                    />

                    <div>
                      <strong>
                        {
                          connection.technology
                        }
                      </strong>

                      <span>
                        {
                          connection.connection_type
                        }
                      </span>
                    </div>
                  </div>
                </div>
              )
            )}
          </div>
        ) : (
          <p className="panel-empty-text">
            No database configuration
            detected.
          </p>
        )}
      </div>
    </section>
  );
}


function DataFlowCard({
  flow,
}) {
  return (
    <article className="data-flow-card">

      <div className="data-flow-request">
        <span>
          {
            flow.method
          }
        </span>

        <code>
          {
            flow.endpoint
          }
        </code>
      </div>


      <div className="data-flow-track">

        <MiniFlowNode
          label="Frontend"
          value={
            getFileName(
              flow.frontend_file
            )
          }
          icon={
            <FileCode2
              size={17}
            />
          }
        />

        <DataArrow />

        <MiniFlowNode
          label="Route"
          value={
            getFileName(
              flow.route_file
            )
          }
          icon={
            <Route
              size={17}
            />
          }
        />

        <DataArrow />

        <MiniFlowNode
          label="Controller"
          value={
            flow.handler ||
            getFileName(
              flow.controller_file
            )
          }
          icon={
            <ServerCog
              size={17}
            />
          }
        />


        {(
          flow.external_services ||
          []
        ).map(
          (
            service
          ) => (
            <DataOutput
              key={
                service
              }
              label="External API"
              value={
                service
              }
              icon={
                <Cloud
                  size={17}
                />
              }
            />
          )
        )}


        {(
          flow.data_technologies ||
          []
        ).map(
          (
            technology
          ) => (
            <DataOutput
              key={
                technology
              }
              label="Database"
              value={
                technology
              }
              icon={
                <Database
                  size={17}
                />
              }
            />
          )
        )}
      </div>
    </article>
  );
}


function MiniFlowNode({
  label,
  value,
  icon,
}) {
  return (
    <div className="mini-flow-node">

      <div>
        {icon}
      </div>

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}


function DataOutput({
  label,
  value,
  icon,
}) {
  return (
    <>
      <DataArrow />

      <div className="mini-flow-node output">

        <div>
          {icon}
        </div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>
      </div>
    </>
  );
}


function DataArrow() {
  return (
    <div className="data-arrow">
      <ArrowRight
        size={17}
      />
    </div>
  );
}


function Dependencies({
  repoName,
  data,
}) {
  const dependencies =
    data.external_dependencies ||
    [];

  const edges =
    data.edges || [];


  const runtimePackages =
    dependencies.filter(
      (dependency) =>
        !NODE_BUILT_INS.has(
          dependency.name
        ) &&
        !CONFIG_DEPENDENCIES.has(
          dependency.name
        )
    );


  const configPackages =
    dependencies.filter(
      (dependency) =>
        CONFIG_DEPENDENCIES.has(
          dependency.name
        )
    );


  const builtIns =
    dependencies.filter(
      (dependency) =>
        NODE_BUILT_INS.has(
          dependency.name
        )
    );


  return (
    <section className="architecture-single-view">

      <div className="flow-header">
        <div>
          <p className="small-label">
            DEPENDENCY MAP
          </p>

          <h2>
            Packages and source relationships
          </h2>
        </div>

        <span>
          {
            dependencies.length
          } dependencies
        </span>
      </div>


      <div className="dependency-summary-grid">

        <DependencySummary
          title="Application Packages"
          value={
            runtimePackages.length
          }
          icon={
            <Package
              size={18}
            />
          }
        />

        <DependencySummary
          title="Tooling / Config"
          value={
            configPackages.length
          }
          icon={
            <Settings2
              size={18}
            />
          }
        />

        <DependencySummary
          title="Node Built-ins"
          value={
            builtIns.length
          }
          icon={
            <Code2
              size={18}
            />
          }
        />

        <DependencySummary
          title="Internal Imports"
          value={
            edges.length
          }
          icon={
            <GitBranch
              size={18}
            />
          }
        />
      </div>


      <DependencyGroup
        title="Application Packages"
        description="Runtime dependencies used by application code."
        dependencies={
          runtimePackages
        }
      />


      {configPackages.length >
        0 && (
        <DependencyGroup
          title="Tooling & Configuration"
          description="Build, linting, and development dependencies."
          dependencies={
            configPackages
          }
        />
      )}


      {builtIns.length >
        0 && (
        <DependencyGroup
          title="Node.js Built-ins"
          description="Runtime modules provided by Node.js rather than npm packages."
          dependencies={
            builtIns
          }
        />
      )}


      <div className="module-dependency-section">

        <div className="internal-heading">
          <div>
            <p className="small-label">
              INTERNAL IMPORTS
            </p>

            <h3>
              Source file relationships
            </h3>
          </div>

          <span>
            {edges.length} connections
          </span>
        </div>


        <div className="dependency-root dependency-root-inline">

          <div className="dependency-root-icon">
            <Network
              size={19}
            />
          </div>

          <div>
            <strong>
              {repoName}
            </strong>

            <span>
              Internal source graph
            </span>
          </div>
        </div>


        {edges.length >
        0 ? (
          <div className="module-dependency-grid">

            {edges.map(
              (
                edge,
                index
              ) => (
                <DependencyRelation
                  key={`${edge.source}-${edge.target}-${index}`}
                  from={
                    getFileName(
                      edge.source
                    )
                  }
                  to={
                    getFileName(
                      edge.target
                    )
                  }
                  label={
                    edge.relationship
                  }
                />
              )
            )}
          </div>
        ) : (
          <p className="panel-empty-text">
            No internal imports
            detected.
          </p>
        )}
      </div>
    </section>
  );
}


function DependencyGroup({
  title,
  description,
  dependencies,
}) {
  if (
    dependencies.length ===
    0
  ) {
    return null;
  }


  return (
    <div className="dependency-group">

      <div className="dependency-group-heading">
        <div>
          <h3>
            {title}
          </h3>

          <p>
            {description}
          </p>
        </div>

        <span>
          {
            dependencies.length
          }
        </span>
      </div>


      <div className="dependency-nodes">

        {dependencies.map(
          (
            dependency
          ) => (
            <div
              className="dependency-node"
              key={
                dependency.name
              }
            >
              <div className="dependency-node-top">

                <Package
                  size={16}
                />

                <div>
                  <strong>
                    {
                      dependency.name
                    }
                  </strong>

                  <span>
                    Dependency
                  </span>
                </div>
              </div>


              <p>
                Used by{" "}
                {
                  dependency
                    .used_by
                    .length
                }{" "}
                source{" "}
                {dependency
                  .used_by
                  .length === 1
                  ? "file"
                  : "files"}
                .
              </p>


              <small>
                {dependency
                  .used_by
                  .slice(
                    0,
                    4
                  )
                  .map(
                    getFileName
                  )
                  .join(
                    " · "
                  )}

                {dependency
                  .used_by
                  .length >
                  4 &&
                  ` +${
                    dependency
                      .used_by
                      .length -
                    4
                  } more`}
              </small>
            </div>
          )
        )}
      </div>
    </div>
  );
}


function DependencySummary({
  title,
  value,
  icon,
}) {
  return (
    <div className="dependency-summary-card">

      <div>
        {icon}
      </div>

      <span>
        {title}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}


function DependencyRelation({
  from,
  to,
  label,
}) {
  return (
    <div className="module-dependency-card">

      <strong>
        {from}
      </strong>

      <div>
        <span>
          {label}
        </span>

        <ArrowRight
          size={15}
        />
      </div>

      <strong>
        {to}
      </strong>
    </div>
  );
}


function ConnectedSummary({
  label,
  value,
}) {
  return (
    <div className="connected-summary">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}


function ArchitectureInfoCard({
  label,
  title,
  value,
  text,
}) {
  return (
    <div className="architecture-info-card">

      <p className="small-label">
        {label}
      </p>

      <h3>
        {title}
      </h3>

      <strong>
        {value}
      </strong>

      <span>
        {text}
      </span>
    </div>
  );
}


function NodeIcon({
  type,
}) {
  switch (type) {
    case "component":
      return (
        <Braces
          size={18}
        />
      );

    case "page":
      return (
        <FileCode2
          size={18}
        />
      );

    case "entry":
      return (
        <GitBranch
          size={18}
        />
      );

    case "api":
      return (
        <Route
          size={18}
        />
      );

    case "controller":
      return (
        <ServerCog
          size={18}
        />
      );

    case "middleware":
      return (
        <ShieldCheck
          size={18}
        />
      );

    case "model":
      return (
        <Database
          size={18}
        />
      );

    case "configuration":
      return (
        <Settings2
          size={18}
        />
      );

    case "service":
      return (
        <Boxes
          size={18}
        />
      );

    default:
      return (
        <Code2
          size={18}
        />
      );
  }
}


function EmptyArchitectureState({
  icon,
  title,
  text,
}) {
  return (
    <div className="arch-empty-state">

      <div className="arch-empty-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>
    </div>
  );
}


function getFileName(
  path
) {
  if (!path) {
    return "Not detected";
  }

  const parts =
    path.split("/");

  return (
    parts[
      parts.length - 1
    ] || path
  );
}


function isTestFile(
  path
) {
  if (!path) {
    return false;
  }

  const value =
    path.toLowerCase();

  return (
    value.includes(
      ".test."
    ) ||
    value.includes(
      ".spec."
    ) ||
    value.includes(
      "/tests/"
    ) ||
    value.includes(
      "/test/"
    ) ||
    value.includes(
      "testgemini"
    )
  );
}


export default Architecture;