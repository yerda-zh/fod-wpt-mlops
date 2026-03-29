import { Upload } from "lucide-react";
import { useDropzone } from "react-dropzone";

interface DropZoneProps {
  onFile: (file: File) => void;
  isLoading: boolean;
}

export default function DropZone({ onFile, isLoading }: DropZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "text/csv": [".csv"] },
    disabled: isLoading,
    multiple: false,
    onDropAccepted: ([file]) => onFile(file),
  });

  return (
    <div
      {...getRootProps()}
      className={[
        "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-8 py-16 transition-colors",
        isLoading
          ? "cursor-not-allowed border-gray-200 bg-gray-50"
          : isDragActive
            ? "border-blue-400 bg-blue-50 cursor-copy"
            : "border-gray-300 bg-white cursor-pointer hover:border-blue-400 hover:bg-blue-50",
      ].join(" ")}
    >
      <input {...getInputProps()} />

      {isLoading ? (
        <>
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-500" />
          <p className="text-sm font-medium text-gray-500">Analysing waveform...</p>
        </>
      ) : (
        <>
          <Upload className="h-10 w-10 text-gray-400" />
          <div className="text-center">
            <p className="text-sm font-medium text-gray-700">
              Drop your waveform CSV here
            </p>
            <p className="mt-1 text-xs text-gray-400">or click to browse</p>
          </div>
        </>
      )}
    </div>
  );
}
