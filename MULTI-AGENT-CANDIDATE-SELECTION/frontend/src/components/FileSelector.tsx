import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { FileText, CheckCircle2, Loader2, RefreshCw } from 'lucide-react';
import { cn } from '../utils/cn';

interface FileInfo {
  id: string;
  filename: string;
  size: number;
  type: string;
  path: string;
}

interface FileSelectorProps {
  title: string;
  endpoint: string;
  selectedFiles: string[];
  onSelectionChange: (fileIds: string[]) => void;
  onFileContentLoad?: (fileId: string, content: string) => void;
  multiple?: boolean;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function FileSelector({
  title,
  endpoint,
  selectedFiles,
  onSelectionChange,
  onFileContentLoad,
  multiple = true,
}: FileSelectorProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingContent, setLoadingContent] = useState<string | null>(null);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error('Failed to fetch files');
      }
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [endpoint]);

  const handleFileToggle = (fileId: string) => {
    if (multiple) {
      if (selectedFiles.includes(fileId)) {
        onSelectionChange(selectedFiles.filter((id) => id !== fileId));
      } else {
        onSelectionChange([...selectedFiles, fileId]);
      }
    } else {
      onSelectionChange([fileId]);
      if (onFileContentLoad) {
        loadFileContent(fileId);
      }
    }
  };

  const loadFileContent = async (fileId: string) => {
    if (!onFileContentLoad) return;
    
    setLoadingContent(fileId);
    try {
      const response = await fetch(`${API_BASE_URL}/api/files/job-offers/${fileId}`);
      if (!response.ok) {
        throw new Error('Failed to load file content');
      }
      const data = await response.json();
      onFileContentLoad(fileId, data.content);
    } catch (error) {
      console.error('Error loading file content:', error);
      alert('Failed to load file content');
    } finally {
      setLoadingContent(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white">{title}</h3>
        <button
          onClick={fetchFiles}
          disabled={loading}
          className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw className={cn('w-5 h-5', loading && 'animate-spin')} />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          <span className="ml-3 text-gray-400">Loading files...</span>
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No files found</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {files.map((file) => {
            const isSelected = selectedFiles.includes(file.id);
            const isLoading = loadingContent === file.id;

            return (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={cn(
                  'flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all',
                  isSelected
                    ? 'bg-blue-500/20 border-2 border-blue-400/50'
                    : 'bg-white/5 border-2 border-transparent hover:bg-white/10'
                )}
                onClick={() => handleFileToggle(file.id)}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div
                    className={cn(
                      'p-2 rounded-lg',
                      isSelected ? 'bg-blue-500/20' : 'bg-gray-700/50'
                    )}
                  >
                    <FileText
                      className={cn(
                        'w-5 h-5',
                        isSelected ? 'text-blue-400' : 'text-gray-400'
                      )}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p
                      className={cn(
                        'text-sm font-medium truncate',
                        isSelected ? 'text-white' : 'text-gray-300'
                      )}
                    >
                      {file.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)} • {file.type.toUpperCase()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                  ) : isSelected ? (
                    <CheckCircle2 className="w-5 h-5 text-blue-400" />
                  ) : null}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {selectedFiles.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 rounded-xl bg-blue-500/10 border border-blue-400/20"
        >
          <p className="text-sm text-blue-400">
            {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}

