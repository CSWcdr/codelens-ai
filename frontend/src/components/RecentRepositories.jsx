import {
    AlertCircle,
    ArrowRight,
    CheckCircle2,
    GitBranch,
    LoaderCircle,
    RefreshCw,
    Trash2,
  } from "lucide-react";
  
  import {
    useEffect,
    useState,
  } from "react";
  
  import {
    useNavigate,
  } from "react-router-dom";
  
  import {
    clearRepositoryHistoryApi,
    deleteRepositoryHistoryApi,
    getApiErrorMessage,
    getRepositoryHistoryApi,
  } from "../services/api";
  
  import {
    useRepo,
  } from "../context/RepoContext";
  
  import "../styles/recent-repositories.css";
  
  
  function formatRelativeTime(
    value
  ) {
    if (!value) {
      return "Unknown";
    }
  
    const date =
      new Date(value);
  
    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "Unknown";
    }
  
    const difference =
      Date.now() -
      date.getTime();
  
    const seconds =
      Math.max(
        0,
        Math.floor(
          difference / 1000
        )
      );
  
    if (seconds < 60) {
      return "Just now";
    }
  
    const minutes =
      Math.floor(
        seconds / 60
      );
  
    if (minutes < 60) {
      return `${minutes} ${
        minutes === 1
          ? "minute"
          : "minutes"
      } ago`;
    }
  
    const hours =
      Math.floor(
        minutes / 60
      );
  
    if (hours < 24) {
      return `${hours} ${
        hours === 1
          ? "hour"
          : "hours"
      } ago`;
    }
  
    const days =
      Math.floor(
        hours / 24
      );
  
    if (days < 7) {
      return `${days} ${
        days === 1
          ? "day"
          : "days"
      } ago`;
    }
  
    return date.toLocaleDateString(
      undefined,
      {
        year: "numeric",
        month: "short",
        day: "numeric",
      }
    );
  }
  
  
  function RecentRepositories() {
    const navigate =
      useNavigate();
  
    const {
      analyzeRepository,
    } = useRepo();
  
  
    const [
      repositories,
      setRepositories,
    ] = useState([]);
  
  
    const [
      historyStatus,
      setHistoryStatus,
    ] = useState(
      "loading"
    );
  
  
    const [
      historyError,
      setHistoryError,
    ] = useState("");
  
  
    const [
      openingRepoUrl,
      setOpeningRepoUrl,
    ] = useState("");
  
  
    const [
      deletingRepoUrl,
      setDeletingRepoUrl,
    ] = useState("");
  
  
    const [
      isClearing,
      setIsClearing,
    ] = useState(false);
  
  
    const loadHistory =
      async () => {
        setHistoryStatus(
          "loading"
        );
  
        setHistoryError("");
  
        try {
          const data =
            await getRepositoryHistoryApi(
              12
            );
  
          setRepositories(
            data?.repositories ||
              []
          );
  
          setHistoryStatus(
            "ready"
          );
        } catch (error) {
          setHistoryError(
            getApiErrorMessage(
              error
            )
          );
  
          setHistoryStatus(
            "error"
          );
        }
      };
  
  
    useEffect(() => {
      loadHistory();
    }, []);
  
  
    const handleOpenRepository =
      async (
        repository
      ) => {
        if (
          !repository?.repo_url ||
          openingRepoUrl
        ) {
          return;
        }
  
        setOpeningRepoUrl(
          repository.repo_url
        );
  
        setHistoryError("");
  
        const result =
          await analyzeRepository(
            repository.repo_url
          );
  
        if (
          result.success
        ) {
          navigate(
            "/repository"
          );
  
          return;
        }
  
        setHistoryError(
          result.error ||
            "Could not open this repository."
        );
  
        setOpeningRepoUrl("");
      };
  
  
    const handleDeleteRepository =
      async (
        repository
      ) => {
        if (
          !repository?.repo_url ||
          deletingRepoUrl ||
          isClearing
        ) {
          return;
        }
  
        const confirmed =
          window.confirm(
            `Remove ${repository.repo_name} from recent repositories?`
          );
  
        if (!confirmed) {
          return;
        }
  
        setDeletingRepoUrl(
          repository.repo_url
        );
  
        setHistoryError("");
  
        try {
          await deleteRepositoryHistoryApi(
            repository.repo_url
          );
  
          setRepositories(
            (
              currentRepositories
            ) =>
              currentRepositories.filter(
                (
                  currentRepository
                ) =>
                  currentRepository.repo_url !==
                  repository.repo_url
              )
          );
        } catch (error) {
          setHistoryError(
            getApiErrorMessage(
              error
            )
          );
        } finally {
          setDeletingRepoUrl(
            ""
          );
        }
      };
  
  
    const handleClearHistory =
      async () => {
        if (
          repositories.length ===
            0 ||
          isClearing
        ) {
          return;
        }
  
        const confirmed =
          window.confirm(
            "Clear all repository history? This will not delete any GitHub repository."
          );
  
        if (!confirmed) {
          return;
        }
  
        setIsClearing(
          true
        );
  
        setHistoryError("");
  
        try {
          await clearRepositoryHistoryApi();
  
          setRepositories([]);
        } catch (error) {
          setHistoryError(
            getApiErrorMessage(
              error
            )
          );
        } finally {
          setIsClearing(
            false
          );
        }
      };
  
  
    return (
      <section
        className="landing-section recent-repositories-section"
        id="recent"
      >
        <div className="recent-repositories-header">
  
          <div className="section-heading recent-heading">
            <div className="section-eyebrow">
              <GitBranch
                size={14}
              />
  
              RECENT REPOSITORIES
            </div>
  
            <h2>
              Continue exploring your
              recent codebases.
            </h2>
  
            <p>
              CodeLens remembers repositories
              you have analyzed so you can
              return to them without pasting
              the GitHub URL again.
            </p>
          </div>
  
  
          {repositories.length >
            0 && (
            <button
              type="button"
              className="recent-clear-button"
              onClick={
                handleClearHistory
              }
              disabled={
                isClearing ||
                Boolean(
                  openingRepoUrl
                )
              }
            >
              {isClearing ? (
                <>
                  <LoaderCircle
                    size={14}
                    className="recent-spinner"
                  />
  
                  Clearing...
                </>
              ) : (
                <>
                  <Trash2
                    size={14}
                  />
  
                  Clear history
                </>
              )}
            </button>
          )}
        </div>
  
  
        {historyError && (
          <div className="recent-history-error">
            <AlertCircle
              size={16}
            />
  
            <span>
              {historyError}
            </span>
  
            {historyStatus ===
              "error" && (
              <button
                type="button"
                onClick={
                  loadHistory
                }
              >
                Retry
              </button>
            )}
          </div>
        )}
  
  
        {historyStatus ===
          "loading" && (
          <div className="recent-loading-state">
            <LoaderCircle
              size={22}
              className="recent-spinner"
            />
  
            <div>
              <strong>
                Loading repository
                history
              </strong>
  
              <span>
                Checking your recent
                CodeLens analyses.
              </span>
            </div>
          </div>
        )}
  
  
        {historyStatus ===
          "ready" &&
          repositories.length ===
            0 && (
            <div className="recent-empty-state">
              <div className="recent-empty-icon">
                <GitBranch
                  size={22}
                />
              </div>
  
              <div>
                <strong>
                  No recent repositories
                  yet
                </strong>
  
                <p>
                  Analyze your first
                  GitHub repository and
                  it will appear here
                  automatically.
                </p>
              </div>
            </div>
          )}
  
  
        {historyStatus ===
          "ready" &&
          repositories.length >
            0 && (
            <div className="recent-repositories-grid">
              {repositories.map(
                (
                  repository
                ) => {
                  const isOpening =
                    openingRepoUrl ===
                    repository.repo_url;
  
                  const isDeleting =
                    deletingRepoUrl ===
                    repository.repo_url;
  
                  const analysisCount =
                    repository.analysis_count ||
                    1;
  
  
                  return (
                    <article
                      className="recent-repository-card"
                      key={
                        repository.id ||
                        repository.repo_url
                      }
                    >
                      <div className="recent-card-top">
                        <div className="recent-repo-icon">
                          <GitBranch
                            size={18}
                          />
                        </div>
  
                        <button
                          type="button"
                          className="recent-delete-button"
                          aria-label={`Remove ${repository.repo_name} from history`}
                          title="Remove from history"
                          disabled={
                            isDeleting ||
                            isOpening ||
                            isClearing
                          }
                          onClick={() =>
                            handleDeleteRepository(
                              repository
                            )
                          }
                        >
                          {isDeleting ? (
                            <LoaderCircle
                              size={14}
                              className="recent-spinner"
                            />
                          ) : (
                            <Trash2
                              size={14}
                            />
                          )}
                        </button>
                      </div>
  
  
                      <div className="recent-card-content">
                        <span className="recent-owner">
                          {
                            repository.owner
                          }
                        </span>
  
                        <h3>
                          {
                            repository.repo_name
                          }
                        </h3>
  
                        {repository.description && (
                          <p className="recent-description">
                            {
                              repository.description
                            }
                          </p>
                        )}
  
  
                        <div className="recent-tags">
                          {repository.primary_language && (
                            <span>
                              {
                                repository.primary_language
                              }
                            </span>
                          )}
  
                          {repository.primary_framework && (
                            <span>
                              {
                                repository.primary_framework
                              }
                            </span>
                          )}
  
                          {repository.architecture && (
                            <span>
                              {
                                repository.architecture
                              }
                            </span>
                          )}
  
                          {repository.default_branch && (
                            <span>
                              {
                                repository.default_branch
                              }
                            </span>
                          )}
                        </div>
                      </div>
  
  
                      <div className="recent-card-meta">
                        <div>
                          <CheckCircle2
                            size={13}
                          />
  
                          <span>
                            {
                              analysisCount
                            }{" "}
                            {
                              analysisCount ===
                              1
                                ? "analysis"
                                : "analyses"
                            }
                          </span>
                        </div>
  
                        <span className="recent-dot">
                          •
                        </span>
  
                        <span>
                          {
                            formatRelativeTime(
                              repository.last_analyzed_at
                            )
                          }
                        </span>
                      </div>
  
  
                      <button
                        type="button"
                        className="recent-open-button"
                        disabled={
                          Boolean(
                            openingRepoUrl
                          ) ||
                          isDeleting ||
                          isClearing
                        }
                        onClick={() =>
                          handleOpenRepository(
                            repository
                          )
                        }
                      >
                        {isOpening ? (
                          <>
                            <LoaderCircle
                              size={15}
                              className="recent-spinner"
                            />
  
                            Opening...
                          </>
                        ) : (
                          <>
                            Open Repository
  
                            <ArrowRight
                              size={15}
                            />
                          </>
                        )}
                      </button>
                    </article>
                  );
                }
              )}
            </div>
          )}
  
  
        {historyStatus ===
          "ready" &&
          repositories.length >
            0 && (
            <div className="recent-history-footer">
              <RefreshCw
                size={13}
              />
  
              Repository history is
              stored persistently by
              CodeLens.
            </div>
          )}
      </section>
    );
  }
  
  
  export default RecentRepositories;