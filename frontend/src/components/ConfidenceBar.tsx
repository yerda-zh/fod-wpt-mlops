import { useEffect, useState } from "react";

interface ConfidenceBarProps {
  confidence: number;
  label: "No object" | "FOD detected";
}

export default function ConfidenceBar({ confidence, label }: ConfidenceBarProps) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const id = requestAnimationFrame(() => setWidth(confidence * 100));
    return () => cancelAnimationFrame(id);
  }, [confidence]);

  const fillColor = label === "No object" ? "bg-green-500" : "bg-red-500";

  return (
    <div className="w-full">
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="font-medium text-gray-700">{label}</span>
        <span className="text-gray-500">{(confidence * 100).toFixed(1)}%</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className={`h-full rounded-full transition-[width] duration-700 ease-out ${fillColor}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}
