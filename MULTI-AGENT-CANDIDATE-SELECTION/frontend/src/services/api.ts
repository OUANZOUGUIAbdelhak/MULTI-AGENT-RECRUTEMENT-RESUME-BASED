import { JobOffer, UploadedCV, CandidateDetails, DecisionOutput } from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Upload CV files to the backend
 */
export async function uploadCVs(files: File[]): Promise<{ success: boolean; message: string }> {
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
      throw new Error('Failed to upload CVs');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading CVs:', error);
    // For now, return success for mock purposes
    return { success: true, message: 'CVs uploaded successfully (mock)' };
  }
}

/**
 * Start the evaluation process
 */
export async function startEvaluation(
  jobOffer: JobOffer,
  cvIds: string[]
): Promise<{ evaluationId: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/start-evaluation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        jobOffer,
        cvIds,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to start evaluation');
    }

    return await response.json();
  } catch (error) {
    console.error('Error starting evaluation:', error);
    // For mock purposes, return a fake evaluation ID
    return { evaluationId: `eval-${Date.now()}` };
  }
}

/**
 * Get evaluation status and results
 */
export async function getEvaluationStatus(
  evaluationId: string
): Promise<{
  status: 'running' | 'completed';
  agents: any[];
  candidates: CandidateDetails[];
  decision?: DecisionOutput;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/evaluation/${evaluationId}`);

    if (!response.ok) {
      throw new Error('Failed to get evaluation status');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting evaluation status:', error);
    // Return mock data structure
    return {
      status: 'running',
      agents: [],
      candidates: [],
    };
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

