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
        
        # Normalize skills for better matching
        def normalize_skill(skill: str) -> str:
            """Normalize skill name for comparison."""
            normalized = skill.lower().replace("-", " ").replace("_", " ").replace(".", " ").strip()
            # Handle special cases
            if "scikit" in normalized or "sklearn" in normalized:
                return "scikit learn"
            if "power bi" in normalized or "powerbi" in normalized:
                return "power bi"
            if "node.js" in normalized or "nodejs" in normalized:
                return "node js"
            if "apache spark" in normalized or "pyspark" in normalized:
                return "apache spark"
            if "apache airflow" in normalized:
                return "apache airflow"
            if normalized == "ml":
                return "machine learning"
            if normalized == "ai":
                return "artificial intelligence"
            if "ci/cd" in normalized or "cicd" in normalized:
                return "ci cd"
            return normalized
        
        candidat_skills_normalized = [normalize_skill(s) for s in candidat_skills]
        
        # Check required skills
        skills_correspondantes = []
        skills_manquantes = []
        
        for skill_requis in skills_obligatoires:
            skill_req_normalized = normalize_skill(skill_requis)
            # Check if candidate has this skill or similar
            matched = False
            
            # Try multiple matching strategies
            for cand_skill_norm in candidat_skills_normalized:
                # Strategy 1: Exact match
                if skill_req_normalized == cand_skill_norm:
                    skills_correspondantes.append(skill_requis)
                    matched = True
                    break
                
                # Strategy 2: Substring match (either direction)
                if (skill_req_normalized in cand_skill_norm or 
                    cand_skill_norm in skill_req_normalized):
                    # Additional check: ensure it's not a false positive
                    # (e.g., "python" shouldn't match "pythonic" unless it's clearly the skill)
                    if len(skill_req_normalized) >= 4:  # Avoid matching very short strings
                        skills_correspondantes.append(skill_requis)
                        matched = True
                        break
                
                # Strategy 3: Word-based matching (for multi-word skills)
                req_words = set(skill_req_normalized.split())
                cand_words = set(cand_skill_norm.split())
                if len(req_words) > 1 and len(cand_words) > 1:
                    # Check if most words match
                    common_words = req_words.intersection(cand_words)
                    if len(common_words) >= min(2, len(req_words) - 1):
                        skills_correspondantes.append(skill_requis)
                        matched = True
                        break
            
            if not matched:
                skills_manquantes.append(skill_requis)
        
        # Check optional skills (same robust matching)
        skills_optionnelles_trouvees = []
        for skill_opt in skills_optionnelles:
            skill_opt_normalized = normalize_skill(skill_opt)
            matched = False
            
            for cand_skill_norm in candidat_skills_normalized:
                # Exact match
                if skill_opt_normalized == cand_skill_norm:
                    skills_optionnelles_trouvees.append(skill_opt)
                    matched = True
                    break
                
                # Substring match
                if (skill_opt_normalized in cand_skill_norm or 
                    cand_skill_norm in skill_opt_normalized):
                    if len(skill_opt_normalized) >= 4:
                        skills_optionnelles_trouvees.append(skill_opt)
                        matched = True
                        break
                
                # Word-based matching
                opt_words = set(skill_opt_normalized.split())
                cand_words = set(cand_skill_norm.split())
                if len(opt_words) > 1 and len(cand_words) > 1:
                    common_words = opt_words.intersection(cand_words)
                    if len(common_words) >= min(2, len(opt_words) - 1):
                        skills_optionnelles_trouvees.append(skill_opt)
                        matched = True
                        break
            
            # Don't add to missing list for optional skills
        
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
        """Calculate technical score (0-100) with improved scoring."""
        if total_requis == 0:
            # No required skills, base score on optional
            if total_optionnel > 0:
                return min(100, (optionnel_trouve / total_optionnel) * 100)
            return 50.0  # Default score
        
        # Calculate match percentage for required skills
        match_ratio_required = correspondant / total_requis if total_requis > 0 else 0
        
        # Base score from required skills (70% of total)
        # Use a more generous curve: 80% match = 70 points, 100% match = 100 points
        if match_ratio_required >= 1.0:
            # All required skills present - give full points
            score_requis = 70.0
        elif match_ratio_required >= 0.9:
            # 90%+ match - excellent
            score_requis = 65.0 + (match_ratio_required - 0.9) * 50  # 65-70
        elif match_ratio_required >= 0.75:
            # 75-90% match - very good
            score_requis = 55.0 + (match_ratio_required - 0.75) * 66.67  # 55-65
        elif match_ratio_required >= 0.6:
            # 60-75% match - good
            score_requis = 40.0 + (match_ratio_required - 0.6) * 100  # 40-55
        elif match_ratio_required >= 0.5:
            # 50-60% match - acceptable
            score_requis = 25.0 + (match_ratio_required - 0.5) * 150  # 25-40
        else:
            # Below 50% - poor
            score_requis = match_ratio_required * 50  # 0-25
        
        # Optional skills bonus (30% of total, but more generous)
        if total_optionnel > 0:
            match_ratio_optional = optionnel_trouve / total_optionnel
            # Bonus points for optional skills
            if match_ratio_optional >= 0.8:
                score_optionnel = 30.0  # Max bonus
            elif match_ratio_optional >= 0.6:
                score_optionnel = 20.0 + (match_ratio_optional - 0.6) * 50  # 20-30
            elif match_ratio_optional >= 0.4:
                score_optionnel = 10.0 + (match_ratio_optional - 0.4) * 50  # 10-20
            else:
                score_optionnel = match_ratio_optional * 25  # 0-10
        else:
            score_optionnel = 0
        
        # Bonus for having all required skills
        if correspondant == total_requis and total_requis > 0:
            score_requis = min(100.0, score_requis + 5.0)  # Small bonus
        
        total_score = min(100.0, score_requis + score_optionnel)
        
        return round(total_score, 1)
    
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

