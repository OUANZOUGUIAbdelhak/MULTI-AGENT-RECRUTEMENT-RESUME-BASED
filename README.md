# 🤖 Système Multi-Agents pour la Sélection Intelligente des Candidats

Un système automatisé de sélection de candidats utilisant une architecture multi-agents combinant RAG (LlamaIndex + ChromaDB), IA générative et raisonnement multi-agent.

## 🚀 Quick Start

**New to this project?** Start here: **[START_HERE.md](START_HERE.md)** - Complete setup guide in 3 steps!

For detailed documentation, continue reading below.

## ✨ Fonctionnalités

- **🤖 Architecture Multi-Agents**: 5 agents spécialisés évaluent les candidats sous différents angles
- **🔍 RAG Intelligent**: Recherche de candidats pertinents avec LlamaIndex et ChromaDB
- **📊 Scoring Multi-Critères**: Évaluation profil, technique et soft skills
- **⚖️ Classement Automatique**: Agent décideur génère un classement final justifié
- **📈 Rapports Détaillés**: Justifications complètes et statistiques
- **🎨 Interface Moderne**: Application React moderne avec design glassmorphism et animations fluides

## 🏗️ Architecture des Agents

Le système comprend 5 agents spécialisés:

1. **Agent RH** 📋: Lit les descriptions de poste et les critères du recruteur, génère un profil cible structuré
2. **Agent Profil** 👤: Analyse les CV et lettres de motivation (NER, scoring, extraction de compétences)
3. **Agent Technique** 💻: Évalue les compétences techniques selon les exigences du poste
4. **Agent Soft Skills** 🤝: Évalue les qualités interpersonnelles, la motivation et l'adéquation culturelle
5. **Agent Décideur** ⚖️: Agrège les avis, justifie les classements et génère un rapport final

## 🚀 Installation

### Prérequis

- Python 3.9+
- pip
- Node.js 18+ et npm (pour l'application React)

### Étapes d'installation

1. **Cloner le repository** (si applicable)
```bash
cd MULTI-AGENT-CANDIDATE-SELECTION
```

2. **Créer un environnement virtuel** (recommandé)
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**

   **⚠️ IMPORTANT:** Si vous rencontrez des erreurs de dépendances (torch/torchvision), exécutez d'abord:
   
   **Windows (PowerShell):**
   ```powershell
   .\fix_dependencies.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   pip uninstall torch torchvision transformers sentence-transformers -y
   pip install "torch>=2.0.0,<2.5.0" "torchvision>=0.15.0,<0.20.0"
   pip install "transformers>=4.35.0,<5.0.0" "sentence-transformers>=2.3.0,<3.0.0"
   pip install -r requirements.txt
   ```
   
   Sinon, installez simplement:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les clés API**

   Éditer `Config.yaml` ou définir les variables d'environnement:
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   export GEMINI_API_KEY="your-gemini-api-key"
   ```

   Ou éditer `Config.yaml`:
   ```yaml
   groq:
     api_key: "your-groq-api-key"
   gemini:
     api_key: "your-gemini-api-key"
   ```

5. **Ajouter les Documents**

   Placer les CV des candidats dans `DATA/raw/`:
   ```bash
   DATA/
   ├── raw/
   │   ├── cv_candidat1.pdf
   │   ├── cv_candidat2.txt
   │   └── ...
   └── jobs/
       ├── offre_data_scientist.txt
       └── ...
   ```

6. **Lancer l'Application**

   Le système comprend un backend FastAPI et une application React frontend.
   
   **Étape 1: Démarrer le Backend API**
   ```bash
   # Dans le répertoire principal
   python backend_api.py
   ```
   Le backend sera disponible sur `http://localhost:8000`
   
   **Étape 2: Démarrer le Frontend React**
   ```bash
   # Dans un nouveau terminal
   cd frontend
   npm install  # Seulement la première fois
   npm run dev
   ```
   L'application React sera disponible sur `http://localhost:5173`
   
   **Note:** Le frontend nécessite que le backend soit en cours d'exécution.

7. **Construire l'Index RAG**

   - Ouvrir l'application React dans votre navigateur (`http://localhost:5173`)
   - Téléverser les CVs ou sélectionner des fichiers existants
   - Cliquer sur "Build Index" pour créer l'index vectoriel
   - Attendre la fin de l'indexation (2-5 minutes pour 10 CVs)
   - Commencer les évaluations!

## 📁 Structure du Projet

```
MULTI-AGENT-CANDIDATE-SELECTION/
├── Config.yaml              # Configuration
├── requirements.txt         # Dépendances Python
├── backend_api.py          # API FastAPI backend
├── README.md               # Ce fichier
├── DATA/
│   ├── raw/               # CV des candidats
│   └── jobs/              # Descriptions de poste
├── vectorstore/           # Stockage ChromaDB (créé automatiquement)
├── frontend/              # Application React
│   ├── src/               # Code source React
│   │   ├── components/    # Composants React
│   │   ├── services/      # Services API
│   │   └── App.tsx        # Composant principal
│   ├── package.json       # Dépendances Node.js
│   └── vite.config.ts     # Configuration Vite
├── src/
│   ├── agents/
│   │   ├── agent_rh.py
│   │   ├── agent_profil.py
│   │   ├── agent_technique.py
│   │   ├── agent_softskills.py
│   │   └── agent_decideur.py
│   ├── rag_new/
│   │   ├── rag_system.py  # Système RAG LlamaIndex
│   │   └── __init__.py
│   ├── main.py            # Pipeline multi-agents
│   └── config.py          # Configuration
└── llm_fallback.py        # Mécanisme de fallback LLM
```

## 🎯 Utilisation

### Évaluation de Candidats

1. **Téléverser les CVs**
   - Utiliser le drag-and-drop ou cliquer pour téléverser des fichiers PDF/TXT
   - Ou sélectionner des fichiers existants depuis `DATA/raw/`

2. **Saisir la description de poste**
   - Remplir le formulaire avec le titre, description et exigences du poste
   - Ou sélectionner un fichier depuis `DATA/jobs/`
   - Ajouter des critères supplémentaires (expérience, salaire, lieu, etc.)

3. **Construire l'Index RAG** (première fois)
   - Cliquer sur "Build Index" pour créer l'index vectoriel
   - Attendre la fin de l'indexation

4. **Lancer l'évaluation**
   - Cliquer sur "Start Evaluation"
   - Suivre la progression en temps réel des 5 agents
   - Le système utilise les agents pour évaluer chaque candidat

5. **Consulter les résultats**
   - Tableau interactif avec classement des candidats et scores globaux
   - Cliquer sur un candidat pour voir les détails complets
   - Visualisations (graphiques radar, barres) des scores par dimension
   - Justifications complètes générées par l'IA
   - Décision finale avec recommandation

### Exemple de Résultat

```
Top 3 candidats:
  1. candidat_01 - Score: 92.3/100 (FORTEMENT RECOMMANDÉ)
  2. candidat_02 - Score: 87.1/100 (RECOMMANDÉ)
  3. candidat_03 - Score: 84.5/100 (RECOMMANDÉ)

Justification candidat_01:
- Profil: Expérience adéquate (3 ans), compétences correspondantes: Python, Power BI
- Technique: Score technique: 95.0/100 (excellent, 8/8 compétences)
- Soft Skills: Excellent profil soft skills, motivation élevée
```

## ⚙️ Configuration

Éditer `Config.yaml` pour personnaliser:

- **Répertoire de données**: Où sont stockés les documents
- **Vector store**: Emplacement du stockage ChromaDB
- **Modèle d'embedding**: Modèle HuggingFace
- **Taille des chunks**: Paramètres de découpage des documents
- **Paramètres LLM**: Configuration Groq et Gemini

## 🛠️ Technologies

**Backend:**
- **FastAPI**: Framework API REST moderne et rapide
- **LlamaIndex**: Framework RAG pour la recherche vectorielle
- **ChromaDB**: Base de données vectorielle persistante
- **HuggingFace**: Modèles d'embedding
- **Groq/Gemini**: Fournisseurs LLM (avec fallback automatique)

**Frontend:**
- **React 18**: Framework UI moderne
- **TypeScript**: Typage statique pour une meilleure qualité de code
- **Vite**: Outil de build rapide et serveur de développement
- **TailwindCSS**: Framework CSS utility-first
- **Framer Motion**: Bibliothèque d'animations fluides
- **Recharts**: Visualisation de données (graphiques radar, barres)

## 📝 Notes

- Le système fonctionne sans LLM (recherche de documents uniquement)
- Le LLM permet des réponses intelligentes avec génération de texte
- L'index doit être reconstruit lorsque les documents changent
- ChromaDB stocke les vecteurs de manière persistante dans `vectorstore/`
- Les agents peuvent fonctionner sans LLM (règles et heuristiques)
- Le frontend React nécessite que le backend FastAPI soit en cours d'exécution
- L'application React utilise le polling (toutes les 2 secondes) pour les mises à jour en temps réel

## 📊 Architecture du Pipeline

```
1. Agent RH → Analyse offre → Profil cible structuré
2. RAG System → Recherche candidats pertinents
3. Pour chaque candidat:
   - Agent Profil → Extraction informations CV
   - Agent Technique → Évaluation compétences techniques
   - Agent Soft Skills → Évaluation qualités interpersonnelles
4. Agent Décideur → Agrégation scores → Classement final
5. Génération rapport avec justifications
```

## 🤝 Contribution

N'hésitez pas à soumettre des issues et des demandes d'amélioration!

## 📄 Licence

Ce projet est open source et disponible pour utilisation.
