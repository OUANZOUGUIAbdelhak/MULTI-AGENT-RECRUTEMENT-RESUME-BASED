import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Loader2, FileText, Scissors, Database, CheckCircle2, XCircle } from 'lucide-react';
import { cn } from '../utils/cn';

interface IndexBuildProgressProps {
  buildId: string | null;
  onComplete?: () => void;
}

interface ProgressData {
  status: 'running' | 'completed' | 'error';
  step: string;
  progress: number;
  current_file?: string;
  total_files: number;
  processed_files: number;
  total_chunks: number;
  processed_chunks: number;
  message: string;
  error?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function IndexBuildProgress({ buildId, onComplete }: IndexBuildProgressProps) {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    if (!buildId) {
      setProgress(null);
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    let pollInterval: NodeJS.Timeout;

    const pollProgress = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/index-build-progress/${buildId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch progress');
        }
        const data = await response.json();
        setProgress(data);

        if (data.status === 'completed' || data.status === 'error') {
          setIsPolling(false);
          if (data.status === 'completed' && onComplete) {
            setTimeout(onComplete, 2000);
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
        setIsPolling(false);
      }
    };

    // Poll immediately, then every second
    pollProgress();
    pollInterval = setInterval(pollProgress, 1000);

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [buildId, onComplete]);

  if (!buildId || !progress) {
    return null;
  }

  const getStepIcon = (step: string) => {
    switch (step) {
      case 'loading':
        return <FileText className="w-5 h-5" />;
      case 'splitting':
        return <Scissors className="w-5 h-5" />;
      case 'embedding':
        return <Loader2 className="w-5 h-5 animate-spin" />;
      case 'setup_chromadb':
        return <Database className="w-5 h-5" />;
      case 'finalizing':
      case 'completed':
        return <CheckCircle2 className="w-5 h-5" />;
      default:
        return <Loader2 className="w-5 h-5 animate-spin" />;
    }
  };

  const getStepLabel = (step: string) => {
    switch (step) {
      case 'initializing':
        return 'Initializing';
      case 'loading':
        return 'Loading Documents';
      case 'configuring':
        return 'Configuring Metadata';
      case 'splitting':
        return 'Splitting Documents';
      case 'setup_chromadb':
        return 'Setting Up Database';
      case 'embedding':
        return 'Creating Embeddings';
      case 'finalizing':
        return 'Finalizing';
      case 'completed':
        return 'Completed';
      default:
        return step;
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="glass-strong rounded-2xl p-6 border-2 border-blue-400/30 mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            {progress.status === 'error' ? (
              <XCircle className="w-6 h-6 text-red-400" />
            ) : progress.status === 'completed' ? (
              <CheckCircle2 className="w-6 h-6 text-green-400" />
            ) : (
              <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
            )}
            Building RAG Index
          </h3>
          <span
            className={cn(
              'px-3 py-1 rounded-full text-sm font-semibold',
              progress.status === 'completed' && 'bg-green-500/20 text-green-400',
              progress.status === 'error' && 'bg-red-500/20 text-red-400',
              progress.status === 'running' && 'bg-blue-500/20 text-blue-400'
            )}
          >
            {progress.status === 'completed' ? 'Completed' : progress.status === 'error' ? 'Error' : 'Processing'}
          </span>
        </div>

        {/* Main Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-300 mb-2">
            <span>{getStepLabel(progress.step)}</span>
            <span>{progress.progress}%</span>
          </div>
          <div className="h-3 bg-gray-700/50 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress.progress}%` }}
              transition={{ duration: 0.3 }}
              className={cn(
                'h-full rounded-full transition-colors',
                progress.status === 'completed' && 'bg-gradient-to-r from-green-400 to-emerald-500',
                progress.status === 'error' && 'bg-gradient-to-r from-red-400 to-pink-500',
                progress.status === 'running' && 'bg-gradient-to-r from-blue-400 to-purple-500'
              )}
            />
          </div>
        </div>

        {/* Status Message */}
        <p className="text-sm text-gray-300 mb-4">{progress.message}</p>

        {/* Detailed Stats */}
        {progress.status === 'running' && (
          <div className="grid grid-cols-2 gap-4 mt-4">
            {progress.total_files > 0 && (
              <div className="glass rounded-xl p-3">
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-4 h-4 text-blue-400" />
                  <span className="text-xs text-gray-400">Documents</span>
                </div>
                <div className="text-lg font-bold text-white">
                  {progress.processed_files} / {progress.total_files}
                </div>
              </div>
            )}
            {progress.total_chunks > 0 && (
              <div className="glass rounded-xl p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Scissors className="w-4 h-4 text-purple-400" />
                  <span className="text-xs text-gray-400">Chunks</span>
                </div>
                <div className="text-lg font-bold text-white">
                  {progress.processed_chunks || 'Processing...'}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Message */}
        {progress.status === 'error' && progress.error && (
          <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-400/20">
            <p className="text-sm text-red-400">{progress.error}</p>
          </div>
        )}

        {/* Success Message */}
        {progress.status === 'completed' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-3 rounded-xl bg-green-500/10 border border-green-400/20"
          >
            <p className="text-sm text-green-400">
              ✅ Index built successfully! {progress.processed_files} documents processed.
            </p>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

