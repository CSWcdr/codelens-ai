import { useState } from "react";

import Topbar from "./Topbar";
import Sidebar from "./Sidebar";
import Footer from "./Footer";
import SettingsModal from "./SettingsModal";

import "../styles/layout.css";

function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [settingsOpen, setSettingsOpen] =
    useState(false);

  const openSidebar = () => {
    setSidebarOpen(true);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  const openSettings = () => {
    setSidebarOpen(false);
    setSettingsOpen(true);
  };

  const closeSettings = () => {
    setSettingsOpen(false);
  };

  return (
    <div className="app-shell">
      <Topbar
        onMenuClick={openSidebar}
      />

      <div className="app-body">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={closeSidebar}
          onSettingsClick={openSettings}
        />

        {sidebarOpen && (
          <button
            type="button"
            className="sidebar-backdrop"
            onClick={closeSidebar}
            aria-label="Close sidebar"
          ></button>
        )}

        <div className="app-content-wrapper">
          <main className="app-content">
            {children}
          </main>

          <Footer />
        </div>
      </div>

      <SettingsModal
        isOpen={settingsOpen}
        onClose={closeSettings}
      />
    </div>
  );
}

export default AppLayout;