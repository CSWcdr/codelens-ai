import {
  AlertTriangle,
  BarChart3,
  Boxes,
  FileCode2,
  GitBranch,
  MessageSquare,
  Network,
  Package,
  RotateCcw,
  Sparkles,
} from "lucide-react";

import {
  useNavigate,
} from "react-router-dom";

import AppLayout from "../components/AppLayout";
import Loading from "../components/Loading";

import {
  useRepo,
} from "../context/RepoContext";

import "../styles/repository.css";


function Repository() {
  const navigate =
    useNavigate();


  const {
    repoName,
    repoUrl,

    analysisData,
    analysisStatus,
    analysisError,

    analyzeRepository,
  } = useRepo();


  const displayedName =
    repoName ||
    "Repository";


  const currentStatus =
    analysisStatus ||
    "pending";


  const retryAnalysis =
    async () => {
      if (!repoUrl) {
        navigate("/");

        return;
      }

      await analyzeRepository(
        repoUrl
      );
    };


  const languages =
    analysisData?.languages ||
    {};


  const languageEntries =
    Object.entries(
      languages
    )
      .sort(
        (
          first,
          second
        ) =>
          second[1] -
          first[1]
      )
      .slice(
        0,
        4
      );


  const overviewSummary =
    analysisData
      ?.overview
      ?.summary ||
    "";


  const overviewParagraphs =
    overviewSummary
      .split("\n\n")
      .map(
        (
          paragraph
        ) =>
          paragraph.trim()
      )
      .filter(
        Boolean
      );


  const overviewHighlights =
    analysisData
      ?.overview
      ?.highlights ||
    [];


  return (
    <AppLayout>

      <div className="repository-content">

        <section className="repo-heading-row">

          <div>

            <p className="small-label">
              CODEBASE OVERVIEW
            </p>


            <h1>
              {displayedName}
            </h1>


            <p className="repo-description">

              {
                analysisData
                  ?.description ||
                "Explore repository structure, technologies, architecture, dependencies, and code intelligence from one workspace."
              }

            </p>

          </div>

        </section>


        {currentStatus ===
          "loading" && (
          <Loading
            title={`Analyzing ${displayedName}`}
            text="Fetching repository metadata, structure, languages, modules, dependencies, and repository signals from GitHub."
          />
        )}


        {currentStatus ===
          "error" && (
          <section className="repo-state-panel repo-error-panel">

            <div className="repo-state-icon error">

              <AlertTriangle
                size={22}
              />

            </div>


            <div className="repo-state-content">

              <h2>
                Repository analysis failed
              </h2>


              <p>

                {
                  analysisError ||
                  "CodeLens AI could not analyze this repository."
                }

              </p>

            </div>


            <button
              type="button"
              onClick={
                retryAnalysis
              }
            >

              <RotateCcw
                size={14}
              />

              Try Again

            </button>

          </section>
        )}


        {currentStatus ===
          "ready" &&
          analysisData && (
          <>

            <section className="stats-grid">

              <StatCard
                icon={
                  <FileCode2
                    size={20}
                  />
                }
                label="Files"
                value={
                  analysisData
                    .total_files
                }
                helper="Source files"
              />


              <StatCard
                icon={
                  <GitBranch
                    size={20}
                  />
                }
                label="Languages"
                value={
                  Object.keys(
                    languages
                  ).length
                }
                helper="Detected"
              />


              <StatCard
                icon={
                  <Package
                    size={20}
                  />
                }
                label="Dependencies"
                value={
                  analysisData
                    .dependency_count
                }
                helper="Packages"
              />


              <StatCard
                icon={
                  <Boxes
                    size={20}
                  />
                }
                label="Modules"
                value={
                  analysisData
                    .total_modules
                }
                helper="Root modules"
              />

            </section>


            <section className="repo-content-grid">


              <div className="repo-panel">

                <div className="panel-heading">

                  <div>

                    <p className="small-label">
                      REPOSITORY SUMMARY
                    </p>

                    <h2>
                      Codebase Overview
                    </h2>

                  </div>

                </div>


                <div className="pending-content repository-intelligence">

                  <div className="pending-icon">

                    <Sparkles
                      size={22}
                    />

                  </div>


                  <h3>
                    Repository Intelligence
                  </h3>


                  <div className="overview-text">

                    {overviewParagraphs.length >
                    0 ? (
                      overviewParagraphs.map(
                        (
                          paragraph,
                          index
                        ) => (
                          <p
                            key={
                              `${index}-${paragraph.slice(
                                0,
                                20
                              )}`
                            }
                          >
                            {paragraph}
                          </p>
                        )
                      )
                    ) : (
                      <p>

                        CodeLens AI analyzed{" "}

                        <strong>
                          {displayedName}
                        </strong>

                        {" "}using repository
                        metadata, structure,
                        languages, modules, and
                        dependency information.

                      </p>
                    )}

                  </div>


                  {overviewHighlights.length >
                    0 && (
                    <div className="overview-highlights">

                      {overviewHighlights.map(
                        (
                          highlight
                        ) => (
                          <span
                            className="overview-highlight-chip"
                            key={
                              highlight
                            }
                          >
                            {highlight}
                          </span>
                        )
                      )}

                    </div>
                  )}

                </div>


                <div className="summary-list">

                  <SummaryProperty
                    label="Primary Framework"
                    value={
                      analysisData
                        .primary_framework ||
                      "Not detected"
                    }
                  />


                  <SummaryProperty
                    label="Build Tool"
                    value={
                      analysisData
                        .build_tool ||
                      "Not detected"
                    }
                  />


                  <SummaryProperty
                    label="Main Language"
                    value={
                      analysisData
                        .primary_language ||
                      "Unknown"
                    }
                  />


                  <SummaryProperty
                    label="Architecture"
                    value={
                      analysisData
                        .architecture ||
                      "Unknown"
                    }
                  />

                </div>

              </div>


              <div className="repo-panel">

                <div className="panel-heading">

                  <div>

                    <p className="small-label">
                      STACK
                    </p>

                    <h2>
                      Technologies
                    </h2>

                  </div>

                </div>


                <div className="technology-empty-state">

                  <div className="technology-placeholder-row">

                    {analysisData
                      .primary_framework && (
                      <span>

                        {
                          analysisData
                            .primary_framework
                        }

                      </span>
                    )}


                    {analysisData
                      .build_tool && (
                      <span>

                        {
                          analysisData
                            .build_tool
                        }

                      </span>
                    )}


                    {analysisData
                      .primary_language && (
                      <span>

                        {
                          analysisData
                            .primary_language
                        }

                      </span>
                    )}

                  </div>


                  <p>

                    Detected from repository
                    metadata, dependency files,
                    language analysis, and
                    source structure.

                  </p>

                </div>


                <div className="language-bars">

                  {languageEntries.length >
                  0 ? (
                    languageEntries.map(
                      ([
                        language,
                        percentage,
                      ]) => (
                        <LanguageBar
                          key={
                            language
                          }
                          label={
                            language
                          }
                          percentage={
                            percentage
                          }
                        />
                      )
                    )
                  ) : (
                    <p className="quick-actions-description">

                      No language data
                      detected.

                    </p>
                  )}

                </div>

              </div>

            </section>


            <section className="quick-actions-panel">

              <p className="small-label">
                QUICK ACTIONS
              </p>


              <h2>

                Explore{" "}
                {displayedName}

              </h2>


              <p className="quick-actions-description">

                Continue into architecture,
                repository questions, and
                engineering insights.

              </p>


              <div className="action-grid">

                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      "/architecture"
                    )
                  }
                >

                  <Network
                    size={19}
                  />


                  <div>

                    <strong>
                      View Architecture
                    </strong>

                    <span>
                      Explore codebase
                      relationships
                    </span>

                  </div>

                </button>


                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      "/assistant"
                    )
                  }
                >

                  <MessageSquare
                    size={19}
                  />


                  <div>

                    <strong>
                      Ask CodeLens AI
                    </strong>

                    <span>
                      Interact with the
                      repository assistant
                    </span>

                  </div>

                </button>


                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      "/insights"
                    )
                  }
                >

                  <BarChart3
                    size={19}
                  />


                  <div>

                    <strong>
                      Code Insights
                    </strong>

                    <span>
                      Explore analytics
                      and findings
                    </span>

                  </div>

                </button>

              </div>

            </section>

          </>
        )}


        {currentStatus ===
          "pending" && (
          <section className="repo-state-panel">

            <div className="repo-state-icon">

              <FileCode2
                size={22}
              />

            </div>


            <div className="repo-state-content">

              <h2>
                Analysis unavailable
              </h2>


              <p>

                Run repository analysis
                again to load the latest
                backend data.

              </p>

            </div>


            <button
              type="button"
              onClick={
                retryAnalysis
              }
            >

              <RotateCcw
                size={14}
              />

              Analyze Repository

            </button>

          </section>
        )}

      </div>

    </AppLayout>
  );
}


function StatCard({
  icon,
  label,
  value,
  helper,
}) {
  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>


      <div>

        <p>
          {label}
        </p>

        <h3>
          {value ?? "—"}
        </h3>

        <span>
          {helper}
        </span>

      </div>

    </div>
  );
}


function SummaryProperty({
  label,
  value,
}) {
  return (
    <div>

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function LanguageBar({
  label,
  percentage,
}) {
  return (
    <div className="language-row">

      <div className="language-title">

        <span>
          {label}
        </span>

        <span>
          {percentage}%
        </span>

      </div>


      <div className="bar">

        <div
          style={{
            width:
              `${percentage}%`,
          }}
        ></div>

      </div>

    </div>
  );
}


export default Repository;