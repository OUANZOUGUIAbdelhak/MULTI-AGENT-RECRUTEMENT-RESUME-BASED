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
import IndexBuildProgress from './components/IndexBuildProgress';
import { Agent, CandidateDetails as CandidateDetailsType, UploadedCV, JobOffer, DecisionOutput as DecisionOutputType } from './types';
import { mockAgents, mockCandidates, mockDecisionOutput } from './data/mockData';
import { uploadCVs, startEvaluation, getEvaluationStatus, pollEvaluationStatus, processResumes } from './services/api';

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
  const [indexBuildId, setIndexBuildId] = useState<string | null>(null);
  const [selectedResumeIds, setSelectedResumeIds] = useState<string[]>([]);
  const evaluationIntervalRef = useRef<number | null>(null);

  // Handle file uploads
  const handleFilesUploaded = async (files: File[]) => {
    try {
      // Upload to backend
      const result = await uploadCVs(files);
      
      // Map backend file IDs to our CV structure
      const newCVs: UploadedCV[] = (result.files || []).map((file: any) => ({
        id: file.id,
        file: files.find(f => f.name === file.filename) || files[0],
        name: file.filename,
        size: file.size,
        uploadDate: new Date(file.upload_date),
        status: 'processed' as const,
      }));

      setUploadedCVs((prev) => [...prev, ...newCVs]);
      
      // If backend is rebuilding index, track progress
      if (result.build_id) {
        setIndexBuildId(result.build_id);
      }
    } catch (error) {
      console.error('Error uploading CVs:', error);
      alert('Failed to upload CVs. Please try again.');
    }
  };

  // Remove CV
  const handleRemoveCV = (id: string) => {
    setUploadedCVs((prev) => prev.filter((cv) => cv.id !== id));
    // Also remove from selected resumes if it was selected from DATA/raw
    setSelectedResumeIds((prev) => prev.filter((resumeId) => resumeId !== id));
  };

  // Handle resume selection change from DATA/raw
  const handleResumeSelectionChange = async (fileIds: string[]) => {
    setSelectedResumeIds(fileIds);
    
    // Remove CVs from uploadedCVs that were from DATA/raw and are no longer selected
    // Only keep files that were actually uploaded (have a real File object with size > 0)
    setUploadedCVs((prev) => 
      prev.filter((cv) => {
        // Keep if it's an uploaded file (has a real File object with actual content)
        // Check if file has meaningful size (uploaded files) vs dummy files (selected from DATA/raw)
        const isUploadedFile = cv.file.size > 100; // Real uploaded files have content
        return isUploadedFile;
      })
    );
  };

  // Process selected resumes from DATA/raw (rebuild index)
  const handleProcessResumes = async (fileIds: string[]) => {
    try {
      // Process resumes (rebuild index) - resumes are already in uploadedCVs from selection
      const result = await processResumes(fileIds);
      if (result.build_id) {
        setIndexBuildId(result.build_id);
      }
    } catch (error) {
      console.error('Error processing resumes:', error);
      alert('Failed to process resumes. Please try again.');
    }
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
    // Combine uploaded CVs and selected resumes from DATA/raw, avoiding duplicates
    // Only count files that were actually uploaded (have real File content)
    const uploadedIds = uploadedCVs
      .filter(cv => cv.file.size > 100) // Real uploaded files have content
      .map(cv => cv.id);
    
    // Add selected resume IDs that aren't already in uploaded CVs
    const selectedIds = selectedResumeIds.filter(id => !uploadedIds.includes(id));
    const allCVIds = [...uploadedIds, ...selectedIds];
    
    if (!jobOffer || allCVIds.length === 0) return;

    setView('evaluating');
    setSystemStatus('running');
    setCandidates([]);
    setDecisionOutput(null);

    // Reset agents
    setAgents(mockAgents.map((agent) => ({ ...agent, status: 'waiting', progress: 0 })));

    try {
      // Start backend evaluation - use allCVIds (uploaded + selected from DATA/raw)
      const result = await startEvaluation(jobOffer, allCVIds, true, 10);
      const evaluationId = result.evaluationId;

      if (!evaluationId) {
        console.error('No evaluation ID returned from backend:', result);
        alert('Failed to start evaluation: No evaluation ID received');
        setSystemStatus('idle');
        setView('setup');
        return;
      }

      console.log('Evaluation started with ID:', evaluationId);

      // Start polling for updates
      const stopPolling = pollEvaluationStatus(
        evaluationId,
        (data) => {
          // Update agents
          const updatedAgents = mockAgents.map((agent) => {
            const backendAgent = data.agents.find((a: any) => a.id === agent.id);
            if (backendAgent) {
              return {
                ...agent,
                status: backendAgent.status as 'waiting' | 'processing' | 'completed',
                progress: backendAgent.progress,
              };
            }
            return agent;
          });
          setAgents(updatedAgents);

          // Update candidates if available
          if (data.candidates && data.candidates.length > 0) {
            setCandidates(data.candidates);
          }

          // Update decision output
          if (data.decision) {
            setDecisionOutput(data.decision);
          }

          // Update system status
          if (data.status === 'completed') {
            setSystemStatus('completed');
            setView('results');
            if (stopPolling) stopPolling();
          } else if (data.status === 'error') {
            setSystemStatus('idle');
            alert(`Evaluation error: ${data.error || 'Unknown error'}`);
            if (stopPolling) stopPolling();
          }
        },
        2000 // Poll every 2 seconds
      );

      // Store stop function for cleanup
      evaluationIntervalRef.current = stopPolling as any;
    } catch (error) {
      console.error('Error starting evaluation:', error);
      alert('Failed to start evaluation. Please check if the backend is running.');
      setSystemStatus('idle');
      setView('setup');
    }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (evaluationIntervalRef.current) {
        evaluationIntervalRef.current();
      }
    };
  }, []);

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
                onProcessResumes={handleProcessResumes}
                selectedResumeIds={selectedResumeIds}
                onResumeSelectionChange={handleResumeSelectionChange}
              />

              {/* Index Build Progress */}
              <IndexBuildProgress
                buildId={indexBuildId}
                onComplete={() => setIndexBuildId(null)}
              />

              {/* Evaluation Control */}
              <EvaluationControl
                jobOffer={jobOffer}
                cvCount={uploadedCVs.filter(cv => cv.file.size > 100).length} // Only count actually uploaded files
                selectedResumeCount={selectedResumeIds.length} // Count files selected from DATA/raw
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
