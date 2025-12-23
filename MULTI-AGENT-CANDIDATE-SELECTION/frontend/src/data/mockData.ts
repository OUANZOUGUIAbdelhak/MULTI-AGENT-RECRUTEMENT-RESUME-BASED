import { Agent, CandidateDetails, DecisionOutput } from '../types';

// Mock Agents Data
export const mockAgents: Agent[] = [
  {
    id: 'rh-agent',
    name: 'RH Agent',
    role: 'Job Analysis',
    description: 'Analyzes job descriptions and recruiter criteria',
    icon: 'FileText',
    status: 'waiting',
    progress: 0,
  },
  {
    id: 'profile-agent',
    name: 'Profile Agent',
    role: 'CV Analysis',
    description: 'Extracts and analyzes CV information',
    icon: 'User',
    status: 'waiting',
    progress: 0,
  },
  {
    id: 'technical-agent',
    name: 'Technical Agent',
    role: 'Technical Evaluation',
    description: 'Evaluates technical skills and competencies',
    icon: 'Code',
    status: 'waiting',
    progress: 0,
  },
  {
    id: 'softskills-agent',
    name: 'Soft Skills Agent',
    role: 'Soft Skills Evaluation',
    description: 'Assesses interpersonal and cultural fit',
    icon: 'Users',
    status: 'waiting',
    progress: 0,
  },
  {
    id: 'decision-agent',
    name: 'Decision Agent',
    role: 'Final Ranking',
    description: 'Generates final ranking and justification',
    icon: 'Award',
    status: 'waiting',
    progress: 0,
  },
];

// Mock Candidates Data
export const mockCandidates: CandidateDetails[] = [
  {
    id: 'candidate-1',
    name: 'Marie Dubois',
    scores: {
      profile: 95,
      technical: 92,
      softSkills: 88,
      global: 91.7,
    },
    recommendation: 'strongly-recommended',
    justification: 'Excellent match with outstanding technical skills and strong cultural fit.',
    radarData: {
      profile: 95,
      technical: 92,
      softSkills: 88,
      experience: 90,
      education: 95,
      certifications: 85,
    },
    aiJustification: 'Marie demonstrates exceptional alignment with the role requirements. Her 5+ years of experience in data science, combined with strong technical skills in Python, ML, and cloud technologies, make her an ideal candidate. Her soft skills assessment reveals excellent communication abilities and team collaboration experience.',
  },
  {
    id: 'candidate-2',
    name: 'Pierre Martin',
    scores: {
      profile: 87,
      technical: 89,
      softSkills: 85,
      global: 87.0,
    },
    recommendation: 'recommended',
    justification: 'Strong technical profile with good overall fit.',
    radarData: {
      profile: 87,
      technical: 89,
      softSkills: 85,
      experience: 88,
      education: 85,
      certifications: 90,
    },
    aiJustification: 'Pierre shows strong technical competencies and relevant experience. His background in full-stack development aligns well with the position requirements. While his soft skills are solid, there is room for growth in leadership areas.',
  },
  {
    id: 'candidate-3',
    name: 'Sophie Bernard',
    scores: {
      profile: 82,
      technical: 78,
      softSkills: 90,
      global: 83.3,
    },
    recommendation: 'recommended',
    justification: 'Good cultural fit with moderate technical skills.',
    radarData: {
      profile: 82,
      technical: 78,
      softSkills: 90,
      experience: 80,
      education: 85,
      certifications: 75,
    },
    aiJustification: 'Sophie excels in soft skills and team dynamics, making her a valuable cultural addition. Her technical skills are adequate but may require some upskilling in specific areas. Her motivation and adaptability are notable strengths.',
  },
  {
    id: 'candidate-4',
    name: 'Nicolas Petit',
    scores: {
      profile: 75,
      technical: 85,
      softSkills: 70,
      global: 76.7,
    },
    recommendation: 'not-recommended',
    justification: 'Strong technical skills but concerns about soft skills fit.',
    radarData: {
      profile: 75,
      technical: 85,
      softSkills: 70,
      experience: 78,
      education: 80,
      certifications: 88,
    },
    aiJustification: 'Nicolas demonstrates solid technical capabilities, particularly in specialized areas. However, the assessment indicates potential challenges in communication and team collaboration, which are critical for this role.',
  },
  {
    id: 'candidate-5',
    name: 'Laura Simon',
    scores: {
      profile: 88,
      technical: 86,
      softSkills: 87,
      global: 87.0,
    },
    recommendation: 'recommended',
    justification: 'Well-rounded candidate with balanced skills.',
    radarData: {
      profile: 88,
      technical: 86,
      softSkills: 87,
      experience: 85,
      education: 90,
      certifications: 82,
    },
    aiJustification: 'Laura presents a balanced profile with strong technical and interpersonal skills. Her UX design background brings a unique perspective, and her collaborative approach makes her a solid team player.',
  },
];

// Mock Decision Output
export const mockDecisionOutput: DecisionOutput = {
  topCandidate: mockCandidates[0],
  confidence: 94,
  finalJustification: 'After comprehensive evaluation by all agents, Marie Dubois emerges as the top candidate with a global score of 91.7/100. Her exceptional technical expertise (92/100), strong profile match (95/100), and excellent soft skills (88/100) demonstrate a perfect alignment with the role requirements. The multi-agent system recommends proceeding with her candidacy with high confidence.',
  totalCandidates: mockCandidates.length,
};

