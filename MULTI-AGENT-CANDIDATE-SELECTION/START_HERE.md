# 🚀 Quick Start Guide - Multi-Agent Candidate Selection System

Welcome! This guide will help you get the system up and running in **less than 10 minutes**.

## 📋 Prerequisites

Before you begin, make sure you have:

- ✅ **Python 3.9 or higher** ([Download here](https://www.python.org/downloads/))
- ✅ **Node.js 18+ and npm** ([Download here](https://nodejs.org/))
- ✅ **API Keys** (optional but recommended):
  - [Groq API Key](https://console.groq.com/) (free tier available)
  - [Google Gemini API Key](https://makersuite.google.com/app/apikey) (optional, for fallback)

---

## ⚡ Quick Setup (3 Steps)

### Step 1: Install Python Dependencies

Open a terminal in the project root directory (`MULTI-AGENT-CANDIDATE-SELECTION`) and run:

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**⚠️ Troubleshooting**: If you encounter errors with `torch` or `transformers`, try:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Step 2: Configure API Keys

Edit `Config.yaml` and add your API keys:

```yaml
groq:
  api_key: "your-groq-api-key-here"  # Get from https://console.groq.com/
  
gemini:
  api_key: "your-gemini-api-key-here"  # Optional, get from https://makersuite.google.com/app/apikey
```

**💡 Note**: The system works without API keys, but LLM features (justifications, advanced extraction) won't be available.

### Step 3: Start the System

#### Option A: Full Stack (Backend + Frontend) - **Recommended**

**Terminal 1 - Start Backend:**
```bash
# Windows
python backend_api.py

# Or use the batch file
start_backend.bat

# Mac/Linux
python backend_api.py
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm install  # Only needed first time
npm run dev
```

Then open your browser to: **http://localhost:5173**

#### Option B: Streamlit Interface (Backend Only)

```bash
streamlit run src/app/app.py
```

Then open your browser to: **http://localhost:8501**

---

## 📁 Project Structure

```
MULTI-AGENT-CANDIDATE-SELECTION/
├── START_HERE.md          ← You are here!
├── README.md             ← Detailed documentation
├── Config.yaml           ← Configuration file (add API keys here)
├── requirements.txt      ← Python dependencies
├── backend_api.py        ← FastAPI backend (for React frontend)
│
├── DATA/                 ← Your data goes here
│   ├── raw/             ← Put candidate CVs here (PDF or TXT)
│   └── jobs/            ← Put job descriptions here (TXT or PDF)
│
├── frontend/             ← React frontend application
│   ├── src/             ← React source code
│   └── package.json     ← Node.js dependencies
│
└── src/                  ← Python backend source code
    ├── agents/          ← 5 specialized AI agents
    ├── rag_new/         ← RAG system (LlamaIndex + ChromaDB)
    └── app/             ← Streamlit interface
```

---

## 🎯 First Time Usage

### 1. Add Sample Data

The project comes with sample CVs and job offers in the `DATA/` folder. You can:
- **Add your own CVs**: Place PDF or TXT files in `DATA/raw/`
- **Add job offers**: Place job descriptions in `DATA/jobs/`

### 2. Build the RAG Index

**If using React Frontend:**
1. Open http://localhost:5173
2. Upload CVs or select existing files
3. Click "Build Index" to create the vector database
4. Wait for indexing to complete (~2-5 minutes for 10 CVs)

**If using Streamlit:**
1. Open http://localhost:8501
2. Click "🚀 Initialize System" in sidebar
3. Click "🔨 Build Index"
4. Wait for completion

### 3. Start Evaluation

1. **Enter Job Description**:
   - Upload a job offer file, OR
   - Manually enter job details (title, description, requirements)

2. **Select Candidates**:
   - Choose CVs to evaluate (or use all available)

3. **Click "Start Evaluation"**:
   - Watch the 5 agents work in real-time
   - See progress updates for each agent
   - View results as they're generated

4. **Review Results**:
   - See ranked candidates with scores
   - View detailed breakdowns (Profile, Technical, Soft Skills)
   - Read AI-generated justifications
   - Explore visualizations (radar charts, score comparisons)

---

## 🔧 Common Issues & Solutions

### Issue: "Module not found" errors

**Solution**: Make sure you're in the correct directory and virtual environment is activated:
```bash
cd MULTI-AGENT-CANDIDATE-SELECTION
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux
```

### Issue: Backend won't start

**Solution**: Check if port 8000 is available:
```bash
# Windows
netstat -ano | findstr :8000
# Mac/Linux
lsof -i :8000
```

If port is in use, edit `backend_api.py` and change the port number.

### Issue: Frontend can't connect to backend

**Solution**: 
1. Make sure backend is running on port 8000
2. Check `frontend/src/services/api.ts` - API URL should be `http://localhost:8000`
3. Check browser console for CORS errors

### Issue: "No LLM available" warnings

**Solution**: This is normal if you haven't added API keys. The system works without LLMs but with limited features. Add API keys to `Config.yaml` for full functionality.

### Issue: Index building fails

**Solution**:
1. Make sure CVs are in `DATA/raw/` folder
2. Check file formats (PDF or TXT supported)
3. Ensure files are readable (not corrupted)
4. Check disk space (vector database needs space)

---

## 📊 Understanding the Results

### Score Breakdown

- **Profile Score (30%)**: Experience, education, basic skills match
- **Technical Score (40%)**: Required and optional technical skills
- **Soft Skills Score (30%)**: Communication, teamwork, leadership, motivation

### Global Score

- **≥80**: Fortement recommandé (Strongly Recommended) 🟢
- **65-79**: Recommandé (Recommended) 🟡
- **50-64**: À considérer (Consider) 🟠
- **<50**: À rejeter (Reject) 🔴

### Agent Roles

1. **RH Agent**: Analyzes job requirements
2. **Profile Agent**: Extracts CV information
3. **Technical Agent**: Evaluates technical skills
4. **Soft Skills Agent**: Assesses interpersonal qualities
5. **Decision Agent**: Generates final ranking and justifications

---

## 🎓 Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🔍 Explore [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) for architecture details
- 🎨 Customize `Config.yaml` for your needs
- 🚀 Add your own CVs and job offers to test the system

---

## 💡 Tips

1. **Start Small**: Test with 3-5 CVs first to understand the system
2. **Use Sample Data**: The included sample CVs are great for testing
3. **Check Logs**: Backend terminal shows detailed processing information
4. **API Keys**: Get free API keys from Groq (very generous free tier)
5. **Performance**: Index building takes time - be patient on first run

---

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed information
- Review [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) for technical details
- Check terminal output for error messages
- Ensure all prerequisites are installed correctly

---

## ✅ Quick Checklist

Before running the system, verify:

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`cd frontend && npm install`)
- [ ] API keys added to `Config.yaml` (optional)
- [ ] CVs in `DATA/raw/` folder
- [ ] Job offers in `DATA/jobs/` folder (or ready to enter manually)

---

**🎉 You're all set! Start the system and begin evaluating candidates.**

For detailed information, see [README.md](README.md)

