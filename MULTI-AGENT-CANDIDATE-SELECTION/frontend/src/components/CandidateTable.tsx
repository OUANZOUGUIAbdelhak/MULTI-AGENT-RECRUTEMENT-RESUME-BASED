import { motion } from 'framer-motion';
import { ArrowUpDown, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { CandidateDetails, RecommendationLevel } from '../types';
import { cn } from '../utils/cn';

interface CandidateTableProps {
  candidates: CandidateDetails[];
  onCandidateClick: (candidate: CandidateDetails) => void;
  expandedId: string | null;
}

export default function CandidateTable({
  candidates,
  onCandidateClick,
  expandedId,
}: CandidateTableProps) {
  const [sortBy, setSortBy] = useState<'score' | 'name'>('score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const sortedCandidates = [...candidates].sort((a, b) => {
    if (sortBy === 'score') {
      return sortOrder === 'desc'
        ? b.scores.global - a.scores.global
        : a.scores.global - b.scores.global;
    } else {
      return sortOrder === 'desc'
        ? b.name.localeCompare(a.name)
        : a.name.localeCompare(b.name);
    }
  });

  const handleSort = (field: 'score' | 'name') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getRecommendationBadge = (level: RecommendationLevel) => {
    const styles = {
      'strongly-recommended': 'bg-green-500/20 border-green-400/50 text-green-400',
      'recommended': 'bg-blue-500/20 border-blue-400/50 text-blue-400',
      'not-recommended': 'bg-red-500/20 border-red-400/50 text-red-400',
    };

    const labels = {
      'strongly-recommended': 'Strongly Recommended',
      'recommended': 'Recommended',
      'not-recommended': 'Not Recommended',
    };

    return (
      <span
        className={cn(
          'px-3 py-1 rounded-full text-xs font-semibold border',
          styles[level]
        )}
      >
        {labels[level]}
      </span>
    );
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-400';
    if (score >= 75) return 'text-blue-400';
    if (score >= 65) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold mb-6 text-white">Candidate Evaluation Results</h2>
      <div className="glass rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  <button
                    onClick={() => handleSort('name')}
                    className="flex items-center gap-2 hover:text-white transition-colors"
                  >
                    Candidate
                    <ArrowUpDown className="w-4 h-4" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  <button
                    onClick={() => handleSort('score')}
                    className="flex items-center gap-2 hover:text-white transition-colors"
                  >
                    Global Score
                    <ArrowUpDown className="w-4 h-4" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  Profile Score
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  Technical Score
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  Soft Skills Score
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  Recommendation
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                  Details
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedCandidates.map((candidate, index) => {
                const isExpanded = expandedId === candidate.id;
                return (
                  <motion.tr
                    key={candidate.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
                    onClick={() => onCandidateClick(candidate)}
                  >
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">{candidate.name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className={cn('text-lg font-bold', getScoreColor(candidate.scores.global))}>
                          {candidate.scores.global.toFixed(1)}
                        </span>
                        <div className="flex-1 h-2 bg-gray-700/50 rounded-full overflow-hidden max-w-[100px]">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${candidate.scores.global}%` }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                            className={cn(
                              'h-full rounded-full',
                              candidate.scores.global >= 85 && 'bg-gradient-to-r from-green-400 to-emerald-500',
                              candidate.scores.global >= 75 && candidate.scores.global < 85 && 'bg-gradient-to-r from-blue-400 to-cyan-500',
                              candidate.scores.global >= 65 && candidate.scores.global < 75 && 'bg-gradient-to-r from-yellow-400 to-orange-500',
                              candidate.scores.global < 65 && 'bg-gradient-to-r from-red-400 to-pink-500'
                            )}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn('font-semibold', getScoreColor(candidate.scores.profile))}>
                        {candidate.scores.profile}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn('font-semibold', getScoreColor(candidate.scores.technical))}>
                        {candidate.scores.technical}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn('font-semibold', getScoreColor(candidate.scores.softSkills))}>
                        {candidate.scores.softSkills}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {getRecommendationBadge(candidate.recommendation)}
                    </td>
                    <td className="px-6 py-4">
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

