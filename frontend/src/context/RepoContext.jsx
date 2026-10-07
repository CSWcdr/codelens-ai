import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  analyzeRepositoryApi,
} from "../services/api";

const RepoContext =
  createContext(null);

const STORAGE_KEY =
  "codelens_repository";

function getSavedRepository() {
  try {
    const saved =
      localStorage.getItem(
        STORAGE_KEY
      );

    if (!saved) {
      return {
        repoUrl: "",
        repoName: "",
        analysisData: null,
      };
    }

    const parsed =
      JSON.parse(saved);

    return {
      repoUrl:
        parsed.repoUrl || "",

      repoName:
        parsed.repoName || "",

      analysisData:
        parsed.analysisData || null,
    };
  } catch {
    return {
      repoUrl: "",
      repoName: "",
      analysisData: null,
    };
  }
}

export function RepoProvider({
  children,
}) {
  const savedRepository =
    getSavedRepository();

  const [
    repoUrl,
    setRepoUrl,
  ] = useState(
    savedRepository.repoUrl
  );

  const [
    repoName,
    setRepoName,
  ] = useState(
    savedRepository.repoName
  );

  const [
    analysisData,
    setAnalysisData,
  ] = useState(
    savedRepository.analysisData
  );

  const [
    analysisStatus,
    setAnalysisStatus,
  ] = useState(
    savedRepository.analysisData
      ? "ready"
      : savedRepository.repoUrl
      ? "pending"
      : "idle"
  );

  const [
    analysisError,
    setAnalysisError,
  ] = useState("");

  useEffect(() => {
    if (!repoUrl) {
      localStorage.removeItem(
        STORAGE_KEY
      );

      return;
    }

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        repoUrl,
        repoName,
        analysisData,
      })
    );
  }, [
    repoUrl,
    repoName,
    analysisData,
  ]);

  const analyzeRepository =
    async (url) => {
      const cleanedUrl =
        url
          .trim()
          .replace(/\/$/, "");

      const parts =
        cleanedUrl.split("/");

      let temporaryName =
        parts[
          parts.length - 1
        ] || "Repository";

      if (
        temporaryName.endsWith(
          ".git"
        )
      ) {
        temporaryName =
          temporaryName.slice(
            0,
            -4
          );
      }

      setRepoUrl(cleanedUrl);

      setRepoName(
        temporaryName
      );

      setAnalysisData(null);

      setAnalysisError("");

      setAnalysisStatus(
        "loading"
      );

      try {
        const data =
          await analyzeRepositoryApi(
            cleanedUrl
          );

        setRepoUrl(
          data.repo_url ||
            cleanedUrl
        );

        setRepoName(
          data.repo_name ||
            temporaryName
        );

        setAnalysisData(data);

        setAnalysisStatus(
          "ready"
        );

        return {
          success: true,
          data,
        };
      } catch (error) {
        let message =
          "Could not analyze this repository.";

        if (
          error.response?.data
            ?.detail
        ) {
          message =
            error.response.data.detail;
        } else if (
          error.code ===
          "ECONNABORTED"
        ) {
          message =
            "Repository analysis timed out.";
        } else if (
          error.message ===
          "Network Error"
        ) {
          message =
            "Could not connect to the CodeLens AI backend.";
        }

        setAnalysisError(
          message
        );

        setAnalysisStatus(
          "error"
        );

        return {
          success: false,
          error: message,
        };
      }
    };

  const clearRepository =
    () => {
      setRepoUrl("");
      setRepoName("");

      setAnalysisData(null);

      setAnalysisStatus(
        "idle"
      );

      setAnalysisError("");

      localStorage.removeItem(
        STORAGE_KEY
      );
    };

  const markAnalysisLoading =
    () => {
      setAnalysisError("");

      setAnalysisStatus(
        "loading"
      );
    };

  const markAnalysisPending =
    () => {
      setAnalysisError("");

      setAnalysisStatus(
        "pending"
      );
    };

  const markAnalysisReady =
    () => {
      setAnalysisError("");

      setAnalysisStatus(
        "ready"
      );
    };

  const markAnalysisError = (
    message =
      "Repository analysis failed."
  ) => {
    setAnalysisError(
      message
    );

    setAnalysisStatus(
      "error"
    );
  };

  const hasRepository =
    Boolean(
      repoUrl &&
      repoName
    );

  const value =
    useMemo(
      () => ({
        repoUrl,
        repoName,

        hasRepository,

        analysisData,
        analysisStatus,
        analysisError,

        analyzeRepository,
        clearRepository,

        markAnalysisLoading,
        markAnalysisPending,
        markAnalysisReady,
        markAnalysisError,
      }),
      [
        repoUrl,
        repoName,

        hasRepository,

        analysisData,
        analysisStatus,
        analysisError,
      ]
    );

  return (
    <RepoContext.Provider
      value={value}
    >
      {children}
    </RepoContext.Provider>
  );
}

export function useRepo() {
  const context =
    useContext(
      RepoContext
    );

  if (!context) {
    throw new Error(
      "useRepo must be used inside RepoProvider."
    );
  }

  return context;
}