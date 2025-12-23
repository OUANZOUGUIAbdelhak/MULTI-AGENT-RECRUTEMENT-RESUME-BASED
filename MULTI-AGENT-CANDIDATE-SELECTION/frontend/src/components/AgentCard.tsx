import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { Agent, AgentStatus } from '../types';
import { cn } from '../utils/cn';

interface AgentCardProps {
  agent: Agent;
  index: number;
  icon: LucideIcon;
}

export default function AgentCard({ agent, index, icon: Icon }: AgentCardProps) {
  const getStatusColor = (status: AgentStatus) => {
    switch (status) {
      case 'completed':
        return 'border-green-400/50 bg-green-500/10 text-green-400';
      case 'processing':
        return 'border-yellow-400/50 bg-yellow-500/10 text-yellow-400 animate-pulse-slow';
      default:
        return 'border-gray-500/50 bg-gray-500/10 text-gray-400';
    }
  };

  const getStatusText = (status: AgentStatus) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'processing':
        return 'Processing';
      default:
        return 'Waiting';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      className={cn(
        'glass rounded-2xl p-6 hover:scale-105 transition-all duration-300',
        agent.status === 'processing' && 'ring-2 ring-yellow-400/50 shadow-lg shadow-yellow-400/20'
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20">
            <Icon className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">{agent.name}</h3>
            <p className="text-sm text-gray-400">{agent.role}</p>
          </div>
        </div>
        <div
          className={cn(
            'px-3 py-1 rounded-full text-xs font-semibold border',
            getStatusColor(agent.status)
          )}
        >
          {getStatusText(agent.status)}
        </div>
      </div>

      <p className="text-sm text-gray-300 mb-4">{agent.description}</p>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-400">
          <span>Progress</span>
          <span>{agent.progress}%</span>
        </div>
        <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${agent.progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className={cn(
              'h-full rounded-full transition-colors',
              agent.status === 'completed' && 'bg-gradient-to-r from-green-400 to-emerald-500',
              agent.status === 'processing' && 'bg-gradient-to-r from-yellow-400 to-orange-500',
              agent.status === 'waiting' && 'bg-gray-600'
            )}
          />
        </div>
      </div>
    </motion.div>
  );
}

