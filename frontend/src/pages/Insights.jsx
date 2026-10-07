import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertTriangle,
  ArrowRight,
  Boxes,
  CheckCircle2,
  Code2,
  Database,
  FileCode2,
  GitBranch,
  Network,
  RefreshCw,
  Route,
  ServerCog,
  TriangleAlert,
} from "lucide-react";

import AppLayout from "../components/AppLayout";

import {
  useRepo,
} from "../context/RepoContext";

import {
  analyzeInsightsApi,
} from "../services/api";

import "../styles/insights.css";


function Insights() {
  const {
    repoName,
    repoUrl,
  } = useRepo();

  const [
    data,
    setData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  const displayName =
    repoName ||
    "Repository";


  const loadInsights =
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
        const result =
          await analyzeInsightsApi(
            repoUrl
          );

        setData(
          result
        );

      } catch (
        requestError
      ) {
        let message =
          "Could not analyze repository insights.";

        if (
          requestError
            .response
            ?.data
            ?.detail
        ) {
          message =
            requestError
              .response
              .data
              .detail;

        } else if (
          requestError.code ===
          "ECONNABORTED"
        ) {
          message =
            "Insights analysis timed out.";

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
    loadInsights();
  }, [repoUrl]);


  if (loading) {
    return (
      <AppLayout>
        <div className="insights-page">

          <InsightsHeader
            repoName={
              displayName
            }
            status="loading"
          />

          <LoadingState
            repoName={
              displayName
            }
          />

        </div>
      </AppLayout>
    );
  }


  if (error) {
    return (
      <AppLayout>
        <div className="insights-page">

          <InsightsHeader
            repoName={
              displayName
            }
            status="error"
          />

          <ErrorState
            message={
              error
            }
            onRetry={
              loadInsights
            }
          />

        </div>
      </AppLayout>
    );
  }


  if (!data) {
    return null;
  }


  return (
    <AppLayout>

      <div className="insights-page">

        <InsightsHeader
          repoName={
            displayName
          }
          status="ready"
        />


        <SummaryCards
          data={
            data
          }
        />


        <div className="insights-layout">

          <main className="insights-main">

            <FindingsSection
              findings={
                data.findings ||
                []
              }
            />


            <LargestFiles
              files={
                data.largest_files ||
                []
              }
            />


            <DependencyHotspots
              incoming={
                data.most_imported_files ||
                []
              }
              outgoing={
                data.highest_outgoing_imports ||
                []
              }
            />

          </main>


          <aside className="insights-sidebar">

            <RouteCoverage
              coverage={
                data.route_coverage
              }
            />


            <NodeTypes
              nodeTypes={
                data.summary
                  ?.node_types ||
                {}
              }
            />


            <ArchitectureSummary
              data={
                data
              }
            />

          </aside>

        </div>

      </div>

    </AppLayout>
  );
}


function InsightsHeader({
  repoName,
  status,
}) {
  return (
    <section className="insights-header">

      <div>

        <p className="insights-eyebrow">
          ENGINEERING INSIGHTS
        </p>

        <h1>
          Repository Insights
        </h1>

        <p>
          Repository-derived
          maintainability,
          dependency, request-flow,
          and integration insights
          for{" "}
          <strong>
            {repoName}
          </strong>
          .
        </p>

      </div>


      <div
        className={`insights-status ${status}`}
      >

        {status ===
        "loading" ? (
          <>
            <RefreshCw
              size={14}
              className="insights-spin"
            />

            Analyzing
          </>
        ) : status ===
          "error" ? (
          <>
            <AlertTriangle
              size={14}
            />

            Analysis Failed
          </>
        ) : (
          <>
            <CheckCircle2
              size={14}
            />

            Live Analysis
          </>
        )}

      </div>

    </section>
  );
}


function SummaryCards({
  data,
}) {
  const summary =
    data.summary || {};

  const routeCoverage =
    data.route_coverage || {};

  const matched =
    routeCoverage
      .matched_requests ||
    0;

  const frontendRequests =
    routeCoverage
      .frontend_requests ||
    0;


  return (
    <section className="insights-summary-grid">

      <MetricCard
        icon={
          <FileCode2
            size={19}
          />
        }
        label="Source Files"
        value={
          summary.source_files ||
          0
        }
        detail={`${summary.frontend_files || 0} frontend · ${summary.backend_files || 0} backend`}
      />


      <MetricCard
        icon={
          <GitBranch
            size={19}
          />
        }
        label="Internal Imports"
        value={
          summary.total_imports ||
          0
        }
        detail="Detected source relationships"
      />


      <MetricCard
        icon={
          <Route
            size={19}
          />
        }
        label="Request Matching"
        value={`${matched}/${frontendRequests}`}
        detail={
          routeCoverage.unmatched_requests >
          0
            ? `${routeCoverage.unmatched_requests} unmatched`
            : "All detected requests matched"
        }
      />


      <MetricCard
        icon={
          <Network
            size={19}
          />
        }
        label="External APIs"
        value={
          summary.external_api_calls ||
          0
        }
        detail={`${summary.external_dependencies || 0} imported dependencies`}
      />

    </section>
  );
}


function MetricCard({
  icon,
  label,
  value,
  detail,
}) {
  return (
    <div className="insights-metric-card">

      <div className="insights-metric-icon">
        {icon}
      </div>

      <div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

        <small>
          {detail}
        </small>

      </div>

    </div>
  );
}


function FindingsSection({
  findings,
}) {
  return (
    <section className="insights-card">

      <SectionHeading
        eyebrow="FINDINGS"
        title="Engineering observations"
        count={
          findings.length
        }
      />


      {findings.length >
      0 ? (
        <div className="findings-list">

          {findings.map(
            (
              finding,
              index
            ) => (
              <FindingCard
                key={`${finding.category}-${finding.title}-${index}`}
                finding={
                  finding
                }
              />
            )
          )}

        </div>
      ) : (
        <EmptyState
          text="No repository findings were produced."
        />
      )}

    </section>
  );
}


function FindingCard({
  finding,
}) {
  const icon =
    finding.severity ===
    "high" ? (
      <TriangleAlert
        size={18}
      />
    ) : finding.severity ===
      "medium" ? (
      <AlertTriangle
        size={18}
      />
    ) : (
      <CheckCircle2
        size={18}
      />
    );


  return (
    <article
      className={`finding-card finding-${finding.severity}`}
    >

      <div className="finding-icon">
        {icon}
      </div>


      <div className="finding-content">

        <div className="finding-heading">

          <div>

            <span>
              {
                finding.category
              }
            </span>

            <h3>
              {
                finding.title
              }
            </h3>

          </div>


          <SeverityBadge
            severity={
              finding.severity
            }
          />

        </div>


        <p>
          {
            finding.description
          }
        </p>


        {finding.files?.length >
          0 && (
          <div className="finding-files">

            {finding.files.map(
              (
                file
              ) => (
                <span
                  key={
                    file
                  }
                >
                  <Code2
                    size={12}
                  />

                  {
                    getFileName(
                      file
                    )
                  }
                </span>
              )
            )}

          </div>
        )}

      </div>

    </article>
  );
}


function SeverityBadge({
  severity,
}) {
  return (
    <span
      className={`severity-badge severity-${severity}`}
    >
      {severity}
    </span>
  );
}


function LargestFiles({
  files,
}) {
  const maxLines =
    useMemo(
      () =>
        Math.max(
          ...files.map(
            (file) =>
              file.lines
          ),
          1
        ),
      [files]
    );


  return (
    <section className="insights-card">

      <SectionHeading
        eyebrow="FILE SIZE"
        title="Largest source files"
        count={
          files.length
        }
      />


      <div className="largest-files-list">

        {files.map(
          (
            file,
            index
          ) => {
            const percentage =
              Math.max(
                4,
                (
                  file.lines /
                  maxLines
                ) *
                  100
              );

            return (
              <div
                className="largest-file-row"
                key={
                  file.path
                }
              >

                <div className="largest-file-rank">
                  {index + 1}
                </div>


                <div className="largest-file-content">

                  <div className="largest-file-heading">

                    <div>

                      <strong>
                        {
                          getFileName(
                            file.path
                          )
                        }
                      </strong>

                      <span>
                        {
                          file.path
                        }
                      </span>

                    </div>


                    <div className="largest-file-lines">

                      <strong>
                        {
                          file.lines
                        }
                      </strong>

                      <span>
                        lines
                      </span>

                    </div>

                  </div>


                  <div className="file-bar-track">

                    <div
                      className="file-bar-value"
                      style={{
                        width:
                          `${percentage}%`,
                      }}
                    />

                  </div>


                  <div className="largest-file-meta">

                    <span>
                      {
                        file.node_type
                      }
                    </span>

                    <span>
                      {
                        file.layer
                      }
                    </span>

                    <span>
                      {
                        file.imports
                      }{" "}
                      imports
                    </span>

                    <span>
                      imported by{" "}
                      {
                        file.imported_by
                      }
                    </span>

                  </div>

                </div>

              </div>
            );
          }
        )}

      </div>

    </section>
  );
}


function DependencyHotspots({
  incoming,
  outgoing,
}) {
  return (
    <section className="insights-card">

      <SectionHeading
        eyebrow="DEPENDENCY HOTSPOTS"
        title="Repository coupling"
      />


      <div className="hotspot-grid">

        <HotspotColumn
          title="Most Imported"
          subtitle="Files depended on by other modules"
          items={
            incoming
          }
          metricLabel="incoming"
        />


        <HotspotColumn
          title="Most Dependencies"
          subtitle="Files importing internal modules"
          items={
            outgoing
          }
          metricLabel="outgoing"
        />

      </div>

    </section>
  );
}


function HotspotColumn({
  title,
  subtitle,
  items,
  metricLabel,
}) {
  return (
    <div className="hotspot-column">

      <div className="hotspot-column-heading">

        <h3>
          {title}
        </h3>

        <p>
          {subtitle}
        </p>

      </div>


      <div className="hotspot-list">

        {items
          .slice(
            0,
            6
          )
          .map(
            (
              item
            ) => (
              <div
                className="hotspot-row"
                key={`${item.path}-${item.metric}`}
              >

                <div>

                  <strong>
                    {
                      getFileName(
                        item.path
                      )
                    }
                  </strong>

                  <span>
                    {
                      item.path
                    }
                  </span>

                </div>


                <div className="hotspot-value">

                  <strong>
                    {
                      item.value
                    }
                  </strong>

                  <span>
                    {
                      metricLabel
                    }
                  </span>

                </div>

              </div>
            )
          )}

      </div>

    </div>
  );
}


function RouteCoverage({
  coverage,
}) {
  if (!coverage) {
    return null;
  }


  const total =
    coverage.frontend_requests ||
    0;

  const matched =
    coverage.matched_requests ||
    0;

  const percentage =
    total > 0
      ? Math.round(
          (
            matched /
            total
          ) *
            100
        )
      : 0;


  return (
    <section className="insights-side-card">

      <p className="insights-side-label">
        REQUEST COVERAGE
      </p>


      <div className="coverage-number">

        <strong>
          {percentage}%
        </strong>

        <span>
          matched
        </span>

      </div>


      <div className="coverage-bar">

        <div
          style={{
            width:
              `${percentage}%`,
          }}
        />

      </div>


      <div className="coverage-stats">

        <div>

          <span>
            Frontend requests
          </span>

          <strong>
            {
              coverage.frontend_requests
            }
          </strong>

        </div>


        <div>

          <span>
            Backend routes
          </span>

          <strong>
            {
              coverage.backend_routes
            }
          </strong>

        </div>


        <div>

          <span>
            Matched
          </span>

          <strong>
            {
              coverage.matched_requests
            }
          </strong>

        </div>


        <div>

          <span>
            Unmatched
          </span>

          <strong>
            {
              coverage.unmatched_requests
            }
          </strong>

        </div>

      </div>

    </section>
  );
}


function NodeTypes({
  nodeTypes,
}) {
  const entries =
    Object.entries(
      nodeTypes
    ).sort(
      (
        first,
        second
      ) =>
        second[1] -
        first[1]
    );


  return (
    <section className="insights-side-card">

      <p className="insights-side-label">
        FILE ROLES
      </p>


      <div className="node-type-list">

        {entries.map(
          ([
            type,
            count,
          ]) => (
            <div
              key={
                type
              }
            >

              <span>
                {
                  type
                }
              </span>

              <strong>
                {
                  count
                }
              </strong>

            </div>
          )
        )}

      </div>

    </section>
  );
}


function ArchitectureSummary({
  data,
}) {
  const summary =
    data.summary ||
    {};


  return (
    <section className="insights-side-card">

      <p className="insights-side-label">
        REPOSITORY PROFILE
      </p>


      <div className="profile-row">

        <div>
          <ServerCog
            size={16}
          />
        </div>

        <span>
          Architecture
        </span>

        <strong>
          {
            data.architecture
          }
        </strong>

      </div>


      <div className="profile-row">

        <div>
          <Boxes
            size={16}
          />
        </div>

        <span>
          Dependencies
        </span>

        <strong>
          {
            summary.external_dependencies ||
            0
          }
        </strong>

      </div>


      <div className="profile-row">

        <div>
          <Database
            size={16}
          />
        </div>

        <span>
          Data layers
        </span>

        <strong>
          {
            summary.data_connections ||
            0
          }
        </strong>

      </div>


      <div className="profile-row">

        <div>
          <Network
            size={16}
          />
        </div>

        <span>
          External calls
        </span>

        <strong>
          {
            summary.external_api_calls ||
            0
          }
        </strong>

      </div>

    </section>
  );
}


function SectionHeading({
  eyebrow,
  title,
  count,
}) {
  return (
    <div className="insights-section-heading">

      <div>

        <p>
          {eyebrow}
        </p>

        <h2>
          {title}
        </h2>

      </div>


      {count !==
        undefined && (
        <span>
          {count}
        </span>
      )}

    </div>
  );
}


function LoadingState({
  repoName,
}) {
  return (
    <section className="insights-loading">

      <div>

        <RefreshCw
          size={24}
          className="insights-spin"
        />

      </div>


      <h2>
        Analyzing engineering signals
      </h2>


      <p>
        Inspecting file size,
        dependencies, request
        mappings, and integrations
        across{" "}
        <strong>
          {repoName}
        </strong>
        .
      </p>

    </section>
  );
}


function ErrorState({
  message,
  onRetry,
}) {
  return (
    <section className="insights-loading">

      <div className="error">

        <AlertTriangle
          size={24}
        />

      </div>


      <h2>
        Insights analysis failed
      </h2>


      <p>
        {message}
      </p>


      <button
        type="button"
        onClick={
          onRetry
        }
      >
        <RefreshCw
          size={14}
        />

        Try Again
      </button>

    </section>
  );
}


function EmptyState({
  text,
}) {
  return (
    <div className="insights-empty">

      <Code2
        size={20}
      />

      <span>
        {text}
      </span>

    </div>
  );
}


function getFileName(
  path
) {
  if (!path) {
    return "Unknown";
  }

  const parts =
    path.split("/");

  return (
    parts[
      parts.length - 1
    ] || path
  );
}


export default Insights;