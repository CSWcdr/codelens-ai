import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Code2,
  FileCode2,
  GitBranch,
  Layers3,
  LoaderCircle,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  useRepo,
} from "../context/RepoContext";

import RecentRepositories from "../components/RecentRepositories";

import "../styles/landing.css";


function GithubLogo({
  size = 18,
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M12 .7C5.73.7.75 5.68.75 11.95c0 5 3.24 9.24 7.74 10.74.56.1.77-.24.77-.54v-2.1c-3.15.68-3.81-1.34-3.81-1.34-.51-1.31-1.25-1.66-1.25-1.66-1.03-.7.08-.69.08-.69 1.13.08 1.73 1.16 1.73 1.16 1.01 1.73 2.65 1.23 3.3.94.1-.73.39-1.23.72-1.51-2.51-.29-5.15-1.26-5.15-5.59 0-1.24.44-2.25 1.16-3.04-.12-.29-.5-1.44.11-3 0 0 .95-.3 3.09 1.16A10.7 10.7 0 0 1 12 6.1c.96 0 1.92.13 2.82.38 2.14-1.46 3.08-1.16 3.08-1.16.62 1.56.23 2.71.12 3 .72.79 1.15 1.8 1.15 3.04 0 4.35-2.65 5.3-5.17 5.58.41.35.77 1.04.77 2.1v3.11c0 .3.2.65.78.54 4.49-1.5 7.72-5.74 7.72-10.74C23.27 5.68 18.28.7 12 .7Z" />
    </svg>
  );
}


const previewItems = [
  {
    file:
      "src/components/Assistant.jsx",

    language:
      "React",

    question:
      "How does the AI assistant work?",

    answer:
      "The Assistant page sends repository-aware questions through the chat interface and renders answers with relevant code references.",

    code:
`function Assistant() {
  const { repoName } = useRepo();

  return (
    <AppLayout>
      <ChatBox repoName={repoName} />
    </AppLayout>
  );
}`,
  },

  {
    file:
      "src/context/RepoContext.jsx",

    language:
      "React",

    question:
      "Where is repository state stored?",

    answer:
      "RepoContext manages the selected repository and persists analysis information locally so workspace pages survive browser refreshes.",

    code:
`const [analysisData, setAnalysisData] =
  useState(savedRepository.analysisData);

const [analysisStatus, setAnalysisStatus] =
  useState("idle");`,
  },

  {
    file:
      "src/services/api.js",

    language:
      "Axios",

    question:
      "How does the frontend call the backend?",

    answer:
      "The frontend uses Axios to send the GitHub repository URL to the FastAPI repository analysis endpoint.",

    code:
`const response = await api.post(
  "/api/repository/analyze",
  {
    repo_url: repoUrl,
  }
);`,
  },

  {
    file:
      "package.json",

    language:
      "JSON",

    question:
      "What powers the frontend?",

    answer:
      "The interface uses React, Vite, React Router, Lucide icons, and Axios for backend communication.",

    code:
`"dependencies": {
  "axios": "...",
  "lucide-react": "...",
  "react": "...",
  "react-router-dom": "..."
}`,
  },
];


const features = [
  {
    icon:
      BrainCircuit,

    title:
      "Repository Intelligence",

    text:
      "Transform a GitHub repository into structured information about files, technologies, modules, dependencies, and architecture.",
  },

  {
    icon:
      Bot,

    title:
      "Codebase AI Assistant",

    text:
      "Ask natural-language questions about a project and receive answers grounded in the repository instead of generic responses.",
  },

  {
    icon:
      Network,

    title:
      "Architecture Visualization",

    text:
      "Explore component relationships, request flows, data pipelines, and dependency connections through a visual workspace.",
  },

  {
    icon:
      BarChart3,

    title:
      "Engineering Insights",

    text:
      "Surface repository composition, code-health indicators, important modules, dependency information, and AI-generated findings.",
  },

  {
    icon:
      FileCode2,

    title:
      "Source References",

    text:
      "Connect AI responses back to relevant files and code snippets so developers can inspect the original implementation.",
  },

  {
    icon:
      ShieldCheck,

    title:
      "Grounded Analysis",

    text:
      "The backend retrieves real repository information before the AI layer generates repository-specific answers.",
  },
];


function Landing() {
  const navigate =
    useNavigate();

  const {
    analyzeRepository,
    analysisStatus,
  } = useRepo();


  const [
    repoInput,
    setRepoInput,
  ] = useState("");


  const [
    inputError,
    setInputError,
  ] = useState("");


  const [
    activeIndex,
    setActiveIndex,
  ] = useState(0);


  const [
    isVisible,
    setIsVisible,
  ] = useState(true);


  const isAnalyzing =
    analysisStatus ===
    "loading";


  useEffect(() => {
    const interval =
      setInterval(() => {
        setIsVisible(
          false
        );

        setTimeout(() => {
          setActiveIndex(
            (current) =>
              (
                current + 1
              ) %
              previewItems.length
          );

          setIsVisible(
            true
          );
        }, 220);
      }, 2600);

    return () =>
      clearInterval(
        interval
      );
  }, []);


  const handleAnalyze =
    async () => {
      const value =
        repoInput.trim();

      if (!value) {
        setInputError(
          "Enter a GitHub repository URL."
        );

        return;
      }


      const githubRegex =
        /^https?:\/\/(www\.)?github\.com\/[^/]+\/[^/]+\/?$/;


      if (
        !githubRegex.test(
          value
        )
      ) {
        setInputError(
          "Enter a valid GitHub repository URL."
        );

        return;
      }


      setInputError(
        ""
      );


      const result =
        await analyzeRepository(
          value
        );


      if (
        result.success
      ) {
        navigate(
          "/repository"
        );

        return;
      }


      setInputError(
        result.error
      );
    };


  const handleKeyDown = (
    event
  ) => {
    if (
      event.key ===
        "Enter" &&
      !isAnalyzing
    ) {
      handleAnalyze();
    }
  };


  const currentPreview =
    previewItems[
      activeIndex
    ];


  return (
    <div className="landing-page">

      {/* =====================================================
          NAVBAR
      ===================================================== */}

      <header className="landing-navbar">

        <a
          href="#home"
          className="landing-brand"
        >
          <div className="landing-brand-logo">
            C
          </div>

          <div>
            <strong>
              CodeLens AI
            </strong>

            <span>
              Codebase Intelligence
            </span>
          </div>
        </a>


        <nav className="landing-nav-links">

          <a href="#recent">
            Recent
          </a>

          <a href="#features">
            Features
          </a>

          <a href="#about">
            About
          </a>

          <a
            href="https://github.com/CSWcdr"
            target="_blank"
            rel="noreferrer"
            className="landing-github-link"
          >
            <GithubLogo
              size={16}
            />

            GitHub
          </a>

        </nav>

      </header>


      <main>

        {/* =====================================================
            HERO
        ===================================================== */}

        <section
          className="landing-hero"
          id="home"
        >

          <div className="hero-glow hero-glow-one">
          </div>

          <div className="hero-glow hero-glow-two">
          </div>


          <div className="hero-content">

            <div className="hero-badge">
              <Sparkles
                size={13}
              />

              AI-powered codebase intelligence
            </div>


            <h1>
              Understand any codebase

              <span>
                {" "}
                in seconds.
              </span>
            </h1>


            <p className="hero-description">
              Paste a GitHub repository.
              Explore its architecture,
              understand the code, inspect
              dependencies, and ask AI
              anything about the project.
            </p>


            <div className="repo-analyze-wrapper">

              <div
                className={`repo-input-container ${
                  inputError
                    ? "repo-input-error"
                    : ""
                }`}
              >

                <GithubLogo
                  size={19}
                />


                <input
                  type="text"
                  value={
                    repoInput
                  }
                  disabled={
                    isAnalyzing
                  }
                  onChange={(
                    event
                  ) => {
                    setRepoInput(
                      event.target
                        .value
                    );

                    if (
                      inputError
                    ) {
                      setInputError(
                        ""
                      );
                    }
                  }}
                  onKeyDown={
                    handleKeyDown
                  }
                  placeholder="https://github.com/username/repository"
                  aria-label="GitHub repository URL"
                />


                <button
                  type="button"
                  onClick={
                    handleAnalyze
                  }
                  disabled={
                    isAnalyzing
                  }
                >
                  {isAnalyzing ? (
                    <>
                      <LoaderCircle
                        size={16}
                        className="landing-analyze-spinner"
                      />

                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze Repository

                      <ArrowRight
                        size={16}
                      />
                    </>
                  )}
                </button>

              </div>


              {inputError && (
                <div className="repo-error-message">

                  <AlertCircle
                    size={14}
                  />

                  {
                    inputError
                  }

                </div>
              )}


              <div className="hero-input-note">

                <CheckCircle2
                  size={13}
                />

                Public GitHub repositories supported

              </div>

            </div>

          </div>


          {/* ===================================================
              WORKSPACE DEMO
          =================================================== */}

          <div className="landing-demo-wrapper">

            <div className="demo-window">

              <div className="demo-window-header">

                <div className="demo-window-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>


                <div className="demo-window-title">

                  <Code2
                    size={14}
                  />

                  CodeLens AI Workspace

                </div>


                <div className="demo-window-status">
                  <span></span>

                  Demo
                </div>

              </div>


              <div className="demo-body">

                <aside className="demo-files">

                  <div className="demo-files-heading">

                    <GitBranch
                      size={14}
                    />

                    example-project

                  </div>


                  <div className="demo-file-list">

                    {previewItems.map(
                      (
                        item,
                        index
                      ) => (
                        <button
                          type="button"
                          key={
                            item.file
                          }
                          className={
                            activeIndex ===
                            index
                              ? "demo-file active"
                              : "demo-file"
                          }
                          onClick={() => {
                            setIsVisible(
                              false
                            );

                            setTimeout(
                              () => {
                                setActiveIndex(
                                  index
                                );

                                setIsVisible(
                                  true
                                );
                              },
                              180
                            );
                          }}
                        >

                          <FileCode2
                            size={13}
                          />

                          <span>
                            {
                              item.file
                            }
                          </span>

                        </button>
                      )
                    )}

                  </div>

                </aside>


                <div className="demo-ai-panel">

                  <div
                    className={`preview-switch ${
                      isVisible
                        ? "visible"
                        : "hidden"
                    }`}
                  >

                    <div className="demo-question">

                      <div className="demo-avatar">
                        N
                      </div>

                      <div>
                        <span>
                          Developer
                        </span>

                        <p>
                          {
                            currentPreview.question
                          }
                        </p>
                      </div>

                    </div>


                    <div className="demo-answer">

                      <div className="demo-ai-avatar">
                        <Sparkles
                          size={15}
                        />
                      </div>


                      <div className="demo-answer-content">

                        <div className="demo-answer-heading">
                          CodeLens AI

                          <span>
                            Repository Context
                          </span>
                        </div>


                        <p>
                          {
                            currentPreview.answer
                          }
                        </p>


                        <div className="demo-code-block">

                          <div className="demo-code-header">

                            <span>
                              {
                                currentPreview.file
                              }
                            </span>

                            <small>
                              {
                                currentPreview.language
                              }
                            </small>

                          </div>


                          <pre>
                            <code>
                              {
                                currentPreview.code
                              }
                            </code>
                          </pre>

                        </div>

                      </div>

                    </div>

                  </div>


                  <div className="preview-progress">

                    {previewItems.map(
                      (
                        item,
                        index
                      ) => (
                        <button
                          type="button"
                          aria-label={`Preview ${
                            index + 1
                          }`}
                          key={
                            item.file
                          }
                          className={
                            activeIndex ===
                            index
                              ? "active"
                              : ""
                          }
                          onClick={() => {
                            setIsVisible(
                              false
                            );

                            setTimeout(
                              () => {
                                setActiveIndex(
                                  index
                                );

                                setIsVisible(
                                  true
                                );
                              },
                              180
                            );
                          }}
                        >
                        </button>
                      )
                    )}

                  </div>

                </div>

              </div>

            </div>

          </div>

        </section>


        {/* =====================================================
            RECENT REPOSITORIES
        ===================================================== */}

        <RecentRepositories />


        {/* =====================================================
            FEATURES
        ===================================================== */}

        <section
          className="landing-section features-section"
          id="features"
        >

          <div className="section-heading">

            <div className="section-eyebrow">

              <Zap
                size={14}
              />

              PLATFORM FEATURES

            </div>


            <h2>
              Everything you need to
              understand an unfamiliar
              repository.
            </h2>


            <p>
              CodeLens AI combines repository
              analysis, architecture
              visualization, AI-assisted
              exploration, and engineering
              insights inside one developer
              workspace.
            </p>

          </div>


          <div className="features-grid">

            {features.map(
              (
                feature
              ) => {
                const Icon =
                  feature.icon;

                return (
                  <article
                    className="feature-card"
                    key={
                      feature.title
                    }
                  >

                    <div className="feature-icon">

                      <Icon
                        size={21}
                      />

                    </div>


                    <h3>
                      {
                        feature.title
                      }
                    </h3>


                    <p>
                      {
                        feature.text
                      }
                    </p>

                  </article>
                );
              }
            )}

          </div>

        </section>


        {/* =====================================================
            HOW IT WORKS
        ===================================================== */}

        <section className="landing-section workflow-section">

          <div className="section-heading centered">

            <div className="section-eyebrow">

              <Layers3
                size={14}
              />

              HOW IT WORKS

            </div>


            <h2>
              From repository URL to
              codebase intelligence.
            </h2>

          </div>


          <div className="workflow-grid">

            <WorkflowStep
              number="01"
              icon={
                GithubLogo
              }
              title="Paste repository"
              text="Enter the URL of a public GitHub repository."
            />


            <WorkflowArrow />


            <WorkflowStep
              number="02"
              icon={
                Search
              }
              title="Analyze codebase"
              text="CodeLens AI scans repository files, dependencies, structure, and technologies."
            />


            <WorkflowArrow />


            <WorkflowStep
              number="03"
              icon={
                BrainCircuit
              }
              title="Build context"
              text="Repository information becomes structured context for deeper analysis."
            />


            <WorkflowArrow />


            <WorkflowStep
              number="04"
              icon={
                Sparkles
              }
              title="Explore with AI"
              text="Ask questions, inspect architecture, and surface repository insights."
            />

          </div>

        </section>


        {/* =====================================================
            ABOUT
        ===================================================== */}

        <section
          className="landing-section about-section"
          id="about"
        >

          <div className="about-panel">

            <div className="about-copy">

              <div className="section-eyebrow">

                <Code2
                  size={14}
                />

                ABOUT CODELENS AI

              </div>


              <h2>
                Built for developers entering
                unfamiliar codebases.
              </h2>


              <p>
                Understanding a new repository
                usually means jumping between
                folders, documentation,
                configuration files,
                dependencies, and implementation
                details. CodeLens AI brings that
                exploration into one intelligent
                workspace.
              </p>


              <p>
                The completed platform combines
                repository analysis with retrieval
                and AI so answers can be grounded
                in actual source code.
              </p>

            </div>


            <div className="about-visual">

              <div className="about-stack-card">

                <span>
                  01
                </span>

                <div>

                  <strong>
                    Repository
                  </strong>

                  <small>
                    Source code
                  </small>

                </div>

              </div>


              <div className="about-connector">
              </div>


              <div className="about-stack-card highlighted">

                <span>
                  02
                </span>

                <div>

                  <strong>
                    CodeLens Intelligence
                  </strong>

                  <small>
                    Analysis + retrieval
                  </small>

                </div>

              </div>


              <div className="about-connector">
              </div>


              <div className="about-stack-card">

                <span>
                  03
                </span>

                <div>

                  <strong>
                    Developer
                  </strong>

                  <small>
                    Answers + insights
                  </small>

                </div>

              </div>

            </div>

          </div>

        </section>


        {/* =====================================================
            CTA
        ===================================================== */}

        <section className="landing-cta">

          <div className="cta-glow">
          </div>


          <div>

            <Sparkles
              size={20}
            />


            <h2>
              Ready to explore a
              codebase?
            </h2>


            <p>
              Paste a public GitHub
              repository and open the
              CodeLens AI workspace.
            </p>


            <a href="#home">
              Analyze a Repository

              <ArrowRight
                size={16}
              />
            </a>

          </div>

        </section>

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer className="landing-footer">

        <div className="landing-footer-brand">

          <div className="landing-brand-logo">
            C
          </div>


          <div>

            <strong>
              CodeLens AI
            </strong>

            <span>
              AI-powered codebase intelligence
            </span>

          </div>

        </div>


        <div className="landing-footer-links">

          <a href="#recent">
            Recent
          </a>

          <a href="#features">
            Features
          </a>

          <a href="#about">
            About
          </a>

          <a
            href="https://github.com/CSWcdr"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>

        </div>


        <span className="landing-footer-note">
          Built for developers.
        </span>

      </footer>

    </div>
  );
}


function WorkflowStep({
  number,
  icon: Icon,
  title,
  text,
}) {
  return (
    <div className="workflow-step">

      <div className="workflow-step-top">

        <div className="workflow-icon">

          <Icon
            size={20}
          />

        </div>


        <span>
          {number}
        </span>

      </div>


      <h3>
        {title}
      </h3>


      <p>
        {text}
      </p>

    </div>
  );
}


function WorkflowArrow() {
  return (
    <div className="workflow-arrow">

      <ArrowRight
        size={17}
      />

    </div>
  );
}


export default Landing;