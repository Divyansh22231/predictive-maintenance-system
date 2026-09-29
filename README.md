# Industrial Machine Failure Risk Prediction & Maintenance Recommendation System

An industrial-grade predictive maintenance web application combining traditional Machine Learning, mathematical feature engineering, and an AI-driven explanation layer.

---

## 📌 Architecture & Design Principles

```text
Streamlit Frontend (Deployed separately)
          ↓
FastAPI Backend (Deployed on Render)
          ↓
Python Preprocessing & Validation
          ↓
Mathematical Feature Engineering (Python)
          ↓
Trained Random Forest Classifier (models/random_forest.pkl)
          ↓
Failure Probability & Binary Prediction
          ↓
Deterministic Risk Classification (LOW / MEDIUM / HIGH)
          ↓
LLM Explanation & Maintenance Recommendation (Post-Prediction Layer)
```

### Core Design Rules
- **Streamlit is the user interface.**
- **FastAPI is the backend API.**
- **Random Forest performs the machine failure prediction.**
- **Python performs mathematical preprocessing and feature engineering.**
- **The LLM provides explanation and maintenance recommendations.**
- The LLM is **never** used for data cleaning, outlier detection, feature engineering, encoding, prediction, or probability calculations.
- If the LLM API is unavailable, the application gracefully provides deterministic fallback maintenance guidance without interrupting ML predictions.

---

## 🔬 Mathematical Feature Engineering

The feature vector order and mathematical calculations strictly mirror the trained Random Forest model:

1. **Temperature Difference [K]**:
   $$\Delta T = \text{Process Temperature} - \text{Air Temperature}$$
2. **Power [W]**:
   $$P = \text{Torque [Nm]} \times \text{Rotational Speed [rpm]}$$
3. **Wear-Torque Product [min·Nm]**:
   $$\text{Wear-Torque} = \text{Tool Wear [min]} \times \text{Torque [Nm]}$$
4. **Machine Type One-Hot Encoding**:
   `Type_H`, `Type_L`, `Type_M`

---

## 🚦 Risk Classification Thresholds

Deterministic risk tiers determined directly in Python:

- **LOW Risk**: Failure Probability $< 0.30$ (Normal operation)
- **MEDIUM Risk**: $0.30 \le \text{Failure Probability} < 0.60$ (Inspection recommended)
- **HIGH Risk**: Failure Probability $\ge 0.60$ (Immediate maintenance action required)

---

## 📁 Project Structure

```text
internship_project/
├── backend/
│   ├── Dockerfile
│   ├── llm_service.py       # LLM explanation service with offline fallback
│   ├── main.py              # FastAPI app definition & CORS
│   ├── model_loader.py      # Robust singleton model loader
│   ├── predictor.py         # Mathematical feature engineering & inference
│   ├── requirements.txt     # Minimal backend dependencies
│   └── schemas.py           # Pydantic input/output schemas
├── models/
│   └── random_forest.pkl    # Trained Random Forest classifier
├── data/
│   ├── raw/                 # Machine failure dataset
│   └── processed/
├── notebooks/               # Data exploration & modeling notebooks
├── tests/
│   └── test_prediction.py   # Unit & integration test suite
├── app.py                   # Streamlit frontend
├── requirements-streamlit.txt # Streamlit dependencies
├── .env.example             # Environment configuration template
└── README.md
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root if you want to use live LLM responses or run Streamlit locally connected to the local backend:

```env
# Backend specific
LLM_API_KEY=your_gemini_or_openai_api_key_here
LLM_MODEL=gemini-1.5-flash
FRONTEND_URL=http://localhost:8501

# Streamlit specific
BACKEND_URL=http://localhost:8000
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+

### 1. Backend Setup

```bash
# Navigate to project root
cd internship_project

# Install backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- Backend API: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# In a new terminal window, navigate to project root
cd internship_project

# Install Streamlit dependencies
pip install -r requirements-streamlit.txt

# Set BACKEND_URL to point to local backend if not in .env
# Start Streamlit
streamlit run app.py
```

- Streamlit Dashboard: `http://localhost:8501`

---

## ☁️ Deployment

### 1. Render Deployment (FastAPI Backend)

Deploy the FastAPI backend on Render using the included Dockerfile.

1. Connect your repository to Render.
2. Create a new "Web Service".
3. Choose "Docker" as the runtime.
4. Set the Docker Context to `./` and Dockerfile path to `backend/Dockerfile`.
5. Set environment variables:
   - `LLM_API_KEY`
   - `LLM_MODEL`
   - `FRONTEND_URL` (Set this to your deployed Streamlit URL)
6. Render will automatically inject the `$PORT` variable which the Dockerfile uses.

### 2. Streamlit Deployment (Frontend)

Deploy the Streamlit application (e.g., on Streamlit Community Cloud).

1. Connect your repository.
2. Set the main file to `app.py`.
3. Add the requirement file: `requirements-streamlit.txt`.
4. In advanced settings/secrets, configure the environment variable:
   - `BACKEND_URL` (Set this to your Render backend URL, e.g. `https://your-backend.onrender.com`)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service health metadata and documentation link |
| `GET` | `/health` | Model status check (`model_loaded: true`) |
| `POST` | `/predict` | Machine telemetry ingestion, mathematical calculation, ML prediction, risk classification, and AI explanation |

---

## 🧪 Testing

Run the test suite using Python's native test runner:

```bash
python -m unittest discover -s tests
```
