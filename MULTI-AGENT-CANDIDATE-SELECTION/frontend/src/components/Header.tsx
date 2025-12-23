import { motion } from 'framer-motion';
import { Brain, CheckCircle2 } from 'lucide-react';

interface HeaderProps {
  status: 'running' | 'completed' | 'idle';
}

export default function Header({ status }: HeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-12"
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-10 h-10 text-blue-400" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Multi-Agent Candidate Intelligence System
            </h1>
          </div>
          <p className="text-gray-300 text-lg ml-13">
            AI-powered candidate evaluation & ranking
          </p>
        </div>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: 'spring' }}
        >
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-full glass ${
              status === 'completed'
                ? 'border-green-400/50 bg-green-500/10'
                : status === 'running'
                ? 'border-yellow-400/50 bg-yellow-500/10'
                : 'border-gray-400/50 bg-gray-500/10'
            }`}
          >
            {status === 'completed' ? (
              <CheckCircle2 className="w-5 h-5 text-green-400" />
            ) : status === 'running' ? (
              <div className="w-5 h-5 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full" />
            )}
            <span
              className={`font-semibold ${
                status === 'completed'
                  ? 'text-green-400'
                  : status === 'running'
                  ? 'text-yellow-400'
                  : 'text-gray-400'
              }`}
            >
              {status === 'completed'
                ? 'Completed'
                : status === 'running'
                ? 'Running'
                : 'Ready'}
            </span>
          </div>
        </motion.div>
      </div>
    </motion.header>
  );
}

