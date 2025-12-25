"""
Agent RH - Analyzes job descriptions and recruiter criteria
Extracts structured profile requirements from job postings
"""

import json
import re
from typing import Dict, List, Any, Optional


class AgentRH:
    """
    Agent RH: Reads job descriptions and recruiter criteria.
    Generates a structured target profile.
    """
    
    def __init__(self, llm=None):
        """
        Initialize Agent RH.
        
        Args:
            llm: Optional LLM for advanced parsing (can use RAG system)
        """
        self.llm = llm
    
    def analyser_offre(self, 
                      description_poste: str,
                      criteres: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze job offer and extract structured profile requirements.
        
        Args:
            description_poste: Job description text
            criteres: Additional criteria from recruiter (optional)
            
        Returns:
            Structured profile dictionary with requirements
        """
        criteres = criteres or {}
        desc_lower = description_poste.lower()
        
        # Extract job title
        poste = self._extract_poste(description_poste, desc_lower)
        
        # Extract seniority level
        seniorite = self._extract_seniorite(desc_lower)
        
        # Extract experience requirements
        exp_min, exp_max = self._extract_experience(desc_lower, criteres)
        
        # Extract required and optional skills
        skills_obligatoires, skills_optionnelles = self._extract_skills(desc_lower, description_poste)
        
        # Extract languages
        langues = self._extract_languages(desc_lower, criteres)
        
        # Extract location
        lieu = self._extract_location(desc_lower, criteres)
        
        # Extract salary range
        salaire_min, salaire_max = self._extract_salary(desc_lower, criteres)
        
        # Extract contract type
        contrat = self._extract_contract_type(desc_lower, criteres)
        
        # Extract keywords
        mots_cles = self._extract_keywords(description_poste)
        
        return {
            "poste": poste,
            "seniorite": seniorite,
            "exp_min": exp_min,
            "exp_max": exp_max,
            "skills_obligatoires": skills_obligatoires,
            "skills_optionnelles": skills_optionnelles,
            "langues": langues,
            "lieu": lieu,
            "salaire_min": salaire_min,
            "salaire_max": salaire_max,
            "contrat": contrat,
            "mots_cles": mots_cles,
            "notes_libres": criteres.get("notes", "")
        }
    
    def _extract_poste(self, description: str, desc_lower: str) -> str:
        """Extract job title."""
        # Common job titles
        job_titles = [
            "data scientist", "data engineer", "data analyst",
            "machine learning engineer", "ml engineer",
            "developpeur", "developer", "ingenieur", "engineer",
            "product manager", "project manager",
            "qa engineer", "test engineer", "quality assurance",
            "devops engineer", "cloud engineer",
            "full stack", "frontend", "backend",
            "cybersecurity", "security engineer"
        ]
        
        for title in job_titles:
            if title in desc_lower:
                return title.title()
        
        # Try to extract from first line
        first_line = description.split('\n')[0].strip()
        if len(first_line) < 100:
            return first_line
        
        return "Poste non spécifié"
    
    def _extract_seniorite(self, desc_lower: str) -> str:
        """Extract seniority level."""
        if any(word in desc_lower for word in ["senior", "sénior", "expérimenté", "expert"]):
            return "senior"
        elif any(word in desc_lower for word in ["junior", "débutant", "entry level", "stagiaire"]):
            return "junior"
        elif any(word in desc_lower for word in ["mid", "intermédiaire"]):
            return "mid"
        return "non spécifié"
    
    def _extract_experience(self, desc_lower: str, criteres: Dict) -> tuple:
        """Extract experience requirements."""
        exp_min = criteres.get("exp_min", 0)
        exp_max = criteres.get("exp_max", 0)
        
        # Extract from text
        exp_patterns = [
            r"(\d+)\s*ans?\s*d['\s]expérience",
            r"(\d+)\s*ans?\s*d['\s]exp",
            r"minimum\s*(\d+)\s*ans?",
            r"au moins\s*(\d+)\s*ans?",
            r"(\d+)\+?\s*ans?\s*d['\s]expérience"
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, desc_lower)
            if matches:
                exp_min = max(exp_min, int(matches[0]))
        
        return exp_min, exp_max
    
    def _extract_skills(self, desc_lower: str, description: str) -> tuple:
        """Extract required and optional skills with better section detection."""
        # Find sections for required vs optional skills
        required_section_start = -1
        optional_section_start = -1
        
        # Look for section headers
        required_markers = [
            "compétences techniques requises", "compétences requises", 
            "requis", "obligatoire", "must have", "nécessaire"
        ]
        optional_markers = [
            "compétences appréciées", "compétences optionnelles",
            "optionnel", "nice to have", "souhaitable", "bonus", "apprécié"
        ]
        
        # Find where required section starts
        for marker in required_markers:
            idx = desc_lower.find(marker)
            if idx != -1:
                required_section_start = idx
                break
        
        # Find where optional section starts
        for marker in optional_markers:
            idx = desc_lower.find(marker)
            if idx != -1:
                optional_section_start = idx
                break
        
        # If we found sections, extract skills from appropriate sections
        skills_obligatoires = []
        skills_optionnelles = []
        
        # Common technical skills with variations
        all_skills = [
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "sql", "nosql", "mongodb", "postgresql", "mysql",
            "machine learning", "ml", "deep learning", "tensorflow", "pytorch", "scikit-learn", "scikit learn", "sklearn",
            "pandas", "numpy", "spark", "apache spark", "pyspark", "hadoop",
            "aws", "azure", "gcp", "google cloud", "cloud", "docker", "kubernetes", "k8s",
            "react", "vue", "angular", "node.js", "nodejs", "django", "flask",
            "power bi", "powerbi", "tableau", "qlik", "looker",
            "git", "github", "ci/cd", "cicd", "jenkins", "terraform", "ansible",
            "mlops", "mlflow", "kubeflow", "airflow", "apache airflow",
            "r"
        ]
        
        # Normalize skill names for matching
        skill_normalizations = {
            "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
            "apache spark": ["apache spark", "spark", "pyspark"],
            "power bi": ["power bi", "powerbi"],
            "node.js": ["node.js", "nodejs"],
            "machine learning": ["machine learning", "ml"],
            "ci/cd": ["ci/cd", "cicd"],
            "apache airflow": ["apache airflow", "airflow"]
        }
        
        for skill in all_skills:
            # Check all variations of the skill
            skill_variations = [skill]
            for normalized, variants in skill_normalizations.items():
                if skill in variants:
                    skill_variations.extend(variants)
                    break
            
            found_in_required = False
            found_in_optional = False
            
            for variation in skill_variations:
                if variation not in desc_lower:
                    continue
                
                # Find all occurrences
                import re
                matches = list(re.finditer(re.escape(variation), desc_lower))
                
                for match in matches:
                    match_pos = match.start()
                    
                    # Determine which section this match is in
                    # Calculate section boundaries
                    required_section_end = optional_section_start if optional_section_start != -1 else len(desc_lower)
                    optional_section_end = len(desc_lower)
                    
                    # Find end markers for sections
                    if required_section_start != -1:
                        # Look for end of required section
                        end_markers = ["compétences appréciées", "soft skills", "langues", "avantages"]
                        for end_marker in end_markers:
                            end_idx = desc_lower.find(end_marker, required_section_start)
                            if end_idx != -1 and end_idx < required_section_end:
                                required_section_end = end_idx
                    
                    if optional_section_start != -1:
                        # Look for end of optional section
                        end_markers = ["soft skills", "langues", "avantages"]
                        for end_marker in end_markers:
                            end_idx = desc_lower.find(end_marker, optional_section_start)
                            if end_idx != -1 and end_idx < optional_section_end:
                                optional_section_end = end_idx
                    
                    # Determine which section this match is in
                    if required_section_start != -1 and optional_section_start != -1:
                        # Both sections found - check boundaries
                        if required_section_start <= match_pos < required_section_end:
                            found_in_required = True
                        elif optional_section_start <= match_pos < optional_section_end:
                            found_in_optional = True
                    elif required_section_start != -1:
                        # Only required section found - check boundaries
                        if required_section_start <= match_pos < required_section_end:
                            found_in_required = True
                    elif optional_section_start != -1:
                        # Only optional section found - check boundaries
                        if optional_section_start <= match_pos < optional_section_end:
                            found_in_optional = True
                    else:
                        # No clear sections, use context-based detection
                        context = self._get_skill_context(description, variation, window=100)
                        context_lower = context.lower()
                        if any(kw in context_lower for kw in ["requis", "obligatoire", "must have", "nécessaire", "essentiel", "maîtrise", "expérience avec"]):
                            found_in_required = True
                        elif any(kw in context_lower for kw in ["optionnel", "nice to have", "souhaitable", "bonus", "apprécié"]):
                            found_in_optional = True
                        else:
                            # Default: if mentioned in "Compétences Techniques Requises" section, it's required
                            # Otherwise, check proximity to "appréciées"
                            if "compétences techniques requises" in desc_lower[:match_pos + 500]:
                                found_in_required = True
                            elif "appréciées" in desc_lower[max(0, match_pos-200):match_pos+200]:
                                found_in_optional = True
                            else:
                                # Default to required for core skills, optional for others
                                core_skills = ["python", "sql", "scikit-learn", "tensorflow", "pytorch", "spark", "hadoop", "postgresql", "mongodb", "git"]
                                if any(cs in variation for cs in core_skills):
                                    found_in_required = True
                                else:
                                    found_in_optional = True
                    
                    if found_in_required or found_in_optional:
                        break
                
                if found_in_required or found_in_optional:
                    break
            
            # Add to appropriate list
            skill_name = skill.title()
            # Handle special cases and normalize to avoid duplicates
            if skill == "scikit-learn" or skill == "scikit learn" or skill == "sklearn":
                skill_name = "Scikit-learn"
            elif skill == "power bi" or skill == "powerbi":
                skill_name = "Power BI"
            elif skill == "node.js" or skill == "nodejs":
                skill_name = "Node.js"
            elif skill == "apache spark" or skill == "pyspark" or skill == "spark":
                skill_name = "Apache Spark"  # Normalize all spark variants
            elif skill == "apache airflow" or skill == "airflow":
                skill_name = "Apache Airflow"
            elif skill == "ci/cd" or skill == "cicd":
                skill_name = "CI/CD"
            elif skill == "ml" or skill == "machine learning":
                skill_name = "Machine Learning"
            elif skill == "aws" or skill == "azure" or skill == "gcp" or skill == "google cloud":
                skill_name = "Cloud"  # Group cloud providers
            elif skill == "mlops" or skill == "mlflow" or skill == "kubeflow":
                skill_name = "MLOps"  # Group MLOps tools
            
            # Check for duplicates before adding
            if found_in_required:
                # Remove any duplicates or more specific versions
                skills_obligatoires = [s for s in skills_obligatoires if s.lower() != skill_name.lower() and skill_name.lower() not in s.lower()]
                if skill_name not in skills_obligatoires:
                    skills_obligatoires.append(skill_name)
            elif found_in_optional:
                # Remove any duplicates or more specific versions
                skills_optionnelles = [s for s in skills_optionnelles if s.lower() != skill_name.lower() and skill_name.lower() not in s.lower()]
                if skill_name not in skills_optionnelles:
                    skills_optionnelles.append(skill_name)
        
        # Final cleanup: remove duplicates and normalize
        skills_obligatoires = list(dict.fromkeys(skills_obligatoires))  # Preserve order, remove duplicates
        skills_optionnelles = list(dict.fromkeys(skills_optionnelles))
        
        # Remove skills from optional if they're already in required
        skills_optionnelles = [s for s in skills_optionnelles if s not in skills_obligatoires]
        
        return skills_obligatoires, skills_optionnelles
    
    def _get_skill_context(self, text: str, skill: str, window: int = 50) -> str:
        """Get context around skill mention."""
        idx = text.lower().find(skill.lower())
        if idx == -1:
            return ""
        start = max(0, idx - window)
        end = min(len(text), idx + len(skill) + window)
        return text[start:end]
    
    def _extract_languages(self, desc_lower: str, criteres: Dict) -> List[str]:
        """Extract language requirements."""
        langues = criteres.get("langues", [])
        
        languages = ["français", "anglais", "espagnol", "allemand", "italien", "chinois"]
        for lang in languages:
            if lang in desc_lower:
                if lang not in langues:
                    langues.append(lang.title())
        
        return langues if langues else ["Français"]
    
    def _extract_location(self, desc_lower: str, criteres: Dict) -> str:
        """Extract location."""
        if criteres.get("lieu"):
            return criteres["lieu"]
        
        locations = ["paris", "lyon", "marseille", "toulouse", "remote", "télétravail"]
        for loc in locations:
            if loc in desc_lower:
                return loc.title()
        
        return "Non spécifié"
    
    def _extract_salary(self, desc_lower: str, criteres: Dict) -> tuple:
        """Extract salary range."""
        salaire_min = criteres.get("salaire_min", 0)
        salaire_max = criteres.get("salaire_max", 0)
        
        # Try to extract from text
        salary_patterns = [
            r"(\d+)\s*€?\s*-\s*(\d+)\s*€",
            r"(\d+)\s*k?\s*€?\s*/\s*an",
            r"salaire\s*:\s*(\d+)\s*€"
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, desc_lower.replace(" ", ""))
            if matches:
                if isinstance(matches[0], tuple):
                    salaire_min = int(matches[0][0])
                    salaire_max = int(matches[0][1]) if len(matches[0]) > 1 else salaire_min
                else:
                    salaire_min = int(matches[0])
        
        return salaire_min, salaire_max
    
    def _extract_contract_type(self, desc_lower: str, criteres: Dict) -> str:
        """Extract contract type."""
        if criteres.get("contrat"):
            return criteres["contrat"]
        
        contract_types = {
            "cdi": ["cdi", "permanent"],
            "cdd": ["cdd", "temporary", "temporaire"],
            "stage": ["stage", "internship", "stagiaire"],
            "alternance": ["alternance", "apprentissage", "apprenticeship"],
            "freelance": ["freelance", "consultant", "indépendant"]
        }
        
        for contract, keywords in contract_types.items():
            if any(kw in desc_lower for kw in keywords):
                return contract.upper()
        
        return "CDI"
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract important keywords from description."""
        # Simple keyword extraction (can be enhanced)
        words = re.findall(r'\b[a-z]{4,}\b', description.lower())
        # Filter common words
        stop_words = {"dans", "pour", "avec", "sont", "cette", "dans", "plus", "tous", "toutes"}
        keywords = [w for w in words if w not in stop_words]
        # Return most frequent
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]

