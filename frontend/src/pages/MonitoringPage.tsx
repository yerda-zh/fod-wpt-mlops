import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";

interface DriftStatus {
  date: string;
  report_available: boolean;
  drift_detected: boolean | null;
  report_url: string | null;
  predictions_count: number;
}

export default function MonitoringPage() {
  const { data: drift, isLoading: driftLoading } = useQuery<DriftStatus>({
    queryKey: ["drift"],
    queryFn: () => api.get("/drift/latest").then((r) => r.data),
    refetchInterval: 60000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Live monitoring</h1>
        <p className="mt-1 text-sm text-gray-500">
          Live metrics from Prometheus and Grafana
        </p>
      </div>

      {/* Drift detection card */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900">Drift detection</h2>

        {driftLoading || !drift ? (
          <p className="mt-3 text-sm text-gray-400">Loading drift status…</p>
        ) : (
          <dl className="mt-3 space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <dt className="w-36 shrink-0 text-gray-500">Predictions today</dt>
              <dd className="font-medium text-gray-900">{drift.predictions_count}</dd>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <dt className="w-36 shrink-0 text-gray-500">Report status</dt>
              <dd className="flex items-center gap-2">
                {drift.report_available ? (
                  <>
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-gray-900">
                      Report available for {drift.date}
                    </span>
                    {drift.report_url && (
                      <a
                        href={drift.report_url}
                        target="_blank"
                        rel="noreferrer"
                        className="ml-1 text-indigo-600 underline hover:text-indigo-800"
                      >
                        View report
                      </a>
                    )}
                  </>
                ) : (
                  <>
                    <span className="h-2 w-2 rounded-full bg-gray-300" />
                    <span className="text-gray-500">
                      No report yet for today — runs nightly at midnight UTC
                    </span>
                  </>
                )}
              </dd>
            </div>
          </dl>
        )}
      </div>

      <iframe
        src="http://107.22.94.101:3000/d/ad6vl6c/my-dashboard?orgId=1&refresh=5s&kiosk&liveNow=false"
        width="100%"
        height="700"
        className="rounded-xl border border-gray-200"
        title="Grafana dashboard"
      />
    </div>
  );
}