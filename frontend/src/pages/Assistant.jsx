import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Bot,
  Check,
  Clipboard,
  Code2,
  CornerDownLeft,
  Database,
  FileCode2,
  GitCommitHorizontal,
  LoaderCircle,
  MessageSquare,
  RefreshCw,
  RotateCcw,
  Send,
  Sparkles,
  TerminalSquare,
  User,
} from "lucide-react";

import AppLayout from "../components/AppLayout";

import {
  useRepo,
} from "../context/RepoContext";

import {
  askRepositoryApi,
  getRepositoryIndexStatusApi,
  indexRepositoryApi,
} from "../services/api";

import "../styles/assistant.css";


const SUGGESTED_PROMPTS = [
  "Explain the overall architecture of this repository.",
  "How does authentication work?",
  "How does image generation work?",
  "How is data stored and retrieved?",
  "What are the most important backend routes?",
  "Walk me through the request flow.",
];


function Assistant() {
  const {
    repoName,
    repoUrl,
  } = useRepo();


  const [
    messages,
    setMessages,
  ] = useState([]);


  const [
    input,
    setInput,
  ] = useState("");


  const [
    thinking,
    setThinking,
  ] = useState(false);


  const [
    copiedId,
    setCopiedId,
  ] = useState(null);


  const [
    error,
    setError,
  ] = useState("");


  const [
    indexStatus,
    setIndexStatus,
  ] = useState("checking");


  const [
    indexedChunks,
    setIndexedChunks,
  ] = useState(0);


  const [
    indexingError,
    setIndexingError,
  ] = useState("");


  const [
    commitSha,
    setCommitSha,
  ] = useState("");


  const [
    cached,
    setCached,
  ] = useState(false);


  const [
    staleRepository,
    setStaleRepository,
  ] = useState(false);


  const messagesEndRef =
    useRef(null);


  const textareaRef =
    useRef(null);


  const preparationStartedRef =
    useRef(false);


  const displayName =
    repoName ||
    "Repository";


  const hasMessages =
    messages.length > 0;


  const ragReady =
    indexStatus ===
    "ready";


  const canSend =
    input.trim().length > 0 &&
    !thinking &&
    ragReady &&
    Boolean(
      repoUrl
    );


  const shortCommitSha =
    commitSha
      ? commitSha.slice(
          0,
          8
        )
      : "";


  const welcomeMessage =
    useMemo(
      () => (
        `Ask questions about ${displayName}. ` +
        "CodeLens AI retrieves relevant repository code and generates grounded answers with source references."
      ),
      [displayName]
    );


  useEffect(() => {
    messagesEndRef.current
      ?.scrollIntoView({
        behavior:
          "smooth",
      });
  }, [
    messages,
    thinking,
  ]);


  useEffect(() => {
    if (
      textareaRef.current
    ) {
      textareaRef.current
        .style
        .height =
        "auto";

      textareaRef.current
        .style
        .height =
        `${Math.min(
          textareaRef
            .current
            .scrollHeight,
          180
        )}px`;
    }
  }, [input]);


  useEffect(() => {
    preparationStartedRef.current =
      false;

    setIndexStatus(
      "checking"
    );

    setIndexedChunks(
      0
    );

    setCommitSha(
      ""
    );

    setCached(
      false
    );

    setStaleRepository(
      false
    );

    setIndexingError(
      ""
    );


    if (!repoUrl) {
      setIndexStatus(
        "error"
      );

      setIndexingError(
        "No repository is selected."
      );

      return;
    }


    const prepareRepository =
      async () => {
        try {
          const status =
            await getRepositoryIndexStatusApi(
              repoUrl
            );


          setIndexedChunks(
            status.indexed_chunks ||
            0
          );


          setCommitSha(
            status.commit_sha ||
            ""
          );


          /*
           * CASE 1
           *
           * Repository already indexed
           * and the GitHub commit SHA is
           * still identical.
           *
           * Nothing to rebuild.
           */
          if (
            status.indexed &&
            status.fresh
          ) {
            setCached(
              true
            );

            setStaleRepository(
              false
            );

            setIndexStatus(
              "ready"
            );

            return;
          }


          /*
           * CASE 2
           *
           * Repository has a Chroma
           * collection, but GitHub has
           * changed since it was indexed.
           */
          if (
            status.indexed &&
            !status.fresh
          ) {
            setStaleRepository(
              true
            );

            setCached(
              false
            );

            setIndexStatus(
              "refreshing"
            );
          }


          /*
           * CASE 3
           *
           * Repository has never been
           * indexed before.
           */
          if (
            !status.indexed
          ) {
            setStaleRepository(
              false
            );

            setCached(
              false
            );

            setIndexStatus(
              "indexing"
            );
          }


          if (
            preparationStartedRef
              .current
          ) {
            return;
          }


          preparationStartedRef.current =
            true;


          const result =
            await indexRepositoryApi(
              repoUrl
            );


          setIndexedChunks(
            result.indexed_chunks ||
            0
          );


          setCommitSha(
            result.commit_sha ||
            status.commit_sha ||
            ""
          );


          setCached(
            Boolean(
              result.cached
            )
          );


          setStaleRepository(
            false
          );


          setIndexStatus(
            "ready"
          );

        } catch (
          requestError
        ) {
          let message =
            "Could not prepare this repository for AI questions.";


          if (
            requestError
              .response
              ?.data
              ?.detail
          ) {
            message =
              requestError
                .response
                .data
                .detail;

          } else if (
            requestError.code ===
            "ECONNABORTED"
          ) {
            message =
              "Repository indexing timed out.";

          } else if (
            requestError.message ===
            "Network Error"
          ) {
            message =
              "Could not connect to the CodeLens AI backend.";
          }


          setIndexingError(
            message
          );


          setIndexStatus(
            "error"
          );
        }
      };


    prepareRepository();

  }, [repoUrl]);


  const retryIndexing =
    async () => {
      if (!repoUrl) {
        return;
      }


      setIndexingError(
        ""
      );


      setCached(
        false
      );


      setIndexStatus(
        staleRepository
          ? "refreshing"
          : "indexing"
      );


      try {
        const result =
          await indexRepositoryApi(
            repoUrl
          );


        setIndexedChunks(
          result.indexed_chunks ||
          0
        );


        setCommitSha(
          result.commit_sha ||
          ""
        );


        setCached(
          Boolean(
            result.cached
          )
        );


        setStaleRepository(
          false
        );


        setIndexStatus(
          "ready"
        );

      } catch (
        requestError
      ) {
        let message =
          "Repository indexing failed.";


        if (
          requestError
            .response
            ?.data
            ?.detail
        ) {
          message =
            requestError
              .response
              .data
              .detail;
        }


        setIndexingError(
          message
        );


        setIndexStatus(
          "error"
        );
      }
    };


  const refreshRepository =
    async () => {
      if (
        !repoUrl ||
        thinking
      ) {
        return;
      }


      setIndexingError(
        ""
      );


      setCached(
        false
      );


      setIndexStatus(
        "checking"
      );


      try {
        const status =
          await getRepositoryIndexStatusApi(
            repoUrl
          );


        setIndexedChunks(
          status.indexed_chunks ||
          0
        );


        setCommitSha(
          status.commit_sha ||
          ""
        );


        if (
          status.indexed &&
          status.fresh
        ) {
          setCached(
            true
          );

          setStaleRepository(
            false
          );

          setIndexStatus(
            "ready"
          );

          return;
        }


        setStaleRepository(
          Boolean(
            status.indexed
          )
        );


        setIndexStatus(
          status.indexed
            ? "refreshing"
            : "indexing"
        );


        const result =
          await indexRepositoryApi(
            repoUrl
          );


        setIndexedChunks(
          result.indexed_chunks ||
          0
        );


        setCommitSha(
          result.commit_sha ||
          status.commit_sha ||
          ""
        );


        setCached(
          Boolean(
            result.cached
          )
        );


        setStaleRepository(
          false
        );


        setIndexStatus(
          "ready"
        );

      } catch (
        requestError
      ) {
        const message =
          requestError
            .response
            ?.data
            ?.detail ||
          "Could not refresh repository index.";


        setIndexingError(
          message
        );


        setIndexStatus(
          "error"
        );
      }
    };


  const submitQuestion =
    async (
      questionValue
    ) => {
      const question =
        questionValue.trim();


      if (
        !question ||
        thinking ||
        !ragReady
      ) {
        return;
      }


      if (!repoUrl) {
        setError(
          "No repository is selected."
        );

        return;
      }


      const userMessage = {
        id:
          crypto.randomUUID(),

        role:
          "user",

        content:
          question,

        createdAt:
          new Date(),
      };


      setMessages(
        (current) => [
          ...current,
          userMessage,
        ]
      );


      setInput("");
      setThinking(true);
      setError("");


      try {
        const response =
          await askRepositoryApi(
            repoUrl,
            question,
            6
          );


        const assistantMessage = {
          id:
            crypto.randomUUID(),

          role:
            "assistant",

          content:
            response.answer,

          sources:
            response.sources ||
            [],

          model:
            response.model,

          createdAt:
            new Date(),
        };


        setMessages(
          (current) => [
            ...current,
            assistantMessage,
          ]
        );

      } catch (
        requestError
      ) {
        let message =
          "CodeLens AI could not answer this question.";


        if (
          requestError
            .response
            ?.data
            ?.detail
        ) {
          message =
            requestError
              .response
              .data
              .detail;

        } else if (
          requestError.code ===
          "ECONNABORTED"
        ) {
          message =
            "The AI request timed out.";

        } else if (
          requestError.message ===
          "Network Error"
        ) {
          message =
            "Could not connect to the CodeLens AI backend.";
        }


        setError(
          message
        );


        setMessages(
          (current) => [
            ...current,
            {
              id:
                crypto.randomUUID(),

              role:
                "assistant",

              content:
                "I couldn't complete that request. Please try again.",

              error:
                true,

              createdAt:
                new Date(),
            },
          ]
        );

      } finally {
        setThinking(
          false
        );
      }
    };


  const handleSubmit =
    async (
      event
    ) => {
      event.preventDefault();

      await submitQuestion(
        input
      );
    };


  const handleKeyDown =
    async (
      event
    ) => {
      if (
        event.key ===
          "Enter" &&
        !event.shiftKey
      ) {
        event.preventDefault();

        if (canSend) {
          await submitQuestion(
            input
          );
        }
      }
    };


  const handleSuggestedPrompt =
    async (
      prompt
    ) => {
      await submitQuestion(
        prompt
      );
    };


  const handleCopy =
    async (
      message
    ) => {
      try {
        await navigator
          .clipboard
          .writeText(
            message.content
          );


        setCopiedId(
          message.id
        );


        window.setTimeout(
          () => {
            setCopiedId(
              null
            );
          },
          1600
        );

      } catch {
        setCopiedId(
          null
        );
      }
    };


  const handleNewChat =
    () => {
      setMessages([]);
      setInput("");
      setError("");

      textareaRef.current
        ?.focus();
    };


  return (
    <AppLayout>

      <div className="assistant-page">

        <section className="assistant-header">

          <div>

            <p className="assistant-eyebrow">
              AI CODEBASE ASSISTANT
            </p>

            <h1>
              Ask CodeLens AI
            </h1>

            <p>
              Ask implementation
              questions about{" "}
              <strong>
                {displayName}
              </strong>
              . Answers are grounded
              in the latest indexed
              repository code.
            </p>

          </div>


          <div className="assistant-header-actions">

            <div className="assistant-live-badge">

              {indexStatus ===
              "checking" ? (
                <>
                  <LoaderCircle
                    size={14}
                    className="assistant-spin"
                  />

                  Checking Repository
                </>
              ) : indexStatus ===
                "indexing" ? (
                <>
                  <LoaderCircle
                    size={14}
                    className="assistant-spin"
                  />

                  Indexing Repository
                </>
              ) : indexStatus ===
                "refreshing" ? (
                <>
                  <LoaderCircle
                    size={14}
                    className="assistant-spin"
                  />

                  Updating Index
                </>
              ) : indexStatus ===
                "ready" ? (
                <>
                  <span></span>

                  RAG Connected
                </>
              ) : (
                <>
                  <span></span>

                  RAG Unavailable
                </>
              )}

            </div>


            <button
              type="button"
              className="assistant-new-chat"
              onClick={
                refreshRepository
              }
              disabled={
                indexStatus ===
                  "checking" ||
                indexStatus ===
                  "indexing" ||
                indexStatus ===
                  "refreshing"
              }
            >
              <RefreshCw
                size={15}
              />

              Refresh Repo
            </button>


            <button
              type="button"
              className="assistant-new-chat"
              onClick={
                handleNewChat
              }
            >
              <RotateCcw
                size={15}
              />

              New Chat
            </button>

          </div>

        </section>


        <section className="assistant-shell">

          <div className="assistant-chat-panel">

            <div className="assistant-chat-topbar">

              <div>

                <MessageSquare
                  size={16}
                />

                <span>
                  Repository conversation
                </span>

              </div>


              <span>
                {displayName}
              </span>

            </div>


            <div className="assistant-messages">

              {indexStatus ===
                "checking" && (
                <RepositoryPreparation
                  title="Checking repository freshness"
                  text="CodeLens AI is comparing the current GitHub commit with the stored repository index."
                />
              )}


              {indexStatus ===
                "indexing" && (
                <RepositoryPreparation
                  title="Preparing repository intelligence"
                  text="This repository has not been indexed yet. CodeLens AI is downloading source files, chunking the code, and creating embeddings."
                />
              )}


              {indexStatus ===
                "refreshing" && (
                <RepositoryPreparation
                  title="Repository changes detected"
                  text="The GitHub repository has changed since the previous analysis. CodeLens AI is rebuilding the index so answers use the latest code."
                />
              )}


              {indexStatus ===
                "error" && (
                <RepositoryIndexError
                  message={
                    indexingError
                  }
                  onRetry={
                    retryIndexing
                  }
                />
              )}


              {ragReady &&
                !hasMessages && (
                <AssistantWelcome
                  text={
                    welcomeMessage
                  }
                  onPrompt={
                    handleSuggestedPrompt
                  }
                  disabled={
                    thinking
                  }
                />
              )}


              {ragReady &&
                messages.map(
                  (
                    message
                  ) => (
                    <MessageBubble
                      key={
                        message.id
                      }
                      message={
                        message
                      }
                      copied={
                        copiedId ===
                        message.id
                      }
                      onCopy={() =>
                        handleCopy(
                          message
                        )
                      }
                    />
                  )
                )}


              {thinking &&
                ragReady && (
                  <ThinkingMessage />
                )}


              <div
                ref={
                  messagesEndRef
                }
              />

            </div>


            {error && (
              <div className="assistant-error-banner">

                <span>
                  {error}
                </span>

                <button
                  type="button"
                  onClick={() =>
                    setError("")
                  }
                >
                  Dismiss
                </button>

              </div>
            )}


            <form
              className="assistant-composer"
              onSubmit={
                handleSubmit
              }
            >

              <div className="assistant-composer-box">

                <textarea
                  ref={
                    textareaRef
                  }
                  value={
                    input
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setInput(
                        event
                          .target
                          .value
                      )
                  }
                  onKeyDown={
                    handleKeyDown
                  }
                  placeholder={
                    ragReady
                      ? `Ask about ${displayName}...`
                      : indexStatus ===
                        "refreshing"
                      ? "Updating repository index..."
                      : indexStatus ===
                        "indexing"
                      ? "Repository is being indexed..."
                      : "Preparing AI Assistant..."
                  }
                  rows={1}
                  disabled={
                    thinking ||
                    !ragReady
                  }
                />


                <button
                  type="submit"
                  className="assistant-send-button"
                  disabled={
                    !canSend
                  }
                  aria-label="Send message"
                >
                  {thinking ? (
                    <LoaderCircle
                      size={18}
                      className="assistant-spin"
                    />
                  ) : (
                    <Send
                      size={18}
                    />
                  )}
                </button>

              </div>


              <div className="assistant-composer-meta">

                <span>
                  <CornerDownLeft
                    size={12}
                  />

                  Enter to send
                </span>

                <span>
                  Shift + Enter for
                  new line
                </span>

              </div>

            </form>

          </div>


          <aside className="assistant-side-panel">

            <div className="assistant-side-card">

              <p className="assistant-side-label">
                RAG STATUS
              </p>


              <div className="assistant-status-row">

                <div className="assistant-status-icon">
                  <Database
                    size={16}
                  />
                </div>

                <div>

                  <strong>
                    {indexStatus ===
                    "ready"
                      ? "Repository indexed"
                      : indexStatus ===
                        "refreshing"
                      ? "Refreshing index"
                      : indexStatus ===
                        "indexing"
                      ? "Indexing repository"
                      : indexStatus ===
                        "checking"
                      ? "Checking freshness"
                      : "Index unavailable"}
                  </strong>

                  <span>
                    {indexStatus ===
                    "ready"
                      ? `${indexedChunks} code chunks`
                      : "Chroma vector store"}
                  </span>

                </div>

              </div>


              <div className="assistant-status-row">

                <div className="assistant-status-icon">
                  <GitCommitHorizontal
                    size={16}
                  />
                </div>

                <div>

                  <strong>
                    {shortCommitSha
                      ? shortCommitSha
                      : "Commit pending"}
                  </strong>

                  <span>
                    Latest GitHub commit
                  </span>

                </div>

              </div>


              <div className="assistant-status-row">

                <div className="assistant-status-icon">
                  <Sparkles
                    size={16}
                  />
                </div>

                <div>

                  <strong>
                    {cached &&
                    ragReady
                      ? "Fresh cached index"
                      : ragReady
                      ? "Fresh repository index"
                      : "Hybrid retrieval"}
                  </strong>

                  <span>
                    Semantic +
                    code-aware
                  </span>

                </div>

              </div>


              <div className="assistant-status-row">

                <div className="assistant-status-icon">
                  <Bot
                    size={16}
                  />
                </div>

                <div>

                  <strong>
                    Groq generation
                  </strong>

                  <span>
                    GPT-OSS-120B
                  </span>

                </div>

              </div>

            </div>


            <div className="assistant-side-card">

              <p className="assistant-side-label">
                GOOD QUESTIONS
              </p>


              <div className="assistant-tip-list">

                <span>
                  Explain a feature
                </span>

                <span>
                  Trace an API request
                </span>

                <span>
                  Find database usage
                </span>

                <span>
                  Explain authentication
                </span>

                <span>
                  Understand controllers
                </span>

              </div>

            </div>


            <div className="assistant-side-card assistant-side-note">

              <TerminalSquare
                size={18}
              />

              <div>

                <strong>
                  Repository-aware answers
                </strong>

                <p>
                  CodeLens checks the
                  latest GitHub commit
                  before enabling chat.
                  Changed repositories
                  are automatically
                  re-indexed before
                  answers are generated.
                </p>

              </div>

            </div>

          </aside>

        </section>

      </div>

    </AppLayout>
  );
}


function RepositoryPreparation({
  title,
  text,
}) {
  return (
    <div className="assistant-welcome">

      <div className="assistant-welcome-icon">

        <LoaderCircle
          size={26}
          className="assistant-spin"
        />

      </div>


      <h2>
        {title}
      </h2>


      <p>
        {text}
      </p>

    </div>
  );
}


function RepositoryIndexError({
  message,
  onRetry,
}) {
  return (
    <div className="assistant-welcome">

      <div className="assistant-welcome-icon">

        <Database
          size={25}
        />

      </div>


      <h2>
        Repository preparation failed
      </h2>


      <p>
        {message}
      </p>


      <div className="assistant-suggestions">

        <button
          type="button"
          onClick={
            onRetry
          }
        >

          <RotateCcw
            size={14}
          />

          <span>
            Retry repository preparation
          </span>

        </button>

      </div>

    </div>
  );
}


function AssistantWelcome({
  text,
  onPrompt,
  disabled,
}) {
  return (
    <div className="assistant-welcome">

      <div className="assistant-welcome-icon">

        <Sparkles
          size={25}
        />

      </div>


      <h2>
        Understand your codebase
      </h2>


      <p>
        {text}
      </p>


      <div className="assistant-suggestions">

        {SUGGESTED_PROMPTS.map(
          (
            prompt
          ) => (
            <button
              type="button"
              key={
                prompt
              }
              disabled={
                disabled
              }
              onClick={() =>
                onPrompt(
                  prompt
                )
              }
            >

              <Code2
                size={14}
              />

              <span>
                {prompt}
              </span>

            </button>
          )
        )}

      </div>

    </div>
  );
}


function MessageBubble({
  message,
  copied,
  onCopy,
}) {
  const isAssistant =
    message.role ===
    "assistant";


  return (
    <article
      className={`assistant-message ${
        isAssistant
          ? "assistant"
          : "user"
      } ${
        message.error
          ? "message-error"
          : ""
      }`}
    >

      <div className="assistant-message-avatar">

        {isAssistant ? (
          <Bot
            size={17}
          />
        ) : (
          <User
            size={17}
          />
        )}

      </div>


      <div className="assistant-message-body">

        <div className="assistant-message-heading">

          <div>

            <strong>
              {isAssistant
                ? "CodeLens AI"
                : "You"}
            </strong>


            {isAssistant &&
              message.model && (
                <span>
                  {
                    message.model
                  }
                </span>
              )}

          </div>


          {isAssistant &&
            !message.error && (
              <button
                type="button"
                className="assistant-copy-button"
                onClick={
                  onCopy
                }
              >

                {copied ? (
                  <>
                    <Check
                      size={13}
                    />

                    Copied
                  </>
                ) : (
                  <>
                    <Clipboard
                      size={13}
                    />

                    Copy
                  </>
                )}

              </button>
            )}

        </div>


        <div className="assistant-message-content">

          {isAssistant ? (
            <ReactMarkdown
              remarkPlugins={[
                remarkGfm,
              ]}
            >
              {
                message.content
              }
            </ReactMarkdown>
          ) : (
            <p>
              {
                message.content
              }
            </p>
          )}

        </div>


        {isAssistant &&
          message.sources?.length >
            0 && (
            <SourceList
              sources={
                message.sources
              }
            />
          )}

      </div>

    </article>
  );
}


function SourceList({
  sources,
}) {
  const uniqueSources =
    deduplicateSources(
      sources
    );


  return (
    <div className="assistant-sources">

      <div className="assistant-sources-heading">

        <FileCode2
          size={14}
        />

        <span>
          Sources
        </span>

        <small>
          {
            uniqueSources.length
          }
        </small>

      </div>


      <div className="assistant-source-grid">

        {uniqueSources.map(
          (
            source
          ) => (
            <div
              className="assistant-source-card"
              key={`${source.path}-${source.start_line}-${source.end_line}`}
            >

              <div className="assistant-source-number">
                {
                  source.source_id
                }
              </div>


              <div>

                <strong>
                  {
                    getFileName(
                      source.path
                    )
                  }
                </strong>

                <span>
                  {
                    source.path
                  }
                </span>

                <small>
                  Lines{" "}
                  {
                    source.start_line
                  }
                  –
                  {
                    source.end_line
                  }
                </small>

              </div>

            </div>
          )
        )}

      </div>

    </div>
  );
}


function ThinkingMessage() {
  return (
    <article className="assistant-message assistant">

      <div className="assistant-message-avatar">

        <Bot
          size={17}
        />

      </div>


      <div className="assistant-message-body">

        <div className="assistant-thinking">

          <LoaderCircle
            size={16}
            className="assistant-spin"
          />

          <div>

            <strong>
              Analyzing repository context
            </strong>

            <span>
              Retrieving relevant
              code and generating a
              grounded answer...
            </span>

          </div>

        </div>

      </div>

    </article>
  );
}


function deduplicateSources(
  sources
) {
  const seen =
    new Set();

  const result =
    [];


  for (
    const source
    of sources
  ) {
    const key =
      `${source.path}:` +
      `${source.start_line}:` +
      `${source.end_line}`;


    if (
      seen.has(
        key
      )
    ) {
      continue;
    }


    seen.add(
      key
    );

    result.push(
      source
    );
  }


  return result;
}


function getFileName(
  path
) {
  if (!path) {
    return "Unknown";
  }


  const parts =
    path.split("/");


  return (
    parts[
      parts.length - 1
    ] || path
  );
}


export default Assistant;