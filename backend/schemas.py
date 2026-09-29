from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class MachineInput(BaseModel):
    air_temperature: float = Field(
        ...,
        ge=250.0,
        le=350.0,
        description="Air temperature in Kelvin [K]",
        example=298.1,
    )
    process_temperature: float = Field(
        ...,
        ge=250.0,
        le=350.0,
        description="Process temperature in Kelvin [K]",
        example=308.6,
    )
    rotational_speed: float = Field(
        ...,
        ge=500.0,
        le=5000.0,
        description="Rotational speed in rotations per minute [rpm]",
        example=1551.0,
    )
    torque: float = Field(
        ...,
        ge=0.0,
        le=200.0,
        description="Torque in Newton-metres [Nm]",
        example=42.8,
    )
    tool_wear: float = Field(
        ...,
        ge=0.0,
        le=500.0,
        description="Tool wear time in minutes [min]",
        example=0.0,
    )
    machine_type: Literal["H", "L", "M"] = Field(
        ...,
        description="Product quality type: High (H), Low (L), or Medium (M)",
        example="M",
    )


class SensorOverview(BaseModel):
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float
    machine_type: str


class CalculatedFeatures(BaseModel):
    temperature_difference: float
    power: float
    wear_torque_product: float


class AIAnalysis(BaseModel):
    summary: str
    why_this_prediction: str
    potential_contributing_factors: str
    maintenance_recommendation: str
    operational_advice: str
    is_fallback: bool = False


class PredictionResponse(BaseModel):
    prediction: str
    failure_predicted: bool
    failure_probability: float
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    sensor_overview: SensorOverview
    calculated_features: CalculatedFeatures
    potential_contributing_factors: List[str]
    ai_analysis: AIAnalysis


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
