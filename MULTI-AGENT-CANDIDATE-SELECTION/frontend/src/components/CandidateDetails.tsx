import { motion, AnimatePresence } from 'framer-motion';
import { CandidateDetails as CandidateDetailsType } from '../types';
import { cn } from '../utils/cn';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';

interface CandidateDetailsProps {
  candidate: CandidateDetailsType | null;
}

export default function CandidateDetails({ candidate }: CandidateDetailsProps) {
  if (!candidate) return null;

  const radarData = [
    { category: 'Profile', value: candidate.radarData.profile, fullMark: 100 },
    { category: 'Technical', value: candidate.radarData.technical, fullMark: 100 },
    { category: 'Soft Skills', value: candidate.radarData.softSkills, fullMark: 100 },
    { category: 'Experience', value: candidate.radarData.experience, fullMark: 100 },
    { category: 'Education', value: candidate.radarData.education, fullMark: 100 },
    { category: 'Certifications', value: candidate.radarData.certifications, fullMark: 100 },
  ];

  return (
    <AnimatePresence>
      {candidate && (
        <motion.section
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-12"
        >
          <div className="glass-strong rounded-2xl p-6">
            <h2 className="text-2xl font-bold mb-6 text-white">
              Detailed Breakdown: {candidate.name}
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Score Breakdown */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-300 mb-4">Score Breakdown</h3>
                {[
                  { label: 'Profile Score', value: candidate.scores.profile, color: 'blue' },
                  { label: 'Technical Score', value: candidate.scores.technical, color: 'purple' },
                  { label: 'Soft Skills Score', value: candidate.scores.softSkills, color: 'green' },
                ].map((item) => (
                  <div key={item.label} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">{item.label}</span>
                      <span className="font-semibold text-white">{item.value}/100</span>
                    </div>
                    <div className="h-3 bg-gray-700/50 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.value}%` }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className={cn(
                          'h-full rounded-full',
                          item.color === 'blue' && 'bg-gradient-to-r from-blue-400 to-cyan-500',
                          item.color === 'purple' && 'bg-gradient-to-r from-purple-400 to-pink-500',
                          item.color === 'green' && 'bg-gradient-to-r from-green-400 to-emerald-500'
                        )}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Radar Chart */}
              <div>
                <h3 className="text-lg font-semibold text-gray-300 mb-4">Skills Radar</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#ffffff20" />
                    <PolarAngleAxis
                      dataKey="category"
                      tick={{ fill: '#ffffff', fontSize: 12 }}
                    />
                    <PolarRadiusAxis
                      angle={90}
                      domain={[0, 100]}
                      tick={{ fill: '#ffffff60', fontSize: 10 }}
                    />
                    <Radar
                      name="Candidate"
                      dataKey="value"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Justification */}
            <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/20">
              <h3 className="text-lg font-semibold text-white mb-2">AI-Generated Justification</h3>
              <p className="text-gray-300 leading-relaxed">{candidate.aiJustification}</p>
            </div>
          </div>
        </motion.section>
      )}
    </AnimatePresence>
  );
}

