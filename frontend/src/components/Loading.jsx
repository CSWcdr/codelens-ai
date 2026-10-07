import {
    LoaderCircle,
  } from "lucide-react";
  
  function Loading({
    title =
      "Preparing repository",
    text =
      "CodeLens AI is preparing the repository workspace.",
  }) {
    return (
      <div className="repo-loading">
        <div className="repo-loading-icon">
          <LoaderCircle
            size={22}
          />
        </div>
  
        <div>
          <strong>
            {title}
          </strong>
  
          <span>
            {text}
          </span>
        </div>
      </div>
    );
  }
  
  export default Loading;