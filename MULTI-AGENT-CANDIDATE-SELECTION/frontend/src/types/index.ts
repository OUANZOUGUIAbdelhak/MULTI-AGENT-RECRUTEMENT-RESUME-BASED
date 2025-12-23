// Agent Status Types
export type AgentStatus = 'waiting' | 'processing' | 'completed';

// Agent Information
export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  icon: string;
  status: AgentStatus;
  progress: number; // 0-100
}

// Recommendation Levels
export type RecommendationLevel = 'strongly-recommended' | 'recommended' | 'not-recommended';

// Candidate Score Breakdown
export interface CandidateScores {
  profile: number;
  technical: number;
  softSkills: number;
  global: number;
}

// Candidate Information
export interface Candidate {
  id: string;
  name: string;
  scores: CandidateScores;
  recommendation: RecommendationLevel;
  justification: string;
}

// Detailed Candidate Data (for expandable section)
export interface CandidateDetails extends Candidate {
  radarData: {
    profile: number;
    technical: number;
    softSkills: number;
    experience: number;
    education: number;
    certifications: number;
  };
  aiJustification: string;
}

// Decision Agent Output
export interface DecisionOutput {
  topCandidate: CandidateDetails;
  confidence: number; // 0-100
  finalJustification: string;
  totalCandidates: number;
}

// Uploaded CV File
export interface UploadedCV {
  id: string;
  file: File;
  name: string;
  size: number;
  uploadDate: Date;
  status: 'uploaded' | 'processing' | 'processed';
}

// Job Offer
export interface JobOffer {
  title: string;
  description: string;
  requirements: string;
  location?: string;
  salary?: string;
}

