import { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";
const RESOLUTIONS = ["480p", "720p", "1080p"];

interface LadderItem {
  resolution: string;
  width: number;
  height: number;
  file_size_mb: number;
  download_url?: string;
}

interface Result {
  success?: boolean;
  message?: string;
  codec?: string;
  ladder?: LadderItem[];
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [codec, setCodec] = useState("h265");
  const [mode, setMode] = useState<"convert" | "ladder">("convert");
  const [resolutions, setResolutions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
  };

  const handleResolutionChange = (res: string) => {
    setResolutions((prev) =>
      prev.includes(res) ? prev.filter((r) => r !== res) : [...prev, res]
    );
  };

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const getFilename = (response: Response, defaultName: string): string => {
    const contentDisposition = response.headers.get("Content-Disposition");
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?(.+)"?/i);
      if (match?.[1]) return match[1];
    }
    return defaultName;
  };

  const handleConvert = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/video/convert/${codec}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Conversion failed: ${await response.text()}`);
      }

      const filename = getFilename(
        response,
        `converted_${codec}.${
          codec === "vp8" || codec === "vp9" ? "webm" : "mp4"
        }`
      );
      const blob = await response.blob();
      downloadFile(blob, filename);
      setResult({ success: true, message: "File downloaded!" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleLadder = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }
    if (resolutions.length === 0) {
      setError("Please select at least one resolution");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("codec", codec);
    formData.append("resolutions", resolutions.join(","));

    try {
      const response = await fetch(`${API_URL}/api/video/encoding-ladder`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Encoding ladder failed");
      }

      setResult(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Video Processing API</h1>

      <div className="section">
        <h2>Upload Video</h2>
        <input type="file" accept="video/*" onChange={handleFileChange} />
        {file && <p>Selected: {file.name}</p>}
      </div>

      <div className="section">
        <h2>Codec</h2>
        <select value={codec} onChange={(e) => setCodec(e.target.value)}>
          <option value="h265">H265</option>
          <option value="av1">AV1</option>
          <option value="vp8">VP8</option>
          <option value="vp9">VP9</option>
        </select>
      </div>

      <div className="section">
        <h2>Mode</h2>
        <div>
          <label>
            <input
              type="radio"
              value="convert"
              checked={mode === "convert"}
              onChange={() => setMode("convert")}
            />
            Convert
          </label>
          <label>
            <input
              type="radio"
              value="ladder"
              checked={mode === "ladder"}
              onChange={() => setMode("ladder")}
            />
            Encoding Ladder
          </label>
        </div>
      </div>

      {mode === "ladder" && (
        <div className="section">
          <h2>Resolutions</h2>
          {RESOLUTIONS.map((res) => (
            <label key={res}>
              <input
                type="checkbox"
                checked={resolutions.includes(res)}
                onChange={() => handleResolutionChange(res)}
              />
              {res}
            </label>
          ))}
        </div>
      )}

      <div className="section">
        <button
          onClick={mode === "convert" ? handleConvert : handleLadder}
          disabled={loading}
        >
          {loading
            ? "Processing..."
            : mode === "convert"
            ? "Convert"
            : "Create Ladder"}
        </button>
      </div>

      {error && <div className="error">Error: {error}</div>}

      {result && (
        <div className="result">
          <h2>Result</h2>
          {result.ladder ? (
            <div>
              <p>Codec: {result.codec}</p>
              <ul>
                {result.ladder.map((item, idx) => (
                  <li key={idx} className="ladder-item">
                    <div className="ladder-info">
                      {item.resolution} ({item.width}x{item.height}) -{" "}
                      {item.file_size_mb} MB
                    </div>
                    {item.download_url && (
                      <button
                        className="download-btn"
                        onClick={() => window.open(item.download_url, "_blank")}
                      >
                        Display
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p>{result.message || "Success!"}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
