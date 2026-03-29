import HistoryTable from "../components/HistoryTable";
import { useHistory } from "../hooks/useHistory";

export default function HistoryPage() {
  const { data, isLoading, isError } = useHistory();
  const entries = data ?? [];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Prediction history
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isLoading
            ? "Loading…"
            : `${entries.length} prediction${entries.length === 1 ? "" : "s"} loaded`}
        </p>
      </div>

      {isError && (
        <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
          Failed to load history. Is the API running?
        </p>
      )}

      <HistoryTable entries={entries} isLoading={isLoading} />
    </div>
  );
}
