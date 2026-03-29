import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { TopFeature } from "../types/api";

interface ShapChartProps {
  features: TopFeature[];
}

export default function ShapChart({ features }: ShapChartProps) {
  if (features.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No SHAP data available</p>
    );
  }

  const data = features.map((f) => ({
    name: f.name,
    value: Math.abs(f.shap_value),
    raw: f.shap_value,
  }));

  return (
    <div className="w-full">
      <p className="mb-3 text-sm font-medium text-gray-700">
        Feature contributions
      </p>
      <ResponsiveContainer width="100%" height={features.length * 48}>
        <BarChart layout="vertical" data={data} margin={{ left: 8, right: 48, top: 0, bottom: 0 }}>
          <XAxis
            type="number"
            tickFormatter={(v: number) => v.toFixed(3)}
            tick={{ fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={140}
            tick={{ fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(_value, _name, item) => {
              const raw = (item as { payload: { raw: number } }).payload.raw;
              return [raw.toFixed(3), "SHAP value"];
            }}
            cursor={{ fill: "rgba(0,0,0,0.04)" }}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.raw >= 0 ? "#3b82f6" : "#ef4444"}
              />
            ))}
            <LabelList
              dataKey="raw"
              position="right"
              formatter={(v) => (v as number).toFixed(3)}
              style={{ fontSize: 11, fill: "#6b7280" }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
