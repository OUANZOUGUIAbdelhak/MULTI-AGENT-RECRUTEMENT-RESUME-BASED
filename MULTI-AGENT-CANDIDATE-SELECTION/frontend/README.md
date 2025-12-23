# Multi-Agent Candidate Intelligence System - Frontend

A modern, single-page React application that visualizes a multi-agent AI system for intelligent candidate selection.

## 🎨 Features

- **CV Upload**: Drag-and-drop or click to upload CV files (PDF, TXT)
- **Job Offer Input**: Complete form to enter job description, requirements, and details
- **CV Management**: View all uploaded resumes with file details and status
- **Start Evaluation**: Control panel to initiate the multi-agent evaluation process
- **Ultra-modern UI**: Dark mode with glassmorphism effects, gradient backgrounds, and smooth animations
- **Real-time Agent Progress**: Visual representation of 5 AI agents working through the evaluation process
- **Candidate Ranking**: Interactive table with sortable scores and detailed breakdowns
- **Expandable Details**: Click on any candidate to see detailed scores, radar charts, and AI-generated justifications
- **Decision Output**: Highlighted final decision with top candidate recommendation

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- (Optional) Backend API running on `http://localhost:8000` or configure via `.env`

### Installation

```bash
cd frontend
npm install
```

### Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Important:** The frontend requires the backend API to be running. Start the backend first (see Backend Setup below).

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

The production build will be in the `dist` directory.

## 🛠️ Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization (radar charts)
- **Lucide React** - Icon library

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx
│   │   ├── AgentCard.tsx
│   │   ├── AgentProgressSection.tsx
│   │   ├── CandidateTable.tsx
│   │   ├── CandidateDetails.tsx
│   │   ├── DecisionOutput.tsx
│   │   ├── FileUpload.tsx      # CV upload component
│   │   ├── JobOfferForm.tsx    # Job offer input form
│   │   └── EvaluationControl.tsx  # Start evaluation control
│   ├── services/            # API services
│   │   └── api.ts           # Backend API integration
│   ├── data/               # Mock data
│   │   └── mockData.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── utils/              # Utility functions
│   │   └── cn.ts
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🎯 Components Overview

### FileUpload
Drag-and-drop CV upload component with:
- File validation (PDF, TXT)
- Upload progress tracking
- File list with remove functionality
- Status indicators (uploaded, processing, processed)

### JobOfferForm
Form for entering job offer details:
- Job title (required)
- Job description (required)
- Requirements (required)
- Location (optional)
- Salary range (optional)
- Real-time validation

### EvaluationControl
Control panel showing:
- Job offer readiness status
- Number of uploaded CVs
- Start Evaluation button (enabled when ready)
- Evaluation progress indicator

### Header
Displays the system title, subtitle, and current status (Ready/Running/Completed).

### AgentProgressSection
Shows 5 agent cards:
- RH Agent (Job Analysis)
- Profile Agent (CV Analysis)
- Technical Agent
- Soft Skills Agent
- Decision Agent (Final Ranking)

Each card displays status, progress bar, and role description.

### CandidateTable
Interactive table showing:
- Candidate names
- Global, Profile, Technical, and Soft Skills scores
- Recommendation badges
- Sortable columns
- Expandable rows for detailed view

### CandidateDetails
Expandable section showing:
- Score breakdown with animated progress bars
- Radar chart visualization of skills
- AI-generated justification

### DecisionOutput
Final decision card highlighting:
- Top candidate
- Final score and confidence level
- Comprehensive AI justification

## 🎨 Design System

### Colors
- **Blue/Purple**: AI-related elements
- **Green**: Success, recommended candidates
- **Yellow**: Processing states
- **Red**: Rejected, low scores

### Effects
- Glassmorphism cards with backdrop blur
- Gradient backgrounds (deep blue/purple/indigo)
- Smooth transitions and hover effects
- Pulsing animations for active agents

## 📊 Data Flow

### Setup Phase
1. User uploads CV files via drag-and-drop or file picker
2. User fills in job offer details (title, description, requirements)
3. System validates that both CVs and job offer are ready
4. User clicks "Start Evaluation" button

### Evaluation Phase
1. CVs are uploaded to backend (or simulated)
2. Job offer is sent to backend
3. Agents process sequentially:
   - RH Agent analyzes job offer
   - Profile Agent analyzes CVs
   - Technical Agent evaluates technical skills
   - Soft Skills Agent evaluates interpersonal skills
   - Decision Agent generates final ranking
4. Results are displayed in real-time

### Results Phase
1. Candidate table shows all evaluated candidates
2. Detailed breakdown available for each candidate
3. Final decision highlights top candidate
4. User can start a new evaluation

## 🔌 Backend Integration

The frontend is fully connected to the Python backend API. The backend uses:
- **Groq API** for LLM processing
- **LlamaIndex + ChromaDB** for RAG
- **Multi-agent system** (5 agents) for candidate evaluation

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys** in `Config.yaml`:
   ```yaml
   groq:
     api_key: "your-groq-api-key"
   ```

3. **Start the backend API:**
   ```bash
   # Windows
   python backend_api.py
   # or
   start_backend.bat
   
   # Linux/Mac
   python backend_api.py
   # or
   ./start_backend.sh
   ```

4. **Start the frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

The backend API runs on `http://localhost:8000` and the frontend connects automatically.

### API Endpoints Used

- `POST /api/upload-cvs` - Upload CV files
- `POST /api/start-evaluation` - Start evaluation
- `GET /api/evaluation/{id}` - Get evaluation status (polled every 2s)
- `POST /api/build-index` - Rebuild RAG index

See `README_BACKEND_API.md` in the project root for full API documentation.

## 🔄 Agent Simulation

The app simulates agent progression using `setTimeout`:
1. Agents start in "waiting" status
2. They transition to "processing" with animated progress bars
3. Finally, they complete and show "completed" status
4. The system status changes to "completed" when all agents finish

## 📝 Notes

- This is a visualization-only frontend. It does not implement AI logic.
- All data is currently mocked for demonstration purposes.
- The UI is optimized for desktop-first, responsive design.
- All animations use Framer Motion for smooth transitions.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

