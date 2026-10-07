import axios from "axios";


const rawBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.trim() ||
  "http://127.0.0.1:8000";


const API_BASE_URL =
  rawBaseUrl.endsWith("/")
    ? rawBaseUrl.slice(0, -1)
    : rawBaseUrl;


const api = axios.create({
  baseURL: API_BASE_URL,

  timeout: 300000,

  headers: {
    "Content-Type": "application/json",
  },
});


export const getApiErrorMessage = (error) => {
  if (
    error?.response?.data?.detail
  ) {
    return error.response.data.detail;
  }


  if (
    error?.response?.data?.message
  ) {
    return error.response.data.message;
  }


  if (
    error?.code === "ECONNABORTED"
  ) {
    return (
      "The request took too long. "
      + "Please try again."
    );
  }


  if (
    error?.message === "Network Error"
  ) {
    return (
      "Unable to connect to the CodeLens backend."
    );
  }


  return (
    error?.message
    || "Something went wrong."
  );
};


// =========================================================
// SYSTEM
// =========================================================

export const getHealthApi =
  async () => {
    const response =
      await api.get(
        "/health"
      );

    return response.data;
  };


// =========================================================
// HISTORY
// =========================================================

export const saveRepositoryHistoryApi =
  async (
    repositoryData
  ) => {
    const response =
      await api.post(
        "/api/history",
        {
          repo_url:
            repositoryData.repo_url,

          repo_name:
            repositoryData.repo_name,

          owner:
            repositoryData.owner,

          description:
            repositoryData.description ??
            null,

          primary_language:
            repositoryData.primary_language ??
            null,

          primary_framework:
            repositoryData.primary_framework ??
            null,

          architecture:
            repositoryData.architecture ??
            null,

          default_branch:
            repositoryData.default_branch ??
            null,

          commit_sha:
            repositoryData.commit_sha ??
            null,
        }
      );

    return response.data;
  };


export const getRepositoryHistoryApi =
  async (
    limit = 20
  ) => {
    const response =
      await api.get(
        "/api/history",
        {
          params: {
            limit,
          },
        }
      );

    return response.data;
  };


export const getRepositoryHistoryItemApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.get(
        "/api/history/repository",
        {
          params: {
            repo_url:
              repoUrl,
          },
        }
      );

    return response.data;
  };


export const deleteRepositoryHistoryApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.delete(
        "/api/history/repository",
        {
          params: {
            repo_url:
              repoUrl,
          },
        }
      );

    return response.data;
  };


export const clearRepositoryHistoryApi =
  async () => {
    const response =
      await api.delete(
        "/api/history"
      );

    return response.data;
  };


// =========================================================
// REPOSITORY
// =========================================================

export const analyzeRepositoryApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.post(
        "/api/repository/analyze",
        {
          repo_url:
            repoUrl,
        }
      );


    const repositoryData =
      response.data;


    try {
      await saveRepositoryHistoryApi(
        repositoryData
      );

    } catch (error) {
      /*
       * History should never prevent the repository
       * itself from opening.
       */
      console.warn(
        "Could not save repository history:",
        getApiErrorMessage(
          error
        )
      );
    }


    return repositoryData;
  };


// =========================================================
// ARCHITECTURE
// =========================================================

export const analyzeArchitectureApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.post(
        "/api/architecture/analyze",
        {
          repo_url:
            repoUrl,
        }
      );

    return response.data;
  };


// =========================================================
// INSIGHTS
// =========================================================

export const analyzeInsightsApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.post(
        "/api/insights/analyze",
        {
          repo_url:
            repoUrl,
        }
      );

    return response.data;
  };


// =========================================================
// ASSISTANT STATUS
// =========================================================

export const getRepositoryIndexStatusApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.post(
        "/api/assistant/status",
        {
          repo_url:
            repoUrl,
        }
      );

    return response.data;
  };


// =========================================================
// ASSISTANT INDEX
// =========================================================

export const indexRepositoryApi =
  async (
    repoUrl
  ) => {
    const response =
      await api.post(
        "/api/assistant/index",
        {
          repo_url:
            repoUrl,
        }
      );

    return response.data;
  };


// =========================================================
// ASSISTANT RETRIEVAL
// =========================================================

export const retrieveRepositoryApi =
  async (
    repoUrl,
    question,
    limit = 6
  ) => {
    const response =
      await api.post(
        "/api/assistant/retrieve",
        {
          repo_url:
            repoUrl,

          question,

          limit,
        }
      );

    return response.data;
  };


// =========================================================
// ASSISTANT QUESTION
// =========================================================

export const askRepositoryApi =
  async (
    repoUrl,
    question,
    limit = 6
  ) => {
    const response =
      await api.post(
        "/api/assistant/ask",
        {
          repo_url:
            repoUrl,

          question,

          limit,
        }
      );

    return response.data;
  };


export default api;