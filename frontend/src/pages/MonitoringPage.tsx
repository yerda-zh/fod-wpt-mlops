export default function MonitoringPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Live monitoring</h1>
        <p className="mt-1 text-sm text-gray-500">
          Live metrics from Prometheus and Grafana
        </p>
      </div>
      <iframe
        src="http://107.22.94.101:3000/d/ad6vl6c/my-dashboard?orgId=1&refresh=5s&kiosk"
        width="100%"
        height="700"
        className="rounded-xl border border-gray-200"
        title="Grafana dashboard"
      />
    </div>
  );
}