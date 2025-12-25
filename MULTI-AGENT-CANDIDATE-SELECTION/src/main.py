"""
Multi-Agent Pipeline for Candidate Selection
Orchestrates all agents and integrates with LlamaIndex RAG system
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import pdfplumber

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents import (
    AgentRH, AgentProfil, AgentTechnique, 
    AgentSoftSkills, AgentDecideur
)
from src.rag_new.rag_system import RAGSystem, create_rag_system_from_config


class MultiAgentPipeline:
    """
    Main pipeline that orchestrates all agents for candidate evaluation.
    Integrates LlamaIndex RAG for candidate retrieval.
    """
    
    def __init__(self, rag_system: Optional[RAGSystem] = None):
        """
        Initialize the multi-agent pipeline.
        
        Args:
            rag_system: Optional RAG system instance (will create if None)
        """
        # Initialize agents
        self.agent_rh = AgentRH()
        self.agent_profil = AgentProfil()
        self.agent_technique = AgentTechnique()
        self.agent_softskills = AgentSoftSkills()
        self.agent_decideur = AgentDecideur()
        
        # Initialize RAG system
        if rag_system:
            self.rag_system = rag_system
        else:
            try:
                self.rag_system = create_rag_system_from_config()
                # Try to load existing index
                self.rag_system.load_index()
            except Exception as e:
                print(f"⚠️  RAG system not available: {e}")
                self.rag_system = None
    
    def process_job_offer(self,
                         job_description: str,
                         criteres: Optional[Dict] = None,
                         use_rag: bool = True,
                         max_candidates: int = 10,
                         cv_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a job offer and evaluate candidates.
        
        Args:
            job_description: Job description text
            criteres: Additional criteria from recruiter
            use_rag: Whether to use RAG for candidate retrieval
            max_candidates: Maximum number of candidates to evaluate
            
        Returns:
            Dictionary with job profile, evaluated candidates, and final report
        """
        # Step 1: Agent RH - Analyze job offer
        print("📋 Agent RH: Analyzing job offer...")
        job_profile = self.agent_rh.analyser_offre(job_description, criteres)
        print(f"✅ Job profile extracted: {job_profile.get('poste', 'N/A')}")
        
        # Step 2: Retrieve candidates using cv_ids, RAG, or direct file access
        print(f"\n🔍 Retrieving candidates...")
        candidates_data = self._retrieve_candidates(
            job_profile, use_rag, max_candidates, cv_ids
        )
        
        if not candidates_data:
            return {
                "job_profile": job_profile,
                "candidates_evaluated": [],
                "report": {
                    "resume": "Aucun candidat trouvé",
                    "statistiques": {},
                    "top_candidats": []
                }
            }
        
        print(f"✅ Found {len(candidates_data)} candidate(s)")
        
        # Step 3: Evaluate each candidate with all agents
        print(f"\n🤖 Evaluating candidates with all agents...")
        evaluations = []
        
        for i, candidate_data in enumerate(candidates_data, 1):
            print(f"\n  [{i}/{len(candidates_data)}] Evaluating candidate...")
            
            evaluation = self._evaluate_candidate(
                candidate_data, job_profile
            )
            evaluations.append(evaluation)
        
        # Step 4: Agent Décideur - Rank candidates
        print(f"\n⚖️  Agent Décideur: Ranking candidates...")
        ranked_candidates = self.agent_decideur.classer_candidats(evaluations)
        
        # Step 5: Generate final report
        print(f"\n📊 Generating final report...")
        report = self.agent_decideur.generer_rapport_final(
            ranked_candidates, job_profile
        )
        
        return {
            "job_profile": job_profile,
            "candidates_evaluated": ranked_candidates,
            "report": report
        }
    
    def _retrieve_candidates(self,
                            job_profile: Dict[str, Any],
                            use_rag: bool,
                            max_candidates: int,
                            cv_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve candidate documents using cv_ids, RAG, or file system.
        
        Args:
            job_profile: Target job profile
            use_rag: Whether to use RAG for ranking (but always load full files)
            max_candidates: Maximum candidates to retrieve
            cv_ids: Optional list of specific CV IDs to load
            
        Returns:
            List of candidate data dictionaries with FULL CV content
        """
        candidates_data = []
        
        # Priority 1: If cv_ids are provided, load those specific files
        if cv_ids:
            print(f"📋 Loading {len(cv_ids)} specific CV(s) by ID...")
            candidates_data = self._load_candidates_by_ids(cv_ids)
            if candidates_data:
                print(f"✅ Loaded {len(candidates_data)} CV(s) by ID")
                return candidates_data
        
        # Priority 2: Use RAG to find relevant CVs, then load FULL files
        if use_rag and self.rag_system and self.rag_system.index:
            try:
                # Build query from job profile
                query_parts = []
                if job_profile.get("poste"):
                    query_parts.append(job_profile["poste"])
                if job_profile.get("skills_obligatoires"):
                    query_parts.extend(job_profile["skills_obligatoires"][:3])
                
                query = " ".join(query_parts) if query_parts else "candidate CV"
                
                # Search documents to get file names (not chunks!)
                results = self.rag_system.search_documents(query, k=max_candidates * 2)  # Get more to deduplicate
                
                # Extract unique file names from results
                file_names = set()
                for result in results:
                    source = result.get("source", "")
                    # Extract filename from source path
                    if source:
                        # Handle different path formats
                        if "/" in source:
                            file_name = source.split("/")[-1]
                        elif "\\" in source:
                            file_name = source.split("\\")[-1]
                        else:
                            file_name = source
                        file_names.add(file_name)
                
                # Load FULL files (not chunks!)
                if file_names:
                    print(f"📋 Loading {len(file_names)} CV file(s) found by RAG...")
                    candidates_data = self._load_candidates_by_filenames(list(file_names)[:max_candidates])
                    if candidates_data:
                        print(f"✅ Loaded {len(candidates_data)} full CV(s) from RAG search")
                        return candidates_data
                
            except Exception as e:
                print(f"⚠️  RAG retrieval failed: {e}, falling back to file system")
        
        # Priority 3: Fallback - Load from file system
        print(f"📋 Loading CVs from file system...")
        candidates_data = self._load_candidates_from_files(max_candidates)
        return candidates_data
    
    def _load_candidates_by_ids(self, cv_ids: List[str]) -> List[Dict[str, Any]]:
        """Load candidate files by their IDs (UUID or filename)."""
        from src.config import RAW_DIR
        import uuid as uuid_lib
        
        candidates_data = []
        
        if not RAW_DIR.exists():
            return candidates_data
        
        # Get all candidate files
        all_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
        
        # Create lookup dictionaries for faster matching
        files_by_uuid = {}  # Files saved with UUID names
        files_by_name = {}  # Files with descriptive names
        
        for file_path in all_files:
            file_stem = file_path.stem
            file_name = file_path.name
            
            # Check if filename is a UUID (uploaded files)
            try:
                # Try to parse as UUID
                uuid_lib.UUID(file_stem)
                files_by_uuid[file_stem] = file_path
            except ValueError:
                # Not a UUID, store by name
                files_by_name[file_name.lower()] = file_path
                files_by_name[file_stem.lower()] = file_path
        
        # Try to match IDs to files
        for cv_id in cv_ids:
            matched_file = None
            
            # Strategy 1: Direct UUID match (for uploaded files)
            try:
                uuid_lib.UUID(cv_id)
                if cv_id in files_by_uuid:
                    matched_file = files_by_uuid[cv_id]
            except ValueError:
                pass
            
            # Strategy 2: Match by filename (exact or partial)
            if not matched_file:
                cv_id_lower = cv_id.lower()
                # Try exact match first
                if cv_id_lower in files_by_name:
                    matched_file = files_by_name[cv_id_lower]
                else:
                    # Try partial match (cv_id might be part of filename)
                    for file_name_lower, file_path in files_by_name.items():
                        if cv_id_lower in file_name_lower or file_name_lower.startswith(cv_id_lower):
                            matched_file = file_path
                            break
            
            # Strategy 3: Match by email prefix (extract from cv_id if it's an email)
            if not matched_file and '@' in cv_id:
                email_prefix = cv_id.split('@')[0].lower()
                for file_name_lower, file_path in files_by_name.items():
                    if email_prefix in file_name_lower:
                        matched_file = file_path
                        break
            
            if matched_file:
                try:
                    if matched_file.suffix.lower() == ".pdf":
                        text = self._extract_pdf_text(matched_file)
                    else:
                        text = matched_file.read_text(encoding='utf-8', errors='ignore')
                    
                    candidates_data.append({
                        "source": matched_file.name,
                        "content": text,
                        "similarity": 1.0,
                        "cv_id": cv_id
                    })
                    print(f"✅ Loaded CV: {matched_file.name} (matched by ID: {cv_id})")
                except Exception as e:
                    print(f"⚠️  Failed to load {matched_file.name}: {e}")
            else:
                print(f"⚠️  Could not find file for CV ID: {cv_id}")
        
        return candidates_data
    
    def _load_candidates_by_filenames(self, filenames: List[str]) -> List[Dict[str, Any]]:
        """Load candidate files by their filenames."""
        from src.config import RAW_DIR
        
        candidates_data = []
        
        if not RAW_DIR.exists():
            return candidates_data
        
        # Get all candidate files
        all_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
        
        # Create a lookup dictionary
        file_lookup = {f.name.lower(): f for f in all_files}
        
        for filename in filenames:
            filename_lower = filename.lower()
            if filename_lower in file_lookup:
                file_path = file_lookup[filename_lower]
                try:
                    if file_path.suffix.lower() == ".pdf":
                        text = self._extract_pdf_text(file_path)
                    else:
                        text = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    candidates_data.append({
                        "source": file_path.name,
                        "content": text,
                        "similarity": 1.0
                    })
                except Exception as e:
                    print(f"⚠️  Failed to load {file_path.name}: {e}")
        
        return candidates_data
    
    def _load_candidates_from_files(self, max_candidates: int) -> List[Dict[str, Any]]:
        """Load candidate files from DATA/raw directory."""
        from src.config import RAW_DIR
        
        candidates_data = []
        
        if not RAW_DIR.exists():
            return candidates_data
        
        # Get all candidate files
        candidate_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
        
        for file_path in candidate_files[:max_candidates]:
            try:
                if file_path.suffix.lower() == ".pdf":
                    # Extract text from PDF
                    text = self._extract_pdf_text(file_path)
                else:
                    # Read text file
                    text = file_path.read_text(encoding='utf-8', errors='ignore')
                
                candidates_data.append({
                    "source": file_path.name,
                    "content": text,
                    "similarity": 1.0
                })
            except Exception as e:
                print(f"⚠️  Failed to load {file_path.name}: {e}")
        
        return candidates_data
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"⚠️  PDF extraction failed: {e}")
            return ""
    
    def _evaluate_candidate(self,
                           candidate_data: Dict[str, Any],
                           job_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single candidate using all agents.
        
        Args:
            candidate_data: Candidate document data
            job_profile: Target job profile
            
        Returns:
            Complete evaluation dictionary
        """
        cv_text = candidate_data.get("content", "")
        source = candidate_data.get("source", "unknown")
        
        # Agent Profil - Extract candidate profile
        profil_data = self.agent_profil.analyser_candidat(
            cv_text=cv_text,
            lettre_motivation="",  # Can be enhanced to load cover letters
            job_profile=job_profile
        )
        
        # Agent Technique - Evaluate technical skills
        technique_data = self.agent_technique.evaluer_competences_techniques(
            candidat_skills=profil_data.get("skills_list", []),
            job_profile=job_profile
        )
        
        # Agent Soft Skills - Evaluate soft skills
        softskills_data = self.agent_softskills.evaluer_soft_skills(
            lettre_motivation=profil_data.get("lettre_motivation", ""),
            cv_text=cv_text,
            experience=profil_data.get("experience", []),
            job_profile=job_profile
        )
        
        # Combine all evaluations
        evaluation = {
            "candidate_id": profil_data.get("id", source),
            "source": source,
            "nom": profil_data.get("nom", "N/A"),
            "email": profil_data.get("email", ""),
            "score_profil": profil_data.get("score_profil", 0),
            "score_technique": technique_data.get("score_technique", 0),
            "score_softskills": softskills_data.get("score_softskills", 0),
            "commentaire_profil": profil_data.get("commentaire_profil", ""),
            "commentaire_technique": technique_data.get("commentaire_technique", ""),
            "commentaire_softskills": softskills_data.get("commentaire_softskills", ""),
            "profil_structuré": profil_data,
            "technique_details": technique_data,
            "softskills_details": softskills_data,
            "similarity": candidate_data.get("similarity", 0.0)
        }
        
        return evaluation

