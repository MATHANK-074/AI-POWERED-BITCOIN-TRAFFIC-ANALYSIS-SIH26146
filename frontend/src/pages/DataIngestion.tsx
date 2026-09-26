import React, { useState } from 'react';
import { uploadFile } from '../services/api';
import { UploadCloud, CheckCircle2, AlertCircle, FileCode, Clock, ShieldCheck } from 'lucide-react';

export const DataIngestion: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadFile(selectedFile);
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'File ingestion failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-brand-900 flex items-center gap-2">
          <UploadCloud className="w-5 h-5 text-brand-600" />
          Bulk Heterogeneous Data Ingestion
        </h2>
        <p className="text-xs text-content-500 mt-1">
          Upload forensic Bitcoin transaction logs or network traffic metadata (CSV, JSON, XML).
          The ingestion engine handles schema mapping, field normalization, duplicate check, and error logging.
        </p>
      </div>

      {/* Upload Zone */}
      <div className="bg-surface-100 border-2 border-dashed border-surface-400 hover:border-brand-500/50 transition-all rounded-xl p-8 text-center flex flex-col items-center justify-center gap-4">
        <div className="p-4 bg-surface-200 rounded-full text-brand-600">
          <FileCode className="w-8 h-8" />
        </div>
        <div>
          <p className="text-sm font-medium text-brand-900">
            {selectedFile ? selectedFile.name : 'Select CSV, JSON, JSONL, or XML file'}
          </p>
          <p className="text-xs text-content-400 mt-1">Maximum file size chunked automatically</p>
        </div>
        <input
          type="file"
          accept=".csv,.json,.jsonl,.xml"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload-input"
        />
        <div className="flex gap-3">
          <label
            htmlFor="file-upload-input"
            className="px-4 py-2 bg-surface-200 hover:bg-surface-300 text-brand-900 text-xs font-medium rounded-lg cursor-pointer transition-all"
          >
            Browse Files
          </label>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className={`px-5 py-2 text-xs font-medium rounded-lg text-brand-900 shadow-md transition-all ${
              !selectedFile || uploading
                ? 'bg-surface-200 text-content-400 cursor-not-allowed'
                : 'bg-brand-600 hover:bg-brand-500 shadow-brand-200/30'
            }`}
          >
            {uploading ? 'Ingesting & Validating...' : 'Start Ingestion'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-critical-500/10 border border-critical-500 rounded-xl flex items-center gap-3 text-critical-600 text-xs">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Result Report Card */}
      {result && result.ingestion_stats && (
        <div className="bg-surface-100 border border-surface-300 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-surface-300 pb-3">
            <h3 className="text-sm font-semibold text-verified-600 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Ingestion Completed Successfully
            </h3>
            <span className="text-xs font-mono text-content-500 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> {result.ingestion_stats.processing_time_sec}s
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surface-50 p-3 rounded-lg">
              <span className="text-[11px] text-content-500 block">Filename</span>
              <span className="text-xs font-mono font-semibold text-brand-900 truncate block">
                {result.ingestion_stats.filename}
              </span>
            </div>
            <div className="bg-surface-50 p-3 rounded-lg">
              <span className="text-[11px] text-content-500 block">Format</span>
              <span className="text-xs font-mono font-semibold text-brand-600 block">
                {result.ingestion_stats.format}
              </span>
            </div>
            <div className="bg-surface-50 p-3 rounded-lg">
              <span className="text-[11px] text-content-500 block">Valid Records</span>
              <span className="text-xs font-mono font-semibold text-verified-600 block">
                {result.ingestion_stats.valid_records.toLocaleString()}
              </span>
            </div>
            <div className="bg-surface-50 p-3 rounded-lg">
              <span className="text-[11px] text-content-500 block">Rejected Records</span>
              <span className="text-xs font-mono font-semibold text-critical-600 block">
                {result.ingestion_stats.invalid_records.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
