import { motion } from 'framer-motion';
import { Upload, FileText, X, Play } from 'lucide-react';
import { useRef, useState } from 'react';
import { UploadedCV } from '../types';
import { cn } from '../utils/cn';
import FileSelector from './FileSelector';

interface FileUploadProps {
  onFilesUploaded: (files: File[]) => void;
  uploadedCVs: UploadedCV[];
  onRemoveCV: (id: string) => void;
  onProcessResumes?: (fileIds: string[]) => void;
  selectedResumeIds?: string[];
}

export default function FileUpload({ 
  onFilesUploaded, 
  uploadedCVs, 
  onRemoveCV,
  onProcessResumes,
  selectedResumeIds = [],
  onResumeSelectionChange
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === 'application/pdf' || file.type === 'text/plain' || file.name.endsWith('.txt')
    );

    if (files.length > 0) {
      onFilesUploaded(files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onFilesUploaded(files);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-4">
      {/* File Selector from DATA/raw */}
      <FileSelector
        title="Select Resumes from DATA/raw"
        endpoint="/api/files/resumes"
        selectedFiles={selectedResumeIds}
        onSelectionChange={(fileIds) => {
          if (onResumeSelectionChange) {
            onResumeSelectionChange(fileIds);
          }
        }}
        multiple={true}
      />
      
      {selectedResumeIds.length > 0 && onProcessResumes && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-4"
        >
          <button
            onClick={() => onProcessResumes(selectedResumeIds)}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all"
          >
            <Play className="w-5 h-5" />
            <span>Process {selectedResumeIds.length} Selected Resume{selectedResumeIds.length !== 1 ? 's' : ''}</span>
          </button>
        </motion.div>
      )}
      
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-white/10"></div>
        <span className="text-xs text-gray-500">OR</span>
        <div className="flex-1 h-px bg-white/10"></div>
      </div>
      
      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn(
          'glass rounded-2xl p-8 border-2 border-dashed transition-all duration-300 cursor-pointer',
          isDragging
            ? 'border-blue-400 bg-blue-500/10 scale-105'
            : 'border-gray-500/50 hover:border-blue-400/50'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />
        <div className="flex flex-col items-center justify-center text-center">
          <div className="p-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 mb-4">
            <Upload className="w-8 h-8 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">
            {isDragging ? 'Drop CVs here' : 'Upload CVs'}
          </h3>
          <p className="text-sm text-gray-400 mb-2">
            Drag and drop CV files here, or click to browse
          </p>
          <p className="text-xs text-gray-500">
            Supported formats: PDF, TXT (Max 10MB per file)
          </p>
        </div>
      </motion.div>

      {/* Uploaded Files List */}
      {uploadedCVs.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">
            Uploaded CVs ({uploadedCVs.length})
          </h3>
          <div className="space-y-2">
            {uploadedCVs.map((cv) => (
              <motion.div
                key={cv.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{cv.name}</p>
                    <p className="text-xs text-gray-400">
                      {formatFileSize(cv.size)} • {cv.uploadDate.toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={cn(
                      'px-2 py-1 rounded-full text-xs font-semibold',
                      cv.status === 'processed' && 'bg-green-500/20 text-green-400',
                      cv.status === 'processing' && 'bg-yellow-500/20 text-yellow-400',
                      cv.status === 'uploaded' && 'bg-blue-500/20 text-blue-400'
                    )}
                  >
                    {cv.status}
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveCV(cv.id);
                  }}
                  className="ml-4 p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

