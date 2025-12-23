import { JobOffer, UploadedCV, CandidateDetails, DecisionOutput } from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Upload CV files to the backend
 */
export async function uploadCVs(files: File[]): Promise<{ success: boolean; message: string; files?: any[]; build_id?: string }> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  try {
    const response = await fetch(`${API_BASE_URL}/api/upload-cvs`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload CVs');
    }

    const data = await response.json();
    return {
      success: data.success,
      message: data.message,
      files: data.files
    };
  } catch (error) {
    console.error('Error uploading CVs:', error);
    throw error; // Re-throw to handle in component
  }
}

/**
 * Start the evaluation process
 */
export async function startEvaluation(
  jobOffer: JobOffer,
  cvIds: string[],
  useRag: boolean = true,
  maxCandidates: number = 10
): Promise<{ evaluationId: string; status: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/start-evaluation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        job_offer: jobOffer,
        cv_ids: cvIds,
        use_rag: useRag,
        max_candidates: maxCandidates,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start evaluation');
    }

    const data = await response.json();
    // Map backend response (snake_case) to frontend format (camelCase)
    return {
      evaluationId: data.evaluation_id,
      status: data.status,
    };
  } catch (error) {
    console.error('Error starting evaluation:', error);
    throw error; // Re-throw to handle in component
  }
}

/**
 * Get evaluation status and results
 */
export async function getEvaluationStatus(
  evaluationId: string
): Promise<{
  status: 'running' | 'completed' | 'error';
  agents: Array<{
    id: string;
    name: string;
    status: 'waiting' | 'processing' | 'completed';
    progress: number;
  }>;
  candidates: CandidateDetails[];
  decision?: DecisionOutput;
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/evaluation/${evaluationId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Evaluation not found');
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get evaluation status');
    }

    const data = await response.json();
    
    // Map backend agent format to frontend format
    const agents = data.agents.map((agent: any) => ({
      id: agent.id,
      name: agent.name,
      status: agent.status,
      progress: agent.progress,
    }));

    return {
      status: data.status,
      agents,
      candidates: data.candidates || [],
      decision: data.decision,
      error: data.error,
    };
  } catch (error) {
    console.error('Error getting evaluation status:', error);
    throw error; // Re-throw to handle in component
  }
}

/**
 * Process selected resume files
 */
export async function processResumes(fileIds: string[]): Promise<{ build_id: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/process-resumes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_ids: fileIds,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to process resumes');
    }

    const data = await response.json();
    return { build_id: data.build_id };
  } catch (error) {
    console.error('Error processing resumes:', error);
    throw error;
  }
}

/**
 * Poll evaluation status (for real-time updates)
 */
export function pollEvaluationStatus(
  evaluationId: string,
  onUpdate: (data: any) => void,
  interval: number = 2000
): () => void {
  let isPolling = true;

  const poll = async () => {
    if (!isPolling) return;

    try {
      const data = await getEvaluationStatus(evaluationId);
      onUpdate(data);

      if (data.status === 'completed') {
        isPolling = false;
        return;
      }
    } catch (error) {
      console.error('Error polling evaluation status:', error);
    }

    if (isPolling) {
      setTimeout(poll, interval);
    }
  };

  poll();

  // Return cleanup function
  return () => {
    isPolling = false;
  };
}

