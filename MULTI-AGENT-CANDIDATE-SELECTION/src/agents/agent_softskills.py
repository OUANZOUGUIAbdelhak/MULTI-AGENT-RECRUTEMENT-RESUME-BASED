"""
Agent Soft Skills - Evaluates interpersonal qualities
Analyzes motivation, cultural fit, and soft skills
"""

import re
from typing import Dict, List, Any, Optional


class AgentSoftSkills:
    """
    Agent Soft Skills: Evaluates interpersonal qualities.
    Analyzes motivation, communication, and cultural fit.
    """
    
    def __init__(self, llm=None):
        """
        Initialize Agent Soft Skills.
        
        Args:
            llm: Optional LLM for advanced analysis
        """
        self.llm = llm
    
    def evaluer_soft_skills(self,
                            lettre_motivation: str,
                            cv_text: str,
                            experience: List[Dict],
                            job_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate soft skills from cover letter and CV.
        
        Args:
            lettre_motivation: Cover letter text
            cv_text: CV text
            experience: List of work experiences
            job_profile: Target job profile (optional)
            
        Returns:
            Dictionary with soft skills score and comment
        """
        # Analyze cover letter
        motivation_score = self._analyze_motivation(lettre_motivation)
        communication_score = self._analyze_communication(lettre_motivation, cv_text)
        
        # Extract soft skills keywords
        soft_skills_detectes = self._extract_soft_skills(lettre_motivation, cv_text)
        
        # Analyze experience for leadership/teamwork
        leadership_score = self._analyze_leadership(experience, cv_text)
        
        # Calculate overall score
        score_softskills = self._calculate_softskills_score(
            motivation_score,
            communication_score,
            leadership_score,
            len(soft_skills_detectes)
        )
        
        # Generate comment
        commentaire = self._generate_comment(
            motivation_score,
            communication_score,
            leadership_score,
            soft_skills_detectes,
            score_softskills
        )
        
        return {
            "score_softskills": score_softskills,
            "commentaire_softskills": commentaire,
            "soft_skills_detectes": soft_skills_detectes,
            "motivation_score": motivation_score,
            "communication_score": communication_score,
            "leadership_score": leadership_score
        }
    
    def _analyze_motivation(self, lettre: str) -> float:
        """Analyze motivation level from cover letter."""
        if not lettre or len(lettre) < 50:
            return 30.0  # Low score if no cover letter
        
        lettre_lower = lettre.lower()
        
        # Positive indicators
        positive_keywords = [
            "passionné", "motivé", "enthousiaste", "intéressé",
            "souhaite", "désire", "ambition", "défi",
            "apprendre", "développer", "progresser", "évoluer",
            "contribution", "apporter", "participer", "collaborer"
        ]
        
        # Negative indicators
        negative_keywords = [
            "cherche", "disponible", "urgent", "n'importe quel"
        ]
        
        positive_count = sum(1 for kw in positive_keywords if kw in lettre_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in lettre_lower)
        
        # Base score
        score = 50.0
        
        # Add points for positive indicators
        score += min(30, positive_count * 5)
        
        # Subtract points for negative indicators
        score -= negative_count * 10
        
        # Bonus for personalized content
        if len(lettre) > 200:
            score += 10
        
        return max(0.0, min(100.0, score))
    
    def _analyze_communication(self, lettre: str, cv: str) -> float:
        """Analyze communication skills."""
        score = 50.0
        
        # Check cover letter quality
        if lettre:
            # Structure
            if "objet" in lettre.lower()[:100] or "madame" in lettre.lower()[:100] or "monsieur" in lettre.lower()[:100]:
                score += 10
            
            # Length (not too short, not too long)
            if 200 <= len(lettre) <= 800:
                score += 10
            elif len(lettre) < 100:
                score -= 20
            
            # Professional language
            professional_words = ["respectueusement", "cordialement", "sincèrement"]
            if any(word in lettre.lower() for word in professional_words):
                score += 10
        
        # Check CV structure
        if cv:
            sections = ["expérience", "formation", "compétences", "langues"]
            sections_found = sum(1 for section in sections if section in cv.lower())
            score += sections_found * 5
        
        return max(0.0, min(100.0, score))
    
    def _extract_soft_skills(self, lettre: str, cv: str) -> List[str]:
        """Extract soft skills keywords."""
        text = (lettre + " " + cv).lower()
        
        soft_skills_keywords = {
            "travail d'équipe": ["travail d'équipe", "teamwork", "collaboration", "collaboratif"],
            "communication": ["communication", "communicationnel", "communiquer"],
            "leadership": ["leadership", "diriger", "management", "gérer", "encadrer"],
            "autonomie": ["autonome", "autonomie", "indépendant"],
            "adaptabilité": ["adaptable", "adaptabilité", "flexible", "polyvalent"],
            "créativité": ["créatif", "créativité", "innovation", "innovant"],
            "résolution de problèmes": ["résolution", "problème", "solution", "défi"],
            "gestion du temps": ["gestion du temps", "organisation", "organisé", "planification"],
            "esprit d'équipe": ["esprit d'équipe", "coopération", "coopératif"],
            "motivation": ["motivé", "motivation", "déterminé", "persévérant"]
        }
        
        detected = []
        for skill, keywords in soft_skills_keywords.items():
            if any(kw in text for kw in keywords):
                detected.append(skill)
        
        return detected
    
    def _analyze_leadership(self, experience: List[Dict], cv: str) -> float:
        """Analyze leadership indicators."""
        score = 30.0  # Base score
        
        cv_lower = cv.lower()
        
        # Leadership keywords
        leadership_keywords = [
            "manager", "chef", "responsable", "directeur", "lead",
            "équipe", "encadrer", "superviser", "coordonner", "piloter"
        ]
        
        leadership_count = sum(1 for kw in leadership_keywords if kw in cv_lower)
        score += min(40, leadership_count * 5)
        
        # Check experience titles
        for exp in experience:
            poste = exp.get("poste", "").lower()
            if any(kw in poste for kw in ["manager", "chef", "responsable", "directeur", "lead"]):
                score += 10
        
        return max(0.0, min(100.0, score))
    
    def _calculate_softskills_score(self,
                                   motivation: float,
                                   communication: float,
                                   leadership: float,
                                   soft_skills_count: int) -> float:
        """Calculate overall soft skills score."""
        # Weighted average
        score = (
            motivation * 0.4 +
            communication * 0.3 +
            leadership * 0.2 +
            min(100, soft_skills_count * 10) * 0.1
        )
        
        return max(0.0, min(100.0, score))
    
    def _generate_comment(self,
                         motivation: float,
                         communication: float,
                         leadership: float,
                         soft_skills: List[str],
                         score: float) -> str:
        """Generate soft skills comment."""
        comment_parts = []
        
        if score >= 80:
            comment_parts.append("Excellent profil soft skills")
        elif score >= 60:
            comment_parts.append("Bon profil soft skills")
        elif score >= 40:
            comment_parts.append("Profil soft skills acceptable")
        else:
            comment_parts.append("Profil soft skills à améliorer")
        
        comment_parts.append(f"Score: {score:.1f}/100")
        comment_parts.append(f"Motivation: {motivation:.1f}/100")
        comment_parts.append(f"Communication: {communication:.1f}/100")
        comment_parts.append(f"Leadership: {leadership:.1f}/100")
        
        if soft_skills:
            comment_parts.append(f"Soft skills détectés: {', '.join(soft_skills[:5])}")
        
        return " | ".join(comment_parts)

