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
        """Extract required and optional skills."""
        # Common technical skills
        all_skills = [
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "sql", "nosql", "mongodb", "postgresql", "mysql",
            "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
            "pandas", "numpy", "spark", "hadoop",
            "aws", "azure", "gcp", "cloud", "docker", "kubernetes",
            "react", "vue", "angular", "node.js", "django", "flask",
            "power bi", "tableau", "qlik", "looker",
            "git", "ci/cd", "jenkins", "terraform", "ansible"
        ]
        
        skills_obligatoires = []
        skills_optionnelles = []
        
        # Check for required skills (often marked with "requis", "obligatoire", "must have")
        required_keywords = ["requis", "obligatoire", "must have", "nécessaire", "essentiel"]
        optional_keywords = ["optionnel", "nice to have", "souhaitable", "bonus"]
        
        for skill in all_skills:
            if skill in desc_lower:
                # Check if it's marked as required or optional
                skill_context = self._get_skill_context(description, skill)
                if any(kw in skill_context.lower() for kw in required_keywords):
                    skills_obligatoires.append(skill.title())
                elif any(kw in skill_context.lower() for kw in optional_keywords):
                    skills_optionnelles.append(skill.title())
                else:
                    # Default to required if mentioned prominently
                    skills_obligatoires.append(skill.title())
        
        return list(set(skills_obligatoires)), list(set(skills_optionnelles))
    
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

