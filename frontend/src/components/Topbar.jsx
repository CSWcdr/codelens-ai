import {
    ArrowLeft,
    ExternalLink,
    Menu,
  } from "lucide-react";
  
  import {
    useNavigate,
  } from "react-router-dom";
  
  import {
    useRepo,
  } from "../context/RepoContext";
  
  function Topbar({
    onMenuClick,
  }) {
    const navigate =
      useNavigate();
  
    const {
      repoName,
      repoUrl,
      analysisStatus,
    } = useRepo();
  
    const displayedName =
      repoName ||
      "No repository";
  
    const statusConfig = {
      idle: {
        text:
          "No Repository",
        className:
          "status-idle",
      },
  
      loading: {
        text:
          "Preparing",
        className:
          "status-loading",
      },
  
      pending: {
        text:
          "Awaiting Analysis",
        className:
          "status-pending",
      },
  
      ready: {
        text:
          "Analysis Complete",
        className:
          "status-ready",
      },
  
      error: {
        text:
          "Analysis Failed",
        className:
          "status-error",
      },
    };
  
    const currentStatus =
      statusConfig[
        analysisStatus
      ] ||
      statusConfig.pending;
  
    return (
      <header className="app-topbar">
        <div className="topbar-left">
          <button
            type="button"
            className="mobile-menu-button"
            onClick={
              onMenuClick
            }
            aria-label="Open navigation"
          >
            <Menu size={19} />
          </button>
  
          <button
            className="topbar-back"
            onClick={() =>
              navigate("/")
            }
            type="button"
            aria-label="Back to home"
          >
            <ArrowLeft
              size={17}
            />
          </button>
  
          <div className="topbar-brand">
            <div className="topbar-logo">
              C
            </div>
  
            <div className="topbar-brand-text">
              <h3>
                CodeLens AI
              </h3>
  
              <span>
                {
                  displayedName
                }
              </span>
            </div>
          </div>
        </div>
  
        <div className="topbar-right">
          <div
            className={`analysis-status ${currentStatus.className}`}
          >
            <span
              className={`status-indicator ${currentStatus.className}`}
            ></span>
  
            {
              currentStatus.text
            }
          </div>
  
          {repoUrl && (
            <a
              href={repoUrl}
              target="_blank"
              rel="noreferrer"
              className="github-repo-link"
            >
              <span>
                View Repository
              </span>
  
              <ExternalLink
                size={15}
              />
            </a>
          )}
        </div>
      </header>
    );
  }
  
  export default Topbar;