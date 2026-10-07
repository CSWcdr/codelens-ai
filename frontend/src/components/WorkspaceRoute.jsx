import {
    Navigate,
    useLocation,
  } from "react-router-dom";
  
  import { useRepo } from "../context/RepoContext";
  
  function WorkspaceRoute({
    children,
  }) {
    const {
      hasRepository,
    } = useRepo();
  
    const location =
      useLocation();
  
    if (!hasRepository) {
      return (
        <Navigate
          to="/"
          replace
          state={{
            from:
              location.pathname,
          }}
        />
      );
    }
  
    return children;
  }
  
  export default WorkspaceRoute;