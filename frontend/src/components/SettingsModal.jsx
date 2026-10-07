import {
    ExternalLink,
    FolderGit2,
    Moon,
    RotateCcw,
    Settings,
    ShieldCheck,
    X,
  } from "lucide-react";
  
  import {
    useEffect,
  } from "react";
  
  import {
    useNavigate,
  } from "react-router-dom";
  
  import {
    useRepo,
  } from "../context/RepoContext";
  
  import "../styles/settings.css";
  
  function SettingsModal({
    isOpen,
    onClose,
  }) {
    const navigate =
      useNavigate();
  
    const {
      repoName,
      repoUrl,
      clearRepository,
    } = useRepo();
  
    useEffect(() => {
      if (!isOpen) {
        return;
      }
  
      const handleKeyDown = (
        event
      ) => {
        if (
          event.key === "Escape"
        ) {
          onClose();
        }
      };
  
      document.addEventListener(
        "keydown",
        handleKeyDown
      );
  
      document.body.style.overflow =
        "hidden";
  
      return () => {
        document.removeEventListener(
          "keydown",
          handleKeyDown
        );
  
        document.body.style.overflow =
          "";
      };
    }, [
      isOpen,
      onClose,
    ]);
  
    if (!isOpen) {
      return null;
    }
  
    const handleClearRepository =
      () => {
        clearRepository();
  
        onClose();
  
        navigate("/");
      };
  
    return (
      <div
        className="settings-overlay"
        onMouseDown={(event) => {
          if (
            event.target ===
            event.currentTarget
          ) {
            onClose();
          }
        }}
      >
        <div
          className="settings-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="settings-title"
        >
          <div className="settings-header">
            <div>
              <div className="settings-header-icon">
                <Settings
                  size={18}
                />
              </div>
  
              <div>
                <h2 id="settings-title">
                  Settings
                </h2>
  
                <p>
                  Manage your CodeLens
                  workspace.
                </p>
              </div>
            </div>
  
            <button
              type="button"
              className="settings-close"
              onClick={onClose}
              aria-label="Close settings"
            >
              <X size={18} />
            </button>
          </div>
  
          <div className="settings-body">
  
            {/* Repository */}
  
            <section className="settings-section">
              <div className="settings-section-title">
                <FolderGit2
                  size={16}
                />
  
                <div>
                  <strong>
                    Current Repository
                  </strong>
  
                  <span>
                    Repository selected for
                    this workspace
                  </span>
                </div>
              </div>
  
              <div className="settings-repository-card">
                <div>
                  <span>
                    Repository
                  </span>
  
                  <strong>
                    {repoName ||
                      "No repository selected"}
                  </strong>
                </div>
  
                <div>
                  <span>
                    GitHub URL
                  </span>
  
                  {repoUrl ? (
                    <a
                      href={repoUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span>
                        Open repository
                      </span>
  
                      <ExternalLink
                        size={13}
                      />
                    </a>
                  ) : (
                    <strong>
                      —
                    </strong>
                  )}
                </div>
              </div>
            </section>
  
            {/* Appearance */}
  
            <section className="settings-section">
              <div className="settings-section-title">
                <Moon size={16} />
  
                <div>
                  <strong>
                    Appearance
                  </strong>
  
                  <span>
                    Interface appearance
                  </span>
                </div>
              </div>
  
              <div className="settings-option-card">
                <div>
                  <strong>
                    Theme
                  </strong>
  
                  <span>
                    CodeLens currently uses
                    the dark developer theme.
                  </span>
                </div>
  
                <div className="settings-pill">
                  Dark
                </div>
              </div>
            </section>
  
            {/* Privacy */}
  
            <section className="settings-section">
              <div className="settings-section-title">
                <ShieldCheck
                  size={16}
                />
  
                <div>
                  <strong>
                    Repository State
                  </strong>
  
                  <span>
                    Browser workspace
                    preferences
                  </span>
                </div>
              </div>
  
              <div className="settings-option-card">
                <div>
                  <strong>
                    Local persistence
                  </strong>
  
                  <span>
                    The selected repository
                    remains available after
                    page refreshes.
                  </span>
                </div>
  
                <div className="settings-pill active">
                  Enabled
                </div>
              </div>
            </section>
  
            {/* Danger Zone */}
  
            <section className="settings-section danger-section">
              <div className="settings-section-title">
                <RotateCcw
                  size={16}
                />
  
                <div>
                  <strong>
                    Reset Workspace
                  </strong>
  
                  <span>
                    Remove the selected
                    repository
                  </span>
                </div>
              </div>
  
              <div className="settings-danger-card">
                <div>
                  <strong>
                    Clear repository
                  </strong>
  
                  <span>
                    This removes the current
                    repository from the
                    frontend workspace and
                    returns you to the
                    landing page.
                  </span>
                </div>
  
                <button
                  type="button"
                  onClick={
                    handleClearRepository
                  }
                  disabled={!repoUrl}
                >
                  Clear Repository
                </button>
              </div>
            </section>
          </div>
  
          <div className="settings-footer">
            <span>
              CodeLens AI v1.0
            </span>
  
            <button
              type="button"
              onClick={onClose}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  export default SettingsModal;