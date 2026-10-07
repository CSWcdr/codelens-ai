import {
    BarChart3,
    FolderTree,
    LayoutDashboard,
    MessageSquare,
    Network,
    Settings,
    X,
  } from "lucide-react";
  
  import {
    NavLink,
  } from "react-router-dom";
  
  import {
    useRepo,
  } from "../context/RepoContext";
  
  function Sidebar({
    isOpen,
    onClose,
    onSettingsClick,
  }) {
    const {
      repoName,
    } = useRepo();
  
    const displayedName =
      repoName || "No repository";
  
    const menuItems = [
      {
        name: "Overview",
        path: "/repository",
        icon: LayoutDashboard,
      },
      {
        name: "Architecture",
        path: "/architecture",
        icon: Network,
      },
      {
        name: "AI Assistant",
        path: "/assistant",
        icon: MessageSquare,
      },
      {
        name: "Insights",
        path: "/insights",
        icon: BarChart3,
      },
    ];
  
    return (
      <aside
        className={`app-sidebar ${
          isOpen
            ? "sidebar-open"
            : ""
        }`}
      >
        <div className="sidebar-mobile-header">
          <div>
            <span className="sidebar-mobile-logo">
              C
            </span>
  
            <strong>
              CodeLens AI
            </strong>
          </div>
  
          <button
            type="button"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <X size={19} />
          </button>
        </div>
  
        <div className="sidebar-repository">
          <p className="sidebar-label">
            CURRENT REPOSITORY
          </p>
  
          <div className="sidebar-repo-name">
            <FolderTree size={17} />
  
            <span
              title={displayedName}
            >
              {displayedName}
            </span>
          </div>
        </div>
  
        <nav className="sidebar-navigation">
          <p className="sidebar-label">
            WORKSPACE
          </p>
  
          {menuItems.map(
            (item) => {
              const Icon =
                item.icon;
  
              return (
                <NavLink
                  key={item.name}
                  to={item.path}
                  onClick={onClose}
                  className={({
                    isActive,
                  }) =>
                    isActive
                      ? "sidebar-link sidebar-link-active"
                      : "sidebar-link"
                  }
                >
                  <Icon size={18} />
  
                  <span>
                    {item.name}
                  </span>
                </NavLink>
              );
            }
          )}
        </nav>
  
        <div className="sidebar-bottom">
          <button
            type="button"
            className="sidebar-settings-button"
            onClick={
              onSettingsClick
            }
          >
            <Settings size={17} />
  
            <span>
              Settings
            </span>
          </button>
  
          <div className="sidebar-version">
            <span>
              CodeLens AI
            </span>
  
            <small>
              v1.0
            </small>
          </div>
        </div>
      </aside>
    );
  }
  
  export default Sidebar;