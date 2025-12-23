"""
Agent Technique - Evaluates technical skills
Checks technical skills against job requirements
"""

from typing import Dict, List, Any, Optional


class AgentTechnique:
    """
    Agent Technique: Evaluates technical skills.
    Checks if candidate has required technical competencies.
    """
    
    def __init__(self, llm=None):
        """
        Initialize Agent Technique.
        
        Args:
            llm: Optional LLM for advanced evaluation
        """
        self.llm = llm
    
    def evaluer_competences_techniques(self,
                                      candidat_skills: List[str],
                                      job_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate technical skills of candidate against job requirements.
        
        Args:
            candidat_skills: List of candidate's technical skills
            job_profile: Target job profile with required skills
            
        Returns:
            Dictionary with technical score and comment
        """
        skills_obligatoires = job_profile.get("skills_obligatoires", [])
        skills_optionnelles = job_profile.get("skills_optionnelles", [])
        
        # Normalize skills (lowercase)
        candidat_skills_lower = [s.lower() for s in candidat_skills]
        
        # Check required skills
        skills_correspondantes = []
        skills_manquantes = []
        
        for skill_requis in skills_obligatoires:
            skill_lower = skill_requis.lower()
            # Check if candidate has this skill or similar
            matched = False
            for cand_skill in candidat_skills_lower:
                if skill_lower in cand_skill or cand_skill in skill_lower:
                    skills_correspondantes.append(skill_requis)
                    matched = True
                    break
            
            if not matched:
                skills_manquantes.append(skill_requis)
        
        # Check optional skills
        skills_optionnelles_trouvees = []
        for skill_opt in skills_optionnelles:
            skill_lower = skill_opt.lower()
            for cand_skill in candidat_skills_lower:
                if skill_lower in cand_skill or cand_skill in skill_lower:
                    skills_optionnelles_trouvees.append(skill_opt)
                    break
        
        # Calculate score (0-100)
        score_technique = self._calculate_technical_score(
            len(skills_obligatoires),
            len(skills_correspondantes),
            len(skills_optionnelles),
            len(skills_optionnelles_trouvees)
        )
        
        # Generate comment
        commentaire = self._generate_comment(
            skills_correspondantes,
            skills_manquantes,
            skills_optionnelles_trouvees,
            score_technique
        )
        
        return {
            "score_technique": score_technique,
            "commentaire_technique": commentaire,
            "skills_correspondantes": skills_correspondantes,
            "skills_manquantes": skills_manquantes,
            "skills_optionnelles_trouvees": skills_optionnelles_trouvees,
            "total_requis": len(skills_obligatoires),
            "total_correspondant": len(skills_correspondantes)
        }
    
    def _calculate_technical_score(self,
                                  total_requis: int,
                                  correspondant: int,
                                  total_optionnel: int,
                                  optionnel_trouve: int) -> float:
        """Calculate technical score (0-100)."""
        if total_requis == 0:
            # No required skills, base score on optional
            if total_optionnel > 0:
                return min(100, (optionnel_trouve / total_optionnel) * 100)
            return 50.0  # Default score
        
        # Required skills are 80% of score
        score_requis = (correspondant / total_requis) * 80
        
        # Optional skills are 20% of score
        if total_optionnel > 0:
            score_optionnel = (optionnel_trouve / total_optionnel) * 20
        else:
            score_optionnel = 0
        
        return min(100.0, score_requis + score_optionnel)
    
    def _generate_comment(self,
                         correspondantes: List[str],
                         manquantes: List[str],
                         optionnelles: List[str],
                         score: float) -> str:
        """Generate technical evaluation comment."""
        comment_parts = []
        
        if score >= 80:
            comment_parts.append("Excellent profil technique")
        elif score >= 60:
            comment_parts.append("Bon profil technique")
        elif score >= 40:
            comment_parts.append("Profil technique acceptable")
        else:
            comment_parts.append("Profil technique insuffisant")
        
        comment_parts.append(f"Score: {score:.1f}/100")
        
        if correspondantes:
            comment_parts.append(f"Compétences correspondantes ({len(correspondantes)}/{len(correspondantes) + len(manquantes)}): {', '.join(correspondantes[:5])}")
        
        if manquantes:
            comment_parts.append(f"Compétences manquantes: {', '.join(manquantes[:5])}")
        
        if optionnelles:
            comment_parts.append(f"Compétences optionnelles trouvées: {', '.join(optionnelles[:5])}")
        
        return " | ".join(comment_parts)

