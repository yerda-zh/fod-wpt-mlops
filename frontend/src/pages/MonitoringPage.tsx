export default function MonitoringPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Live monitoring</h1>
      </div>

      <iframe
        src="http://localhost:3000/d/ad489v8/my-dashboard?kiosk=1&refresh=5s"
        width="100%"
        height="700"
        className="rounded-xl border border-gray-200"
        title="Grafana dashboard"
      />

      <p className="text-sm text-gray-400">
        Grafana dashboard — start docker compose to view live metrics.
      </p>
    </div>
  );
}
