from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)


from config import (
    APP_NAME,
    APP_VERSION,
    CORS_ORIGINS,
    ENVIRONMENT,
    GITHUB_TOKEN,
    GROQ_API_KEY,
)


from routes import (
    architecture,
    assistant,
    history,
    insights,
    repository,
)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "AI-powered GitHub repository intelligence API "
        "for repository analysis, architecture discovery, "
        "engineering insights, repository-grounded AI, "
        "and persistent repository history."
    ),
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=
        CORS_ORIGINS,

    allow_credentials=
        True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    repository.router
)


app.include_router(
    architecture.router
)


app.include_router(
    assistant.router
)


app.include_router(
    insights.router
)


app.include_router(
    history.router
)


# =========================================================
# ROOT
# =========================================================

@app.get(
    "/",
    tags=["System"],
)
async def root():
    return {
        "name":
            APP_NAME,

        "version":
            APP_VERSION,

        "environment":
            ENVIRONMENT,

        "status":
            "running",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get(
    "/health",
    tags=["System"],
)
async def health():
    return {
        "status":
            "healthy",

        "application":
            APP_NAME,

        "version":
            APP_VERSION,

        "environment":
            ENVIRONMENT,

        "services": {
            "github": {
                "configured":
                    bool(
                        GITHUB_TOKEN
                    )
            },

            "groq": {
                "configured":
                    bool(
                        GROQ_API_KEY
                    )
            },
        },
    }