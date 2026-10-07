import {
    Bot,
    Check,
    Copy,
    FileCode2,
    RotateCcw,
    Send,
    Sparkles,
    User,
  } from "lucide-react";
  
  import {
    useEffect,
    useRef,
    useState,
  } from "react";
  
  import {
    getMockResponse,
    suggestedQuestions,
  } from "../data/assistantMock";
  
  import {
    useRepo,
  } from "../context/RepoContext";
  
  function ChatBox() {
    const {
      repoName,
    } = useRepo();
  
    const displayedName =
      repoName || "this repository";
  
    const createInitialMessage =
      () => ({
        id: Date.now(),
        role: "assistant",
        answer: `I’m ready to help you explore ${displayedName}. Ask me about the architecture, folder structure, dependencies, components, APIs, or how a part of the codebase works.`,
        sources: [],
        code: null,
      });
  
    const [
      messages,
      setMessages,
    ] = useState([
      createInitialMessage(),
    ]);
  
    const [
      input,
      setInput,
    ] = useState("");
  
    const [
      isThinking,
      setIsThinking,
    ] = useState(false);
  
    const [
      inputFocused,
      setInputFocused,
    ] = useState(false);
  
    const [
      copiedMessageId,
      setCopiedMessageId,
    ] = useState(null);
  
    const messagesEndRef =
      useRef(null);
  
    const textareaRef =
      useRef(null);
  
  
    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }, [
      messages,
      isThinking,
    ]);
  
  
    const sendMessage = async (
      question
    ) => {
      const cleanQuestion =
        question.trim();
  
      if (
        !cleanQuestion ||
        isThinking
      ) {
        return;
      }
  
      const userMessage = {
        id: Date.now(),
        role: "user",
        text: cleanQuestion,
      };
  
      setMessages(
        (currentMessages) => [
          ...currentMessages,
          userMessage,
        ]
      );
  
      setInput("");
      setIsThinking(true);
  
      if (
        textareaRef.current
      ) {
        textareaRef.current.style.height =
          "40px";
      }
  
      try {
        await new Promise(
          (resolve) => {
            setTimeout(
              resolve,
              650
            );
          }
        );
  
        const response =
          getMockResponse(
            cleanQuestion
          );
  
        const assistantMessage = {
          id:
            Date.now() + 1,
          role: "assistant",
          answer:
            response?.answer ||
            "I found repository context related to your question.",
          sources:
            Array.isArray(
              response?.sources
            )
              ? response.sources
              : [],
          code:
            response?.code || null,
        };
  
        setMessages(
          (currentMessages) => [
            ...currentMessages,
            assistantMessage,
          ]
        );
      } catch {
        const errorMessage = {
          id:
            Date.now() + 1,
          role: "error",
          text:
            "Something went wrong while preparing the response. Please try again.",
        };
  
        setMessages(
          (currentMessages) => [
            ...currentMessages,
            errorMessage,
          ]
        );
      } finally {
        setIsThinking(false);
      }
    };
  
  
    const handleSubmit = () => {
      sendMessage(input);
    };
  
  
    const handleKeyDown = (
      event
    ) => {
      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {
        event.preventDefault();
  
        handleSubmit();
      }
    };
  
  
    const handleTextareaChange = (
      event
    ) => {
      setInput(
        event.target.value
      );
  
      event.target.style.height =
        "40px";
  
      event.target.style.height =
        `${Math.min(
          event.target.scrollHeight,
          130
        )}px`;
    };
  
  
    const handleNewChat = () => {
      setMessages([
        createInitialMessage(),
      ]);
  
      setInput("");
      setIsThinking(false);
      setCopiedMessageId(null);
  
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 50);
    };
  
  
    const handleCopy = async (
      message
    ) => {
      if (!message.code) {
        return;
      }
  
      const codeText =
        typeof message.code ===
        "string"
          ? message.code
          : message.code.code ||
            message.code.content ||
            "";
  
      if (!codeText) {
        return;
      }
  
      try {
        await navigator.clipboard.writeText(
          codeText
        );
  
        setCopiedMessageId(
          message.id
        );
  
        setTimeout(() => {
          setCopiedMessageId(
            null
          );
        }, 1500);
      } catch {
        setCopiedMessageId(
          null
        );
      }
    };
  
  
    const renderCode = (
      message
    ) => {
      if (!message.code) {
        return null;
      }
  
      const codeText =
        typeof message.code ===
        "string"
          ? message.code
          : message.code.code ||
            message.code.content ||
            "";
  
      const filename =
        typeof message.code ===
        "object"
          ? message.code.file ||
            message.code.filename ||
            "Referenced code"
          : "Referenced code";
  
      if (!codeText) {
        return null;
      }
  
      const copied =
        copiedMessageId ===
        message.id;
  
      return (
        <div className="code-reference">
          <div className="code-reference-header">
            <span>
              <FileCode2
                size={13}
              />
  
              {filename}
            </span>
  
            <button
              type="button"
              onClick={() =>
                handleCopy(
                  message
                )
              }
              aria-label="Copy code"
              title="Copy code"
            >
              {copied ? (
                <Check
                  size={14}
                />
              ) : (
                <Copy
                  size={14}
                />
              )}
            </button>
          </div>
  
          <pre>
            <code>
              {codeText}
            </code>
          </pre>
        </div>
      );
    };
  
  
    return (
      <div className="chat-panel">
  
        {/* =====================
            CHAT HEADER
            ===================== */}
  
        <div className="chat-topbar">
          <div>
            <span className="chat-status-dot"></span>
  
            Repository Assistant
          </div>
  
          <button
            type="button"
            onClick={
              handleNewChat
            }
          >
            <RotateCcw
              size={12}
            />
  
            New Chat
          </button>
        </div>
  
  
        {/* =====================
            MESSAGES
            ===================== */}
  
        <div className="chat-messages">
          {messages.map(
            (message) => {
  
              if (
                message.role ===
                "user"
              ) {
                return (
                  <div
                    className="message user-message"
                    key={
                      message.id
                    }
                  >
                    <div className="message-content">
                      <span className="message-name">
                        You
                      </span>
  
                      <div className="message-bubble">
                        <p>
                          {
                            message.text
                          }
                        </p>
                      </div>
                    </div>
  
                    <div className="message-avatar user-avatar">
                      <User
                        size={15}
                      />
                    </div>
                  </div>
                );
              }
  
  
              if (
                message.role ===
                "error"
              ) {
                return (
                  <div
                    className="message"
                    key={
                      message.id
                    }
                  >
                    <div className="message-avatar ai-avatar">
                      <Bot
                        size={15}
                      />
                    </div>
  
                    <div className="message-content">
                      <div className="message-heading-row">
                        <span className="message-name">
                          CodeLens AI
                        </span>
  
                        <span className="ai-badge">
                          Error
                        </span>
                      </div>
  
                      <div className="message-bubble ai-bubble">
                        <p>
                          {
                            message.text
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                );
              }
  
  
              return (
                <div
                  className="message"
                  key={
                    message.id
                  }
                >
                  <div className="message-avatar ai-avatar">
                    <Sparkles
                      size={15}
                    />
                  </div>
  
                  <div className="message-content">
                    <div className="message-heading-row">
                      <span className="message-name">
                        CodeLens AI
                      </span>
  
                      <span className="ai-badge">
                        <Sparkles
                          size={9}
                        />
  
                        Repository Context
                      </span>
                    </div>
  
                    <div className="message-bubble ai-bubble">
                      <p>
                        {
                          message.answer
                        }
                      </p>
  
                      {renderCode(
                        message
                      )}
  
                      {message.sources
                        ?.length >
                        0 && (
                        <div className="source-links">
                          <span>
                            Sources
                          </span>
  
                          {message.sources.map(
                            (
                              source,
                              index
                            ) => (
                              <button
                                type="button"
                                key={`${source}-${index}`}
                              >
                                <FileCode2
                                  size={10}
                                />
  
                                {
                                  source
                                }
                              </button>
                            )
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            }
          )}
  
  
          {isThinking && (
            <div className="message">
              <div className="message-avatar ai-avatar">
                <Sparkles
                  size={15}
                />
              </div>
  
              <div className="message-content">
                <div className="message-heading-row">
                  <span className="message-name">
                    CodeLens AI
                  </span>
  
                  <span className="ai-badge">
                    Thinking
                  </span>
                </div>
  
                <div className="thinking-bubble">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
  
  
          <div
            ref={
              messagesEndRef
            }
          ></div>
        </div>
  
  
        {/* =====================
            INPUT
            ===================== */}
  
        <div className="chat-input-area">
          <div className="suggested-prompts">
            {suggestedQuestions.map(
              (question) => (
                <button
                  type="button"
                  key={question}
                  onClick={() =>
                    sendMessage(
                      question
                    )
                  }
                  disabled={
                    isThinking
                  }
                >
                  {question}
                </button>
              )
            )}
          </div>
  
          <div
            className={`chat-input ${
              inputFocused
                ? "chat-input-active"
                : ""
            }`}
          >
            <textarea
              ref={
                textareaRef
              }
              value={input}
              onChange={
                handleTextareaChange
              }
              onKeyDown={
                handleKeyDown
              }
              onFocus={() =>
                setInputFocused(
                  true
                )
              }
              onBlur={() =>
                setInputFocused(
                  false
                )
              }
              placeholder={`Ask anything about ${displayedName}...`}
              rows={1}
            ></textarea>
  
            <button
              type="button"
              className="send-button"
              onClick={
                handleSubmit
              }
              disabled={
                !input.trim() ||
                isThinking
              }
              aria-label="Send message"
            >
              <Send
                size={16}
              />
            </button>
          </div>
  
          <p>
            Enter to send • Shift + Enter
            for a new line
          </p>
        </div>
      </div>
    );
  }
  
  export default ChatBox;