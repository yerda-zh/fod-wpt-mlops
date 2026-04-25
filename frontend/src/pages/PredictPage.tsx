import { useState } from "react";
import DropZone from "../components/DropZone";
import ResultCard from "../components/ResultCard";
import { usePredict } from "../hooks/usePredict";
import type { PredictionResponse } from "../types/api";

export default function PredictPage() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { mutate, isPending } = usePredict();

  function handleFile(file: File) {
    setError(null);
    mutate(file, {
      onSuccess: (data) => setResult(data),
      onError: () => {
        setError("Prediction failed. Please check your file and try again.");
      },
    });
  }

  function handleReset() {
    setResult(null);
    setError(null);
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Foreign Object Detection (FOD) system</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload a transmitter coil current waveform to analyse
        </p>
      </div>

      {/* Project Description */}
      <div className="rounded-xl border border-gray-300 bg-gray-50 p-5 space-y-4">
        <p className="text-sm text-gray-600 leading-relaxed">
          This system analyzes transmitter coil current waveforms from wireless
          power transfer (WPT) systems to detect metallic foreign objects (keys,
          coins, wrenches) that cause overheating. No additional hardware
          required — the existing coil current signal is the only input.
        </p>
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "F1 Score", value: "0.9783" },
            { label: "ROC AUC", value: "0.9966" },
            { label: "Training samples", value: "3,680" },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="rounded-lg bg-white border border-gray-200 px-4 py-3 text-center"
            >
              <p className="text-lg font-semibold text-gray-900">{value}</p>
              <p className="mt-0.5 text-xs text-gray-500">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {result ? (
        <ResultCard result={result} onReset={handleReset} />
      ) : (
        <>
          <DropZone onFile={handleFile} isLoading={isPending} />
          {error && (
            <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </p>
          )}
        </>
      )}

      {/* Author */}
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-5 flex items-start gap-4">
        <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold text-sm">
          Y
        </div>
        <div className="min-w-0 flex-1 space-y-1">
          <p className="text-sm font-semibold text-gray-900">Yerdaulet Zhumay</p>
          <p className="text-xs text-gray-500">Software & ML Engineer</p>
          <p className="text-xs text-gray-600 leading-relaxed">
            Built this system as part of research on foreign object detection in
            wireless power transfer systems for EV charging at Nazarbayev University.
          </p>
          <div className="flex gap-3 pt-1">
            <a
              href="https://github.com/yerda-zh"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 transition-colors"
            >
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12z" />
              </svg>
              GitHub
            </a>
            <a
              href="https://www.linkedin.com/in/yerdaulet-zh"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-blue-600 transition-colors"
            >
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
              LinkedIn
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
