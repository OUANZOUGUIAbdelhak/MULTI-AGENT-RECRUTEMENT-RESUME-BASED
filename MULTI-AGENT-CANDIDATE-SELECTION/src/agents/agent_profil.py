"""
Agent Profil - Analyzes candidate CVs and cover letters
Extracts structured profile information with NER, scoring, and skill extraction
"""

import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class AgentProfil:
    """
    Agent Profil: Analyzes CVs and cover letters.
    Extracts structured information and calculates profile score.
    """
    
    def __init__(self, llm=None):
        """
        Initialize Agent Profil.
        
        Args:
            llm: Optional LLM for advanced extraction
        """
        self.llm = llm
    
    def analyser_candidat(self, 
                         cv_text: str,
                         lettre_motivation: Optional[str] = None,
                         job_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze candidate CV and extract structured profile.
        
        Args:
            cv_text: CV text content
            lettre_motivation: Cover letter text (optional)
            job_profile: Target job profile for matching
            
        Returns:
            Structured candidate profile with score
        """
        # Extract basic information
        nom = self._extract_name(cv_text)
        email = self._extract_email(cv_text)
        telephone = self._extract_phone(cv_text)
        
        # Extract experience
        experience = self._extract_experience(cv_text)
        years_experience = self._calculate_years_experience(experience)
        
        # Extract education
        education = self._extract_education(cv_text)
        
        # Extract skills
        skills_list = self._extract_skills(cv_text)
        
        # Extract languages
        languages = self._extract_languages(cv_text)
        
        # Calculate profile score
        score_profil = self._calculate_profile_score(
            years_experience, skills_list, education, job_profile
        )
        
        # Generate comment
        commentaire = self._generate_comment(
            nom, years_experience, skills_list, job_profile, score_profil
        )
        
        return {
            "id": self._generate_id(nom, email),
            "nom": nom,
            "email": email,
            "telephone": telephone,
            "years_experience": years_experience,
            "experience": experience,
            "education": education,
            "skills_list": skills_list,
            "languages": languages,
            "score_profil": score_profil,
            "commentaire_profil": commentaire,
            "raw_text": cv_text,
            "lettre_motivation": lettre_motivation or ""
        }
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name (usually first line)."""
        lines = text.split('\n')
        
        # Try first few lines
        for line in lines[:10]:
            line = line.strip()
            if not line:
                continue
                
            # Remove common prefixes/suffixes
            line_clean = re.sub(r'^\s*[A-Z\s]+\s*\|\s*', '', line)  # Remove "TITLE |" prefix
            line_clean = re.sub(r'\s*\|\s*[A-Z\s]+$', '', line_clean)  # Remove "| TITLE" suffix
            line_clean = re.sub(r'^[A-Z\s]+\s*-\s*', '', line_clean)  # Remove "TITLE -" prefix
            line_clean = line_clean.strip()
            
            # Skip if it's clearly not a name (contains @, http, digits, etc.)
            if '@' in line_clean or 'http' in line_clean.lower() or re.search(r'\d{4}', line_clean):
                continue
            
            if len(line_clean) > 3 and len(line_clean) < 50:
                # Pattern 1: All caps (ALEXANDRE MARTIN, SARAH BERNARD)
                if re.match(r'^[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ\s]+$', line_clean):
                    words = line_clean.split()
                    if 2 <= len(words) <= 4:  # Typically 2-4 words for a name
                        return line_clean.title()
                
                # Pattern 2: Title case (Alexandre Martin, Sarah Bernard)
                if re.match(r'^[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ][a-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]+(?:\s+[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ][a-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]+)+$', line_clean):
                    words = line_clean.split()
                    if 2 <= len(words) <= 4:
                        return line_clean
        
        # Fallback: Try to extract from email if available
        email = self._extract_email(text)
        if email:
            # Extract name from email (e.g., "alexandre.martin@email.com" -> "Alexandre Martin")
            email_prefix = email.split('@')[0]
            if '.' in email_prefix:
                name_parts = email_prefix.split('.')
                if len(name_parts) == 2:
                    return f"{name_parts[0].title()} {name_parts[1].title()}"
        
        return "Nom non trouvé"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number."""
        phone_patterns = [
            r'\b0[1-9](?:[.\s-]?\d{2}){4}\b',
            r'\+\d{1,3}[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}'
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return ""
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience."""
        experience = []
        
        # Look for experience section
        exp_keywords = ["expérience", "expérience professionnelle", "parcours", "carrière", "work experience"]
        exp_section = ""
        
        for keyword in exp_keywords:
            idx = text.lower().find(keyword.lower())
            if idx != -1:
                # Extract section
                start = idx
                end = text.find("\n\n", start + 100)
                if end == -1:
                    end = min(start + 2000, len(text))
                exp_section = text[start:end]
                break
        
        if not exp_section:
            exp_section = text
        
        # Extract job entries
        # Pattern: Company/Position - Date range
        patterns = [
            r'([A-Z][^.\n]{10,60})\s*[-–]\s*(\d{4}|\d{1,2}/\d{4})\s*[-–]?\s*(\d{4}|\d{1,2}/\d{4}|présent|aujourd\'hui)?',
            r'([A-Z][^.\n]{10,60})\s*\((\d{4})\s*[-–]\s*(\d{4}|présent)\)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, exp_section, re.MULTILINE)
            for match in matches:
                experience.append({
                    "poste": match.group(1).strip(),
                    "date_debut": match.group(2),
                    "date_fin": match.group(3) if len(match.groups()) > 2 else "présent"
                })
        
        return experience[:10]  # Limit to 10 experiences
    
    def _calculate_years_experience(self, experience: List[Dict]) -> float:
        """Calculate total years of experience."""
        if not experience:
            return 0.0
        
        total_years = 0.0
        for exp in experience:
            try:
                date_debut = exp.get("date_debut", "")
                date_fin = exp.get("date_fin", "présent")
                
                # Extract year
                year_debut = re.search(r'(\d{4})', date_debut)
                if year_debut:
                    year_debut = int(year_debut.group(1))
                    if date_fin.lower() in ["présent", "aujourd'hui", "present"]:
                        from datetime import datetime
                        year_fin = datetime.now().year
                    else:
                        year_fin_match = re.search(r'(\d{4})', date_fin)
                        if year_fin_match:
                            year_fin = int(year_fin_match.group(1))
                        else:
                            continue
                    
                    total_years += (year_fin - year_debut)
            except:
                continue
        
        return max(0.0, total_years)
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information."""
        education = []
        
        edu_keywords = ["formation", "éducation", "diplôme", "éducation", "education", "études"]
        edu_section = ""
        
        for keyword in edu_keywords:
            idx = text.lower().find(keyword.lower())
            if idx != -1:
                start = idx
                end = text.find("\n\n", start + 100)
                if end == -1:
                    end = min(start + 1000, len(text))
                edu_section = text[start:end]
                break
        
        if not edu_section:
            edu_section = text
        
        # Extract degree and school
        degree_patterns = [
            r'(Master|Licence|Bac|Doctorat|PhD|MBA|Ingénieur|École|Université)[^.\n]{0,100}',
            r'([A-Z][^.\n]{10,60})\s*[-–]\s*(\d{4})'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, edu_section)
            for match in matches:
                education.append({
                    "diplome": match.group(0).strip()[:100]
                })
        
        return education[:5]
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills."""
        skills = []
        text_lower = text.lower()
        
        # Normalize text for better matching (replace common variations)
        text_normalized = text_lower.replace("-", " ").replace("_", " ").replace(".", " ")
        
        # Common skills with variations
        skill_keywords = [
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "sql", "nosql", "mongodb", "postgresql", "mysql", "redis",
            "machine learning", "deep learning", "ml", "ai", "artificial intelligence",
            "tensorflow", "pytorch", "scikit-learn", "scikit learn", "sklearn", "keras",
            "pandas", "numpy", "matplotlib", "seaborn",
            "spark", "apache spark", "pyspark", "hadoop", "kafka",
            "aws", "azure", "gcp", "google cloud", "cloud computing", "docker", "kubernetes", "k8s",
            "react", "vue", "angular", "node.js", "nodejs", "django", "flask", "fastapi",
            "power bi", "powerbi", "tableau", "qlik", "looker", "excel",
            "git", "github", "gitlab", "ci/cd", "cicd", "jenkins", "terraform", "ansible",
            "linux", "bash", "shell scripting",
            "agile", "scrum", "kanban",
            "mlops", "mlflow", "kubeflow", "airflow", "apache airflow"
        ]
        
        for skill in skill_keywords:
            skill_normalized = skill.replace("-", " ").replace("_", " ")
            # Check both original and normalized versions
            if skill in text_lower or skill_normalized in text_normalized:
                # Normalize skill name for storage (handle special cases)
                if skill == "c++":
                    skill_stored = "C++"
                elif skill == "c#":
                    skill_stored = "C#"
                elif skill == "ml":
                    skill_stored = "Machine Learning"
                elif skill == "ai":
                    skill_stored = "Artificial Intelligence"
                elif skill == "ci/cd" or skill == "cicd":
                    skill_stored = "CI/CD"
                elif skill == "scikit-learn" or skill == "scikit learn" or skill == "sklearn":
                    skill_stored = "Scikit-learn"
                elif skill == "power bi" or skill == "powerbi":
                    skill_stored = "Power BI"
                elif skill == "node.js" or skill == "nodejs":
                    skill_stored = "Node.js"
                elif skill == "apache spark" or skill == "pyspark":
                    skill_stored = "Apache Spark"
                elif skill == "apache airflow":
                    skill_stored = "Apache Airflow"
                elif "-" in skill:
                    skill_stored = skill.replace(" ", "-").title()
                else:
                    skill_stored = skill.title()
                skills.append(skill_stored)
        
        return list(set(skills))
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages."""
        languages = []
        text_lower = text.lower()
        
        lang_keywords = {
            "français": ["français", "french"],
            "anglais": ["anglais", "english", "anglophone"],
            "espagnol": ["espagnol", "spanish"],
            "allemand": ["allemand", "german", "deutsch"],
            "italien": ["italien", "italian"],
            "chinois": ["chinois", "chinese", "mandarin"]
        }
        
        for lang, keywords in lang_keywords.items():
            if any(kw in text_lower for kw in keywords):
                languages.append(lang.title())
        
        return languages if languages else ["Français"]
    
    def _calculate_profile_score(self, 
                                 years_experience: float,
                                 skills: List[str],
                                 education: List[Dict],
                                 job_profile: Optional[Dict]) -> float:
        """Calculate profile score (0-100)."""
        if not job_profile:
            # Base score without job profile
            exp_score = min(30, years_experience * 5)
            skills_score = min(40, len(skills) * 2)
            edu_score = min(30, len(education) * 10)
            return exp_score + skills_score + edu_score
        
        score = 0.0
        
        # Experience match (30 points)
        exp_min = job_profile.get("exp_min", 0)
        if years_experience >= exp_min:
            score += 30
        elif years_experience >= exp_min * 0.7:
            score += 20
        elif years_experience >= exp_min * 0.5:
            score += 10
        
        # Skills match (50 points)
        required_skills = job_profile.get("skills_obligatoires", [])
        optional_skills = job_profile.get("skills_optionnelles", [])
        
        # Normalize skills for matching
        def normalize_skill_for_match(skill: str) -> str:
            normalized = skill.lower().replace("-", " ").replace("_", " ").replace(".", " ").strip()
            if "scikit" in normalized or "sklearn" in normalized:
                return "scikit learn"
            if "power bi" in normalized or "powerbi" in normalized:
                return "power bi"
            if "node.js" in normalized or "nodejs" in normalized:
                return "node js"
            if normalized == "ml":
                return "machine learning"
            if normalized == "ai":
                return "artificial intelligence"
            return normalized
        
        matched_required = 0
        for skill_req in required_skills:
            skill_req_norm = normalize_skill_for_match(skill_req)
            for skill_cand in skills:
                skill_cand_norm = normalize_skill_for_match(skill_cand)
                if (skill_req_norm == skill_cand_norm or 
                    skill_req_norm in skill_cand_norm or 
                    skill_cand_norm in skill_req_norm):
                    matched_required += 1
                    break
        
        matched_optional = 0
        for skill_opt in optional_skills:
            skill_opt_norm = normalize_skill_for_match(skill_opt)
            for skill_cand in skills:
                skill_cand_norm = normalize_skill_for_match(skill_cand)
                if (skill_opt_norm == skill_cand_norm or 
                    skill_opt_norm in skill_cand_norm or 
                    skill_cand_norm in skill_opt_norm):
                    matched_optional += 1
                    break
        
        if required_skills:
            match_ratio_required = matched_required / len(required_skills)
            
            # More generous scoring for required skills (40 points max)
            if match_ratio_required >= 1.0:
                # All required skills - full points
                skills_score = 40.0
            elif match_ratio_required >= 0.9:
                # 90%+ match - excellent
                skills_score = 36.0 + (match_ratio_required - 0.9) * 40  # 36-40
            elif match_ratio_required >= 0.75:
                # 75-90% match - very good
                skills_score = 30.0 + (match_ratio_required - 0.75) * 40  # 30-36
            elif match_ratio_required >= 0.6:
                # 60-75% match - good
                skills_score = 22.0 + (match_ratio_required - 0.6) * 53.33  # 22-30
            elif match_ratio_required >= 0.5:
                # 50-60% match - acceptable
                skills_score = 15.0 + (match_ratio_required - 0.5) * 70  # 15-22
            else:
                # Below 50% - poor
                skills_score = match_ratio_required * 30  # 0-15
            
            # Optional skills bonus (10 points max, more generous)
            if optional_skills:
                match_ratio_optional = matched_optional / len(optional_skills)
                if match_ratio_optional >= 0.8:
                    optional_score = 10.0  # Max bonus
                elif match_ratio_optional >= 0.6:
                    optional_score = 7.0 + (match_ratio_optional - 0.6) * 15  # 7-10
                elif match_ratio_optional >= 0.4:
                    optional_score = 4.0 + (match_ratio_optional - 0.4) * 15  # 4-7
                else:
                    optional_score = match_ratio_optional * 10  # 0-4
            else:
                optional_score = 0
            
            score += skills_score + optional_score
        else:
            score += min(50, len(skills) * 2)
        
        # Education (20 points)
        if education:
            score += 20
        elif len(education) > 1:
            score += 15
        
        return min(100.0, score)
    
    def _generate_comment(self, 
                         nom: str,
                         years_experience: float,
                         skills: List[str],
                         job_profile: Optional[Dict],
                         score: float) -> str:
        """Generate profile comment."""
        comment_parts = [f"Profil de {nom}:"]
        
        comment_parts.append(f"Expérience: {years_experience:.1f} ans")
        comment_parts.append(f"Compétences: {', '.join(skills[:10])}")
        comment_parts.append(f"Score de profil: {score:.1f}/100")
        
        if job_profile:
            required = job_profile.get("skills_obligatoires", [])
            matched = [s for s in required if any(s.lower() in skill.lower() for skill in skills)]
            if matched:
                comment_parts.append(f"Compétences requises correspondantes: {', '.join(matched)}")
        
        return " | ".join(comment_parts)
    
    def _generate_id(self, nom: str, email: str) -> str:
        """Generate candidate ID."""
        if email:
            return email.split('@')[0]
        return nom.lower().replace(' ', '_')

