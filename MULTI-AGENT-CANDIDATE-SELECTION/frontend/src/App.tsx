import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import AgentProgressSection from './components/AgentProgressSection';
import CandidateTable from './components/CandidateTable';
import CandidateDetails from './components/CandidateDetails';
import DecisionOutput from './components/DecisionOutput';
import FileUpload from './components/FileUpload';
import JobOfferForm from './components/JobOfferForm';
import EvaluationControl from './components/EvaluationControl';
import { Agent, CandidateDetails as CandidateDetailsType, UploadedCV, JobOffer, DecisionOutput as DecisionOutputType } from './types';
import { mockAgents, mockCandidates, mockDecisionOutput } from './data/mockData';
import { uploadCVs, startEvaluation } from './services/api';

type AppView = 'setup' | 'evaluating' | 'results';

function App() {
  const [view, setView] = useState<AppView>('setup');
  const [uploadedCVs, setUploadedCVs] = useState<UploadedCV[]>([]);
  const [jobOffer, setJobOffer] = useState<JobOffer | null>(null);
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [systemStatus, setSystemStatus] = useState<'running' | 'completed' | 'idle'>('idle');
  const [expandedCandidateId, setExpandedCandidateId] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateDetailsType | null>(null);
  const [candidates, setCandidates] = useState<CandidateDetailsType[]>([]);
  const [decisionOutput, setDecisionOutput] = useState<DecisionOutputType | null>(null);
  const evaluationIntervalRef = useRef<number | null>(null);

  // Handle file uploads
  const handleFilesUploaded = async (files: File[]) => {
    const newCVs: UploadedCV[] = files.map((file) => ({
      id: `cv-${Date.now()}-${Math.random()}`,
      file,
      name: file.name,
      size: file.size,
      uploadDate: new Date(),
      status: 'uploaded',
    }));

    setUploadedCVs((prev) => [...prev, ...newCVs]);

    // Upload to backend (mock for now)
    try {
      await uploadCVs(files);
      // Update status to processed after upload
      setTimeout(() => {
        setUploadedCVs((prev) =>
          prev.map((cv) =>
            newCVs.some((ncv) => ncv.id === cv.id) ? { ...cv, status: 'processed' } : cv
          )
        );
      }, 1000);
    } catch (error) {
      console.error('Error uploading CVs:', error);
    }
  };

  // Remove CV
  const handleRemoveCV = (id: string) => {
    setUploadedCVs((prev) => prev.filter((cv) => cv.id !== id));
  };

  // Generate mock candidates from uploaded CVs
  const generateCandidatesFromCVs = (cvs: UploadedCV[]): CandidateDetailsType[] => {
    if (cvs.length === 0) return [];

    // Use mock candidates but adjust based on number of CVs
    const baseCandidates = [...mockCandidates];
    return cvs.map((cv, index) => {
      const baseCandidate = baseCandidates[index % baseCandidates.length];
      // Extract name from filename (remove extension)
      const name = cv.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ').split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

      return {
        ...baseCandidate,
        id: cv.id,
        name: name || `Candidate ${index + 1}`,
      };
    });
  };

  // Start evaluation
  const handleStartEvaluation = async () => {
    if (!jobOffer || uploadedCVs.length === 0) return;

    setView('evaluating');
    setSystemStatus('running');
    setCandidates([]);
    setDecisionOutput(null);

    // Reset agents
    setAgents(mockAgents.map((agent) => ({ ...agent, status: 'waiting', progress: 0 })));

    // Start backend evaluation (mock for now)
    try {
      const cvIds = uploadedCVs.map((cv) => cv.id);
      await startEvaluation(jobOffer, cvIds);
    } catch (error) {
      console.error('Error starting evaluation:', error);
    }

    // Simulate agent progression
    simulateAgentProgression();
  };

  // Simulate agent progression
  const simulateAgentProgression = () => {
    let currentAgentIndex = 0;

    const processAgent = (index: number) => {
      if (index >= agents.length) {
        setSystemStatus('completed');
        setView('results');
        
        // Generate candidates from uploaded CVs
        const generatedCandidates = generateCandidatesFromCVs(uploadedCVs);
        setCandidates(generatedCandidates);

        // Generate decision output
        if (generatedCandidates.length > 0) {
          const topCandidate = generatedCandidates[0];
          setDecisionOutput({
            topCandidate,
            confidence: 94,
            finalJustification: `After comprehensive evaluation by all agents, ${topCandidate.name} emerges as the top candidate with a global score of ${topCandidate.scores.global.toFixed(1)}/100. ${topCandidate.aiJustification} The multi-agent system recommends proceeding with this candidacy with high confidence.`,
            totalCandidates: generatedCandidates.length,
          });
        }
        return;
      }

      // Set current agent to processing
      setAgents((prev) =>
        prev.map((agent, i) =>
          i === index ? { ...agent, status: 'processing', progress: 0 } : agent
        )
      );

      // Simulate progress
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += 10;
        if (progress <= 100) {
          setAgents((prev) =>
            prev.map((agent, i) =>
              i === index ? { ...agent, progress } : agent
            )
          );
        } else {
          clearInterval(progressInterval);
          // Mark as completed
          setAgents((prev) =>
            prev.map((agent, i) =>
              i === index
                ? { ...agent, status: 'completed', progress: 100 }
                : agent
            )
          );
          // Move to next agent
          setTimeout(() => processAgent(index + 1), 500);
        }
      }, 200);
    };

    // Start processing
    setTimeout(() => processAgent(0), 1000);
  };

  const handleCandidateClick = (candidate: CandidateDetailsType) => {
    if (expandedCandidateId === candidate.id) {
      setExpandedCandidateId(null);
      setSelectedCandidate(null);
    } else {
      setExpandedCandidateId(candidate.id);
      setSelectedCandidate(candidate);
    }
  };

  const handleReset = () => {
    setView('setup');
    setSystemStatus('idle');
    setAgents(mockAgents.map((agent) => ({ ...agent, status: 'waiting', progress: 0 })));
    setCandidates([]);
    setDecisionOutput(null);
    setExpandedCandidateId(null);
    setSelectedCandidate(null);
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <Header status={systemStatus} />
        
        <AnimatePresence mode="wait">
          {view === 'setup' && (
            <motion.div
              key="setup"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* Job Offer Form */}
              <JobOfferForm
                onJobOfferChange={setJobOffer}
                initialOffer={jobOffer}
              />

              {/* File Upload */}
              <FileUpload
                onFilesUploaded={handleFilesUploaded}
                uploadedCVs={uploadedCVs}
                onRemoveCV={handleRemoveCV}
              />

              {/* Evaluation Control */}
              <EvaluationControl
                jobOffer={jobOffer}
                cvCount={uploadedCVs.length}
                isEvaluating={false}
                onStartEvaluation={handleStartEvaluation}
              />
            </motion.div>
          )}

          {(view === 'evaluating' || view === 'results') && (
            <motion.div
              key="evaluation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {/* Agent Progress Section */}
              <AgentProgressSection agents={agents} />

              {/* Candidates Table - Show only when we have candidates */}
              {candidates.length > 0 && (
                <>
                  <CandidateTable
                    candidates={candidates}
                    onCandidateClick={handleCandidateClick}
                    expandedId={expandedCandidateId}
                  />

                  <CandidateDetails candidate={selectedCandidate} />

                  {systemStatus === 'completed' && decisionOutput && (
                    <>
                      <DecisionOutput decision={decisionOutput} />
                      
                      {/* Reset Button */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex justify-center mt-8"
                      >
                        <button
                          onClick={handleReset}
                          className="px-8 py-4 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all duration-300"
                        >
                          Start New Evaluation
                        </button>
                      </motion.div>
                    </>
                  )}
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
