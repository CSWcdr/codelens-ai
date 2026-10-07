export const suggestedQuestions = [
    "Explain the project architecture",
    "Where is authentication handled?",
    "Where are API calls made?",
    "Explain the folder structure",
  ];
  
  export const mockResponses = [
    {
      keywords: ["authentication", "auth", "login", "token"],
      answer:
        "Authentication appears to be handled through the application's authentication middleware and related route logic. Protected requests pass through validation before accessing restricted functionality.",
      sources: [
        "src/middleware/auth.js",
        "src/routes/auth.js",
      ],
      code: `export function authenticate(req, res, next) {
    const token = req.headers.authorization;
  
    if (!token) {
      return res.status(401).json({
        message: "Unauthorized"
      });
    }
  
    next();
  }`,
    },
  
    {
      keywords: ["architecture", "structure", "project"],
      answer:
        "The project follows a modular architecture. The application entry point loads the main application shell, which connects routing, reusable components, pages, and service logic.",
      sources: [
        "src/main.jsx",
        "src/App.jsx",
        "src/components/AppLayout.jsx",
      ],
      code: `main.jsx
     ↓
  App.jsx
     ↓
  Routes
     ├── Repository
     ├── Architecture
     ├── Assistant
     └── Insights`,
    },
  
    {
      keywords: ["api", "request", "axios", "backend"],
      answer:
        "API communication is handled through the service layer. Frontend components send requests to backend endpoints and consume the returned JSON responses.",
      sources: [
        "src/services/api.js",
        "src/pages/Repository.jsx",
      ],
      code: `const response = await axios.get(
    "/api/repository"
  );
  
  return response.data;`,
    },
  
    {
      keywords: ["folder", "directory", "files"],
      answer:
        "The repository is organized into pages, reusable components, styles, shared context, and supporting utilities. This keeps page-level functionality separate from reusable interface logic.",
      sources: [
        "src/pages/",
        "src/components/",
        "src/styles/",
        "src/context/",
      ],
      code: `src/
  ├── components/
  ├── context/
  ├── data/
  ├── pages/
  ├── styles/
  ├── App.jsx
  └── main.jsx`,
    },
  ];
  
  export const defaultResponse = {
    answer:
      "I found relevant code areas for your question. Once the backend repository analysis is connected, CodeLens AI will retrieve the exact files and generate an answer grounded in the selected repository.",
    sources: [
      "Repository analysis pending",
    ],
    code: null,
  };
  
  export function getMockResponse(question) {
    const normalizedQuestion = question.toLowerCase();
  
    const match = mockResponses.find((response) =>
      response.keywords.some((keyword) =>
        normalizedQuestion.includes(keyword)
      )
    );
  
    return match || defaultResponse;
  }