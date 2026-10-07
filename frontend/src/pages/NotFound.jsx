import {
    ArrowLeft,
    Home,
    SearchX,
  } from "lucide-react";
  
  import {
    useNavigate,
  } from "react-router-dom";
  
  import "../styles/notfound.css";
  
  function NotFound() {
    const navigate =
      useNavigate();
  
    return (
      <div className="notfound-page">
        <div className="notfound-glow"></div>
  
        <div className="notfound-card">
          <div className="notfound-icon">
            <SearchX size={30} />
          </div>
  
          <p className="notfound-code">
            404
          </p>
  
          <h1>
            Page not found
          </h1>
  
          <p className="notfound-description">
            The page you tried to open does
            not exist in the CodeLens AI
            workspace.
          </p>
  
          <div className="notfound-actions">
            <button
              type="button"
              className="notfound-primary"
              onClick={() =>
                navigate("/")
              }
            >
              <Home size={16} />
  
              Back to Home
            </button>
  
            <button
              type="button"
              className="notfound-secondary"
              onClick={() =>
                navigate(-1)
              }
            >
              <ArrowLeft size={16} />
  
              Go Back
            </button>
          </div>
        </div>
  
        <p className="notfound-footer">
          CodeLens AI • AI-powered
          codebase intelligence
        </p>
      </div>
    );
  }
  
  export default NotFound;