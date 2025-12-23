import { motion } from 'framer-motion';
import { Award, TrendingUp, CheckCircle2 } from 'lucide-react';
import { DecisionOutput as DecisionOutputType } from '../types';

interface DecisionOutputProps {
  decision: DecisionOutputType;
}

export default function DecisionOutput({ decision }: DecisionOutputProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.5 }}
      className="mb-12"
    >
      <h2 className="text-2xl font-bold mb-6 text-white">Decision Agent Final Output</h2>
      <div className="glass-strong rounded-2xl p-8 border-2 border-green-400/30 bg-gradient-to-br from-green-500/10 to-emerald-500/10">
        <div className="flex items-start gap-4 mb-6">
          <div className="p-4 rounded-xl bg-green-500/20">
            <Award className="w-8 h-8 text-green-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-white mb-2">Top Candidate Selected</h3>
            <p className="text-xl text-green-400 font-semibold mb-1">
              {decision.topCandidate.name}
            </p>
            <div className="flex items-center gap-4 mt-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <span className="text-3xl font-bold text-green-400">
                  {decision.topCandidate.scores.global.toFixed(1)}
                </span>
                <span className="text-gray-400">/100</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-blue-400" />
                <span className="text-gray-300">
                  Confidence: <span className="font-semibold text-blue-400">{decision.confidence}%</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Profile', value: decision.topCandidate.scores.profile },
            { label: 'Technical', value: decision.topCandidate.scores.technical },
            { label: 'Soft Skills', value: decision.topCandidate.scores.softSkills },
          ].map((item) => (
            <div key={item.label} className="glass rounded-xl p-4 text-center">
              <div className="text-sm text-gray-400 mb-1">{item.label}</div>
              <div className="text-2xl font-bold text-white">{item.value}</div>
            </div>
          ))}
        </div>

        {/* Final Justification */}
        <div className="mt-6 p-6 rounded-xl bg-white/5 border border-white/10">
          <h4 className="text-lg font-semibold text-white mb-3">Final AI Justification</h4>
          <p className="text-gray-300 leading-relaxed">{decision.finalJustification}</p>
        </div>

        {/* Summary Stats */}
        <div className="mt-6 flex items-center justify-between text-sm text-gray-400">
          <span>Total Candidates Evaluated: {decision.totalCandidates}</span>
          <span>Evaluation Completed</span>
        </div>
      </div>
    </motion.section>
  );
}

