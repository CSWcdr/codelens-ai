import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import Landing from "./pages/Landing";
import Repository from "./pages/Repository";
import Architecture from "./pages/Architecture";
import Assistant from "./pages/Assistant";
import Insights from "./pages/Insights";
import NotFound from "./pages/NotFound";

import WorkspaceRoute from "./components/WorkspaceRoute";

import {
  RepoProvider,
} from "./context/RepoContext";

function App() {
  return (
    <RepoProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              <Landing />
            }
          />

          <Route
            path="/repository"
            element={
              <WorkspaceRoute>
                <Repository />
              </WorkspaceRoute>
            }
          />

          <Route
            path="/architecture"
            element={
              <WorkspaceRoute>
                <Architecture />
              </WorkspaceRoute>
            }
          />

          <Route
            path="/assistant"
            element={
              <WorkspaceRoute>
                <Assistant />
              </WorkspaceRoute>
            }
          />

          <Route
            path="/insights"
            element={
              <WorkspaceRoute>
                <Insights />
              </WorkspaceRoute>
            }
          />

          <Route
            path="*"
            element={
              <NotFound />
            }
          />
        </Routes>
      </BrowserRouter>
    </RepoProvider>
  );
}

export default App;