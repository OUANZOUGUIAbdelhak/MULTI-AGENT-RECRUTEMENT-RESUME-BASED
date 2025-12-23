import { motion } from 'framer-motion';
import { Play, Loader2, CheckCircle2 } from 'lucide-react';
import { JobOffer } from '../types';

interface EvaluationControlProps {
  jobOffer: JobOffer | null;
  cvCount: number;
  selectedResumeCount?: number;
  isEvaluating: boolean;
  onStartEvaluation: () => void;
}

export default function EvaluationControl({
  jobOffer,
  cvCount,
  selectedResumeCount = 0,
  isEvaluating,
  onStartEvaluation,
}: EvaluationControlProps) {
  const totalCVs = cvCount + selectedResumeCount;
  const canStart = jobOffer !== null && totalCVs > 0 && !isEvaluating;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-strong rounded-2xl p-6 border-2 border-blue-400/30"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white mb-2">Ready to Evaluate?</h3>
          <div className="flex items-center gap-4 text-sm text-gray-300">
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  jobOffer ? 'bg-green-400' : 'bg-gray-500'
                }`}
              />
              <span>
                Job Offer: {jobOffer ? 'Ready' : 'Not Set'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  totalCVs > 0 ? 'bg-green-400' : 'bg-gray-500'
                }`}
              />
              <span>
                CVs: {totalCVs} {totalCVs === 1 ? 'file' : 'files'}
                {selectedResumeCount > 0 && cvCount > 0 && (
                  <span className="text-gray-500 ml-1">
                    ({cvCount} uploaded, {selectedResumeCount} selected)
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>

        <motion.button
          whileHover={canStart ? { scale: 1.05 } : {}}
          whileTap={canStart ? { scale: 0.95 } : {}}
          onClick={onStartEvaluation}
          disabled={!canStart}
          className={`
            flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg
            transition-all duration-300
            ${
              canStart
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:shadow-lg hover:shadow-blue-500/50 cursor-pointer'
                : 'bg-gray-700/50 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isEvaluating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Evaluating...</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>Start Evaluation</span>
            </>
          )}
        </motion.button>
      </div>

          {!canStart && !isEvaluating && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 text-sm text-yellow-400"
        >
          {!jobOffer && totalCVs === 0
            ? 'Please add a job offer and select/upload at least one CV to start evaluation.'
            : !jobOffer
            ? 'Please complete the job offer details to start evaluation.'
            : 'Please select or upload at least one CV to start evaluation.'}
        </motion.p>
      )}
    </motion.div>
  );
}

