import { AlertTriangle, CheckCircle } from "lucide-react";

import type { PredictionResponse } from "../types/api";
import ConfidenceBar from "./ConfidenceBar";
import ShapChart from "./ShapChart";

interface ResultCardProps {
  result: PredictionResponse;
  onReset: () => void;
}

export default function ResultCard({ result, onReset }: ResultCardProps) {
  const isFod = result.label === "FOD detected";

  return (
    <div className="w-full rounded-xl border border-gray-200 bg-white p-6 shadow-sm space-y-6">
      {/* Badge */}
      <div
        className={`flex items-center gap-3 rounded-lg px-4 py-3 ${
          isFod ? "bg-red-50" : "bg-green-50"
        }`}
      >
        {isFod ? (
          <AlertTriangle className="h-7 w-7 shrink-0 text-red-500" />
        ) : (
          <CheckCircle className="h-7 w-7 shrink-0 text-green-500" />
        )}
        <span
          className={`text-xl font-semibold ${
            isFod ? "text-red-700" : "text-green-700"
          }`}
        >
          {result.label}
        </span>
      </div>

      {/* Confidence */}
      <ConfidenceBar confidence={result.confidence} label={result.label} />

      {/* SHAP chart */}
      <ShapChart features={result.top_features} />

      {/* Metadata */}
      <div className="flex items-center gap-6 text-sm text-gray-500">
        <span>
          <span className="font-medium text-gray-700">Latency:</span>{" "}
          {result.latency_ms.toFixed(0)}ms
        </span>
        <span>
          <span className="font-medium text-gray-700">Model:</span>{" "}
          {result.model_version}
        </span>
      </div>

      {/* Reset */}
      <button
        onClick={onReset}
        className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
      >
        Run another prediction
      </button>
    </div>
  );
}
