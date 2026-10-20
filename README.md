# GradPath

GradPath is a data-driven career development platform designed to help graduates understand job-market requirements, identify skill gaps, follow learning recommendations, and build evidence of career readiness.

The project focuses on explainable, evidence-based analysis rather than treating every skill mentioned on a CV as a verified competency.

## Target Roles

- Data Analyst
- Data Scientist

## Current Development Status

**Phase 10 - User Interface, integration, and refinement**

GradPath's core analysis modules have been developed. The React frontend and FastAPI backend are being refined and connected into a complete user workflow.

### Implemented Core Capabilities

- **Job-market intelligence:** Collects and processes job-posting data to identify in-demand skills.
- **Skill knowledge base:** Uses ESCO and O*NET occupational and skills information.
- **CV analysis:** Extracts profile information and organizes education, experience, projects, certifications, and skills.
- **Skill-gap analysis:** Compares candidate profiles with role-specific skill requirements.
- **Learning recommendations:** Suggests learning resources based on identified skill gaps.
- **Progress tracking:** Includes a SQLite-based foundation for tracking candidate learning progress.
- **Project and evidence workflow:** Supports the planned process of building practical evidence for career readiness.
- **Readiness scoring:** Combines available profile, learning, assessment, and project evidence to explain readiness results.

## User Interface

The React interface is being developed around five main areas:

- **Overview:** Career summary, detected skills, progress indicators, and suggested next steps.
- **My Career:** CV upload, extracted profile details, and skill evidence.
- **Learning Roadmap:** Recommended learning actions.
- **Project Workspace:** Practical project development and evidence.
- **Readiness Report:** A breakdown of available evidence and career-readiness indicators.

Frontend integration with persistent user-specific CV history, authentication, and progress data is still being refined. Features shown in the interface should not be assumed to be fully connected to persistent storage unless verified.

## Technology Stack

**Backend and analysis**
- Python
- Pandas and NumPy
- scikit-learn
- FastAPI
- SQLite

**Frontend**
- React
- Vite
- JavaScript
- CSS

**Data sources and knowledge**
- ESCO
- O*NET
- Adzuna job-market data

The exact dependencies are maintained in `requirements.txt` and `frontend/package.json`.

## Running Locally

### 1. Start the backend

From the project root, create and activate a Python virtual environment if you have not already done so.

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the API:

```powershell
python -m uvicorn gradpath_api:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

### 2. Start the frontend

Open a second terminal and navigate to the frontend directory:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the local URL printed by Vite in the terminal.

These instructions assume the required project dependencies and local configuration are available. Authentication or other integration issues may still need to be resolved during development.

## Development Principles

- Preserve uncertainty when CV extraction is ambiguous.
- Distinguish skills mentioned in a CV from skills supported by evidence.
- Avoid duplicate or incorrectly grouped CV records.
- Make recommendations and readiness results explainable.
- Evaluate analytical components with tests and measurable metrics.
- Keep raw CV content and personal data handling separate from general skill-market datasets.

## Planned Machine Learning Work

Machine learning improvements are planned after the current interface and integration work:

1. **CV-to-job matching:** Establish a TF-IDF and cosine-similarity baseline, then evaluate whether semantic embeddings improve matching quality.
2. **Skill extraction:** Evaluate ML/NLP-assisted extraction against a labelled test set and the current baseline.
3. **Learning recommendation ranking:** Explore better ranking using role requirements, skill gaps, prerequisites, market demand, and progress.
4. **Model evaluation and tracking:** Record experiments and compare results using appropriate evaluation metrics.

These are planned improvements, not claims that the models have already been integrated.

## Project Goal

GradPath aims to provide graduates with a transparent, personalized pathway from their current skills to the requirements of their target careers, supported by learning activities and practical evidence.

---

**Status:** Active development. Core analysis modules are implemented; UI refinement and end-to-end integration are ongoing.
