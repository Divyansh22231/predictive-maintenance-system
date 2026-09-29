import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env if present
load_dotenv()

from backend.model_loader import load_model
from backend.schemas import MachineInput, PredictionResponse, HealthResponse
from backend.predictor import predict_machine_condition
from backend.llm_service import generate_llm_analysis

app = FastAPI(
    title="Predictive Maintenance API",
    description="Machine Failure Risk Monitoring & AI-Assisted Maintenance Recommendation API",
    version="1.0.0",
)

frontend_url = os.getenv("FRONTEND_URL")
origins = [frontend_url] if frontend_url else ["*"]

# Enable CORS for local development and deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Preload model on startup to ensure instant prediction response."""
    try:
        load_model()
    except Exception as e:
        print(f"Warning during model preload: {e}")


@app.get("/", tags=["General"])
def read_root():
    """Root endpoint providing service metadata."""
    return {
        "service": "Predictive Maintenance API",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": ["/health", "/predict"],
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    try:
        model = load_model()
        model_loaded = model is not None
    except Exception:
        model_loaded = False

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(input_data: MachineInput):
    """
    Predict machine failure probability, classify risk level,
    and generate actionable maintenance explanations.
    """
    try:
        # 1. Run ML Pipeline (Feature Engineering + Random Forest Inference + Risk Level)
        ml_output = predict_machine_condition(input_data)

        # 2. Run LLM Analysis Layer (Explanation + Recommendations, with robust fallback)
        ai_analysis = generate_llm_analysis(ml_output)

        return PredictionResponse(
            prediction=ml_output["prediction"],
            failure_predicted=ml_output["failure_predicted"],
            failure_probability=ml_output["failure_probability"],
            risk_level=ml_output["risk_level"],
            sensor_overview=ml_output["sensor_overview"],
            calculated_features=ml_output["calculated_features"],
            potential_contributing_factors=ml_output["potential_contributing_factors"],
            ai_analysis=ai_analysis,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
