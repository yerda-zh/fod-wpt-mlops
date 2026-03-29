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
        <h1 className="text-2xl font-semibold text-gray-900">FOD Detection</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload a transmitter coil current waveform to analyse
        </p>
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
    </div>
  );
}
