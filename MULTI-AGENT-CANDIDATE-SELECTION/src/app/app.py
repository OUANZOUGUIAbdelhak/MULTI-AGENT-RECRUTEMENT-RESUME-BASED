"""
Multi-Agent Candidate Selection System
Beautiful interface for evaluating candidates using multi-agent architecture
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root.parent))

# Lazy imports to avoid dependency issues at startup
try:
    from src.main import MultiAgentPipeline
    from src.rag_new.rag_system import create_rag_system_from_config
    from src.config import RAW_DIR, DATA_DIR
    import pdfplumber
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Système Multi-Agents - Sélection de Candidats",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful design
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #ec4899;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .candidate-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #6366f1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .score-excellent { background: #10b981; color: white; }
    .score-good { background: #3b82f6; color: white; }
    .score-fair { background: #f59e0b; color: white; }
    .score-poor { background: #ef4444; color: white; }
    
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None
if "index_built" not in st.session_state:
    st.session_state.index_built = False


def initialize_systems():
    """Initialize RAG system and pipeline."""
    if st.session_state.rag_system is None:
        with st.spinner("🔄 Initializing RAG system..."):
            try:
                st.session_state.rag_system = create_rag_system_from_config()
                # Try to load existing index
                if st.session_state.rag_system.load_index():
                    st.session_state.index_built = True
                return True
            except Exception as e:
                st.warning(f"⚠️ RAG system initialization: {e}")
                st.session_state.rag_system = None
                return False
    return True


def build_index():
    """Build the vector index."""
    if st.session_state.rag_system is None:
        st.warning("⚠️ Please initialize the RAG system first.")
        return False
    
    with st.spinner("🔨 Building vector index... This may take a few minutes."):
        try:
            st.session_state.rag_system.build_index()
            st.session_state.index_built = True
            return True
        except Exception as e:
            st.error(f"❌ Failed to build index: {e}")
            return False


def extract_text_from_file(file_path: Path) -> str:
    """Extract text from file (PDF or TXT)."""
    try:
        if file_path.suffix.lower() == ".pdf":
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)
        else:
            return file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        st.error(f"Error reading file {file_path.name}: {e}")
        return ""


# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: #6366f1; margin-bottom: 0.5rem;">🤖 Multi-Agents</h2>
        <p style="color: #94a3b8; font-size: 0.9rem;">Sélection Intelligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize button
    if st.button("🚀 Initialize System", use_container_width=True, type="primary"):
        if initialize_systems():
            st.success("✅ System initialized!")
            st.session_state.pipeline = MultiAgentPipeline(st.session_state.rag_system)
            st.rerun()
    
    st.markdown("---")
    
    # Index management
    st.subheader("📚 Index RAG")
    
    if st.button("🔨 Build Index", use_container_width=True):
        if build_index():
            st.success("✅ Index built successfully!")
            if st.session_state.rag_system:
                st.session_state.pipeline = MultiAgentPipeline(st.session_state.rag_system)
            st.rerun()
    
    st.markdown("---")
    
    # Status
    st.subheader("📊 Status")
    if st.session_state.pipeline:
        st.success("✅ Pipeline Ready")
    else:
        st.warning("⚠️ Not Initialized")
    
    if st.session_state.index_built:
        st.success("✅ Index Ready")
    else:
        st.warning("⚠️ Index Not Built")
    
    st.markdown("---")
    
    # Statistics
    st.subheader("📈 Statistics")
    if RAW_DIR.exists():
        candidate_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
        st.metric("Candidates Available", len(candidate_files))


# Main content
st.markdown("""
<div class="main-header">
    <h1>🤖 Système Multi-Agents pour la Sélection Intelligente des Candidats</h1>
    <p>Évaluation automatisée avec 5 agents spécialisés + RAG (LlamaIndex + ChromaDB)</p>
</div>
""", unsafe_allow_html=True)

# Check initialization
if st.session_state.pipeline is None:
    st.info("👈 Please initialize the system from the sidebar to begin.")
    st.stop()

# Main interface
tab1, tab2 = st.tabs(["🎯 Évaluation de Candidats", "📄 Gestion des Données"])

with tab1:
    st.header("Évaluation de Candidats")
    
    # Job description input
    st.subheader("1️⃣ Description de l'Offre d'Emploi")
    
    input_method = st.radio(
        "Méthode de saisie",
        ["📝 Texte manuel", "📄 Fichier"],
        horizontal=True
    )
    
    job_description = ""
    
    if input_method == "📄 Fichier":
        jobs_dir = DATA_DIR / "jobs"
        if jobs_dir.exists():
            job_files = list(jobs_dir.glob("*.pdf")) + list(jobs_dir.glob("*.txt"))
            if job_files:
                selected_file = st.selectbox(
                    "Sélectionner un fichier",
                    [f.name for f in job_files]
                )
                if selected_file:
                    file_path = jobs_dir / selected_file
                    job_description = extract_text_from_file(file_path)
            else:
                st.warning("Aucun fichier d'offre trouvé dans DATA/jobs/")
    
    job_description_input = st.text_area(
        "Description de l'offre d'emploi",
        value=job_description,
        height=200,
        placeholder="Exemple:\nData Scientist\n\nNous recherchons un Data Scientist avec 2 ans d'expérience minimum.\nCompétences requises: Python, Machine Learning, Power BI.\nLangues: Français, Anglais."
    )
    
    # Additional criteria
    with st.expander("➕ Critères supplémentaires (optionnel)"):
        col1, col2 = st.columns(2)
        with col1:
            exp_min = st.number_input("Expérience minimale (années)", min_value=0, value=0)
            salaire_min = st.number_input("Salaire minimum", min_value=0, value=0)
        with col2:
            exp_max = st.number_input("Expérience maximale (années)", min_value=0, value=0)
            salaire_max = st.number_input("Salaire maximum", min_value=0, value=0)
        
        lieu = st.text_input("Lieu", placeholder="ex: Paris, Remote")
        contrat = st.selectbox("Type de contrat", ["", "CDI", "CDD", "Stage", "Alternance", "Freelance"])
    
    criteres = {}
    if exp_min > 0:
        criteres["exp_min"] = exp_min
    if exp_max > 0:
        criteres["exp_max"] = exp_max
    if salaire_min > 0:
        criteres["salaire_min"] = salaire_min
    if salaire_max > 0:
        criteres["salaire_max"] = salaire_max
    if lieu:
        criteres["lieu"] = lieu
    if contrat:
        criteres["contrat"] = contrat
    
    # Evaluation button
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        evaluate_button = st.button("🚀 Lancer l'Évaluation", type="primary", use_container_width=True)
    
    with col2:
        use_rag = st.checkbox("Utiliser RAG pour la recherche de candidats", value=st.session_state.index_built)
        max_candidates = st.slider("Nombre maximum de candidats", 1, 20, 10)
    
    # Process evaluation
    if evaluate_button and job_description_input.strip():
        with st.spinner("🤖 Évaluation en cours avec les 5 agents... Cela peut prendre quelques minutes."):
            try:
                results = st.session_state.pipeline.process_job_offer(
                    job_description_input,
                    criteres if criteres else None,
                    use_rag=use_rag and st.session_state.index_built,
                    max_candidates=max_candidates
                )
                
                st.session_state.evaluation_results = results
                st.success("✅ Évaluation terminée!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de l'évaluation: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results
    if "evaluation_results" in st.session_state:
        results = st.session_state.evaluation_results
        
        st.markdown("---")
        st.subheader("📊 Résultats de l'Évaluation")
        
        # Job profile
        with st.expander("📋 Profil de l'Offre Analysé (Agent RH)"):
            job_profile = results["job_profile"]
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Poste:**", job_profile.get("poste", "N/A"))
                st.write("**Séniorité:**", job_profile.get("seniorite", "N/A"))
                st.write("**Expérience min:**", job_profile.get("exp_min", 0), "ans")
                st.write("**Lieu:**", job_profile.get("lieu", "N/A"))
            with col2:
                st.write("**Compétences obligatoires:**")
                for skill in job_profile.get("skills_obligatoires", [])[:10]:
                    st.write(f"- {skill}")
                st.write("**Langues:**", ", ".join(job_profile.get("langues", [])))
        
        # Candidate rankings
        candidates = results["candidates_evaluated"]
        
        if candidates:
            st.subheader(f"🏆 Classement des Candidats ({len(candidates)} évalué(s))")
            
            # Filter by recommendation
            filter_rec = st.selectbox(
                "Filtrer par recommandation",
                ["Tous", "Fortement recommandé", "Recommandé", "À considérer", "À rejeter"]
            )
            
            filtered_candidates = candidates
            if filter_rec != "Tous":
                filtered_candidates = [
                    c for c in candidates
                    if c.get("recommandation", "").lower() == filter_rec.lower()
                ]
            
            # Display top candidates
            for i, candidate in enumerate(filtered_candidates[:10], 1):
                score_global = candidate.get("score_global", 0)
                recommandation = candidate.get("recommandation", "")
                
                # Color based on recommendation
                if "fortement" in recommandation.lower():
                    border_color = "#10b981"
                elif "recommandé" in recommandation.lower():
                    border_color = "#3b82f6"
                elif "considérer" in recommandation.lower():
                    border_color = "#f59e0b"
                else:
                    border_color = "#ef4444"
                
                st.markdown(f"""
                <div class="candidate-card" style="border-left-color: {border_color};">
                    <h3 style="color: white; margin-bottom: 1rem;">
                        {i}. {candidate.get('nom', candidate.get('candidate_id', 'N/A'))} 
                        <span style="font-size: 1.2rem; color: {border_color};">
                            ({recommandation})
                        </span>
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Scores
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Score Global", f"{score_global:.1f}/100")
                with col2:
                    st.metric("Profil", f"{candidate.get('score_profil', 0):.1f}/100")
                with col3:
                    st.metric("Technique", f"{candidate.get('score_technique', 0):.1f}/100")
                with col4:
                    st.metric("Soft Skills", f"{candidate.get('score_softskills', 0):.1f}/100")
                
                # Detailed justification
                with st.expander(f"📝 Justification complète - {candidate.get('nom', 'N/A')}"):
                    st.text(candidate.get("justification", ""))
                    
                    st.markdown("**Commentaires des agents:**")
                    st.write("**Agent Profil:**", candidate.get("commentaire_profil", ""))
                    st.write("**Agent Technique:**", candidate.get("commentaire_technique", ""))
                    st.write("**Agent Soft Skills:**", candidate.get("commentaire_softskills", ""))
                
                st.markdown("---")
            
            # Final report
            st.subheader("📈 Rapport Final (Agent Décideur)")
            report = results["report"]
            st.text(report.get("resume", ""))
            
            # Statistics
            stats = report.get("statistiques", {})
            if stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Candidats", stats.get("total_candidats", 0))
                with col2:
                    st.metric("Score Moyen", f"{stats.get('score_moyen', 0):.1f}")
                with col3:
                    st.metric("Score Max", f"{stats.get('score_max', 0):.1f}")
                with col4:
                    st.metric("Score Min", f"{stats.get('score_min', 0):.1f}")
        else:
            st.warning("Aucun candidat évalué.")


with tab2:
    st.header("Gestion des Données")
    
    st.subheader("📁 Structure des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Candidats")
        if RAW_DIR.exists():
            candidate_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
            st.metric("Candidats disponibles", len(candidate_files))
            
            if candidate_files:
                st.markdown("**Fichiers disponibles:**")
                for file in candidate_files[:10]:
                    st.text(f"  • {file.name}")
                if len(candidate_files) > 10:
                    st.text(f"  ... et {len(candidate_files) - 10} autres")
        else:
            st.warning("Dossier des candidats non trouvé.")
    
    with col2:
        st.markdown("### Offres d'Emploi")
        jobs_dir = DATA_DIR / "jobs"
        if jobs_dir.exists():
            job_files = list(jobs_dir.glob("*.pdf")) + list(jobs_dir.glob("*.txt"))
            st.metric("Offres disponibles", len(job_files))
            
            if job_files:
                st.markdown("**Fichiers disponibles:**")
                for file in job_files[:10]:
                    st.text(f"  • {file.name}")
                if len(job_files) > 10:
                    st.text(f"  ... et {len(job_files) - 10} autres")
        else:
            st.warning("Dossier des offres non trouvé.")
