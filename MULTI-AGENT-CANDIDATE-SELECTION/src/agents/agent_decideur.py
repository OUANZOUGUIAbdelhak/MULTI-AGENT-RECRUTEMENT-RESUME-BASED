"""
Agent Décideur - Aggregates agent opinions and generates final ranking
Justifies decisions and produces comprehensive reports
"""

from typing import Dict, List, Any, Optional


class AgentDecideur:
    """
    Agent Décideur: Aggregates all agent evaluations.
    Generates final ranking with justifications.
    """
    
    # Scoring weights
    WEIGHT_PROFIL = 0.3
    WEIGHT_TECHNIQUE = 0.4
    WEIGHT_SOFTSKILLS = 0.3
    
    def __init__(self, llm=None):
        """
        Initialize Agent Décideur.
        
        Args:
            llm: Optional LLM for advanced justification generation
        """
        self.llm = llm
    
    def classer_candidats(self,
                         evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank candidates based on all agent evaluations.
        
        Args:
            evaluations: List of candidate evaluations from all agents
            
        Returns:
            Ranked list of candidates with scores and justifications
        """
        # Calculate global scores
        for eval_data in evaluations:
            score_global = self._calculate_global_score(
                eval_data.get("score_profil", 0),
                eval_data.get("score_technique", 0),
                eval_data.get("score_softskills", 0)
            )
            eval_data["score_global"] = score_global
            
            # Generate recommendation
            eval_data["recommandation"] = self._generate_recommendation(score_global)
            
            # Generate justification
            eval_data["justification"] = self._generer_justification(eval_data)
        
        # Sort by global score (descending)
        evaluations_sorted = sorted(
            evaluations,
            key=lambda x: x.get("score_global", 0),
            reverse=True
        )
        
        return evaluations_sorted
    
    def _calculate_global_score(self,
                               score_profil: float,
                               score_technique: float,
                               score_softskills: float) -> float:
        """Calculate weighted global score."""
        score = (
            score_profil * self.WEIGHT_PROFIL +
            score_technique * self.WEIGHT_TECHNIQUE +
            score_softskills * self.WEIGHT_SOFTSKILLS
        )
        return round(score, 2)
    
    def _generate_recommendation(self, score_global: float) -> str:
        """Generate recommendation based on global score."""
        if score_global >= 80:
            return "Fortement recommandé"
        elif score_global >= 65:
            return "Recommandé"
        elif score_global >= 50:
            return "À considérer"
        else:
            return "À rejeter"
    
    def _generer_justification(self, eval_data: Dict[str, Any]) -> str:
        """Generate comprehensive justification for candidate."""
        candidate_id = eval_data.get("candidate_id", "N/A")
        score_global = eval_data.get("score_global", 0)
        score_profil = eval_data.get("score_profil", 0)
        score_technique = eval_data.get("score_technique", 0)
        score_softskills = eval_data.get("score_softskills", 0)
        recommandation = eval_data.get("recommandation", "")
        
        justification_parts = [
            f"Candidat: {candidate_id}",
            f"Score global: {score_global:.1f}/100",
            f"Recommandation: {recommandation}",
            "",
            "Détail des scores:",
            f"- Profil: {score_profil:.1f}/100 - {eval_data.get('commentaire_profil', '')[:100]}",
            f"- Technique: {score_technique:.1f}/100 - {eval_data.get('commentaire_technique', '')[:100]}",
            f"- Soft Skills: {score_softskills:.1f}/100 - {eval_data.get('commentaire_softskills', '')[:100]}",
            "",
            "Points forts:"
        ]
        
        # Add strengths
        if score_technique >= 70:
            justification_parts.append(f"✓ Excellente adéquation technique")
        if score_softskills >= 70:
            justification_parts.append(f"✓ Bon profil soft skills")
        if score_profil >= 70:
            justification_parts.append(f"✓ Profil expérimenté")
        
        # Add areas for improvement
        if score_technique < 50:
            justification_parts.append(f"⚠ Compétences techniques à renforcer")
        if score_softskills < 50:
            justification_parts.append(f"⚠ Soft skills à développer")
        
        return "\n".join(justification_parts)
    
    def generer_rapport_final(self,
                             evaluations: List[Dict[str, Any]],
                             job_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final comprehensive report.
        
        Args:
            evaluations: Ranked candidate evaluations
            job_profile: Target job profile
            
        Returns:
            Comprehensive report dictionary
        """
        total_candidats = len(evaluations)
        
        if total_candidats == 0:
            return {
                "resume": "Aucun candidat évalué",
                "statistiques": {},
                "top_candidats": []
            }
        
        # Calculate statistics
        scores_globaux = [e.get("score_global", 0) for e in evaluations]
        scores_techniques = [e.get("score_technique", 0) for e in evaluations]
        scores_softskills = [e.get("score_softskills", 0) for e in evaluations]
        
        stats = {
            "total_candidats": total_candidats,
            "score_moyen": sum(scores_globaux) / total_candidats if scores_globaux else 0,
            "score_max": max(scores_globaux) if scores_globaux else 0,
            "score_min": min(scores_globaux) if scores_globaux else 0,
            "score_technique_moyen": sum(scores_techniques) / total_candidats if scores_techniques else 0,
            "score_softskills_moyen": sum(scores_softskills) / total_candidats if scores_softskills else 0
        }
        
        # Top 3 candidates
        top_candidats = evaluations[:3]
        
        # Generate summary
        resume = self._generate_summary(evaluations, job_profile, stats)
        
        return {
            "resume": resume,
            "statistiques": stats,
            "top_candidats": top_candidats,
            "job_profile": job_profile
        }
    
    def _generate_summary(self,
                         evaluations: List[Dict],
                         job_profile: Dict,
                         stats: Dict) -> str:
        """Generate executive summary."""
        poste = job_profile.get("poste", "Poste")
        total = stats.get("total_candidats", 0)
        score_moyen = stats.get("score_moyen", 0)
        
        summary_parts = [
            f"Rapport d'évaluation pour le poste: {poste}",
            f"",
            f"Total de candidats évalués: {total}",
            f"Score moyen: {score_moyen:.1f}/100",
            f"",
            "Top 3 candidats recommandés:"
        ]
        
        for i, candidate in enumerate(evaluations[:3], 1):
            candidate_id = candidate.get("candidate_id", "N/A")
            score = candidate.get("score_global", 0)
            recommandation = candidate.get("recommandation", "")
            summary_parts.append(
                f"{i}. {candidate_id} - Score: {score:.1f}/100 ({recommandation})"
            )
        
        return "\n".join(summary_parts)

