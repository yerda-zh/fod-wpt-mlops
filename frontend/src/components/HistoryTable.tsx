import { useState } from "react";

import type { HistoryEntry } from "../types/api";

interface HistoryTableProps {
  entries: HistoryEntry[];
  isLoading: boolean;
}

type Filter = "All" | "No object" | "FOD detected";

function relativeTime(isoString: string): string {
  const normalized = isoString.replace(" ", "T");
  const diffMs = Date.now() - new Date(normalized).getTime();
  const secs = Math.floor(diffMs / 1000);
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins} min${mins === 1 ? "" : "s"} ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} hr${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

const FILTERS: Filter[] = ["All", "No object", "FOD detected"];

export default function HistoryTable({ entries, isLoading }: HistoryTableProps) {
  const [filter, setFilter] = useState<Filter>("All");

  const visible =
    filter === "All" ? entries : entries.filter((e) => e.label === filter);

  return (
    <div className="w-full space-y-4">
      {/* Filter buttons */}
      <div className="flex gap-2">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === f
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200 bg-white text-sm">
          <thead className="bg-gray-50">
            <tr>
              {["Timestamp", "Result", "Confidence", "Latency", "Model"].map(
                (col) => (
                  <th
                    key={col}
                    className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500"
                  >
                    {col}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 5 }).map((__, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 w-full animate-pulse rounded bg-gray-100" />
                    </td>
                  ))}
                </tr>
              ))
            ) : visible.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-10 text-center text-sm text-gray-400"
                >
                  No predictions yet
                </td>
              </tr>
            ) : (
              visible.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="whitespace-nowrap px-4 py-3 text-gray-500">
                    {relativeTime(entry.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        entry.label === "FOD detected"
                          ? "bg-red-100 text-red-700"
                          : "bg-green-100 text-green-700"
                      }`}
                    >
                      {entry.label}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {(entry.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {entry.latency_ms.toFixed(0)}ms
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {entry.model_version}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
