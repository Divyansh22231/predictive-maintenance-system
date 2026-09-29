import pandas as pd
from typing import Dict, Any, List, Tuple
from backend.model_loader import load_model
from backend.schemas import MachineInput, SensorOverview, CalculatedFeatures


FEATURE_COLUMNS = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Type_H",
    "Type_L",
    "Type_M",
    "Temperature difference [K]",
    "Power [W]",
    "Wear-Torque product [minNm]",
]


def perform_feature_engineering(input_data: MachineInput) -> Tuple[pd.DataFrame, CalculatedFeatures]:
    """
    Reproduces the exact mathematical feature engineering from the training pipeline.
    """
    temp_diff = round(input_data.process_temperature - input_data.air_temperature, 2)
    power = round(input_data.torque * input_data.rotational_speed, 2)
    wear_torque = round(input_data.tool_wear * input_data.torque, 2)

    features_dict = {
        "Air temperature [K]": [input_data.air_temperature],
        "Process temperature [K]": [input_data.process_temperature],
        "Rotational speed [rpm]": [input_data.rotational_speed],
        "Torque [Nm]": [input_data.torque],
        "Tool wear [min]": [input_data.tool_wear],
        "Type_H": [1 if input_data.machine_type == "H" else 0],
        "Type_L": [1 if input_data.machine_type == "L" else 0],
        "Type_M": [1 if input_data.machine_type == "M" else 0],
        "Temperature difference [K]": [temp_diff],
        "Power [W]": [power],
        "Wear-Torque product [minNm]": [wear_torque],
    }

    df_features = pd.DataFrame(features_dict)[FEATURE_COLUMNS]

    calculated = CalculatedFeatures(
        temperature_difference=temp_diff,
        power=power,
        wear_torque_product=wear_torque,
    )
    return df_features, calculated


def determine_risk_level(probability: float) -> str:
    """
    Classifies risk strictly using Python threshold logic:
    Low: probability < 0.30
    Medium: 0.30 <= probability < 0.60
    High: probability >= 0.60
    """
    if probability < 0.30:
        return "LOW"
    elif probability < 0.60:
        return "MEDIUM"
    else:
        return "HIGH"


def identify_contributing_factors(
    input_data: MachineInput,
    calculated: CalculatedFeatures,
    probability: float,
) -> List[str]:
    """
    Identifies potential contributing factors using model domain knowledge.
    Always uses the required wording: 'Potential contributing factor: ...'
    """
    factors = []

    # 1. Torque check (normal 30-50 Nm, high load > 55 Nm)
    if input_data.torque >= 55.0:
        factors.append(f"Potential contributing factor: Elevated mechanical torque load ({input_data.torque} Nm)")
    elif input_data.torque <= 18.0:
        factors.append(f"Potential contributing factor: Unusually low torque resistance ({input_data.torque} Nm)")

    # 2. Tool wear check (normal 0-150 min, critical > 180 min)
    if input_data.tool_wear >= 180.0:
        factors.append(f"Potential contributing factor: Significant cumulative tool wear ({input_data.tool_wear} min)")

    # 3. Rotational speed check (normal 1380-1750 rpm)
    if input_data.rotational_speed <= 1380.0:
        factors.append(f"Potential contributing factor: Reduced rotational speed ({input_data.rotational_speed} rpm)")
    elif input_data.rotational_speed >= 2200.0:
        factors.append(f"Potential contributing factor: High rotational speed ({input_data.rotational_speed} rpm)")

    # 4. Temperature difference check (normal 9-11 K; < 8.6 K indicates poor heat dissipation)
    if calculated.temperature_difference <= 8.6:
        factors.append(f"Potential contributing factor: Inadequate heat dissipation (Process-Air \u0394T of {calculated.temperature_difference} K)")

    # 5. Overstrain / Power check
    if calculated.wear_torque_product >= 9000.0:
        factors.append(f"Potential contributing factor: High wear-torque overstrain product ({calculated.wear_torque_product} min\u00b7Nm)")
    if calculated.power >= 80000.0:
        factors.append(f"Potential contributing factor: High mechanical power consumption ({calculated.power} W)")

    if not factors:
        if probability >= 0.30:
            factors.append("Potential contributing factor: Cumulative interaction of operating stress metrics")
        else:
            factors.append("Potential contributing factor: None identified (all operating conditions within normal parameters)")

    return factors


def predict_machine_condition(input_data: MachineInput) -> Dict[str, Any]:
    """
    Runs full ML prediction and feature engineering pipeline.
    """
    model = load_model()
    df_features, calculated = perform_feature_engineering(input_data)

    pred_class = int(model.predict(df_features)[0])
    probabilities = model.predict_proba(df_features)[0]
    failure_prob = round(float(probabilities[1]), 4)

    risk_level = determine_risk_level(failure_prob)
    prediction_label = "Machine Failure" if pred_class == 1 or failure_prob >= 0.50 else "No Machine Failure"
    failure_predicted = bool(pred_class == 1 or failure_prob >= 0.50)

    factors = identify_contributing_factors(input_data, calculated, failure_prob)

    sensor_overview = SensorOverview(
        air_temperature=input_data.air_temperature,
        process_temperature=input_data.process_temperature,
        rotational_speed=input_data.rotational_speed,
        torque=input_data.torque,
        tool_wear=input_data.tool_wear,
        machine_type=input_data.machine_type,
    )

    return {
        "prediction": prediction_label,
        "failure_predicted": failure_predicted,
        "failure_probability": failure_prob,
        "risk_level": risk_level,
        "sensor_overview": sensor_overview,
        "calculated_features": calculated,
        "potential_contributing_factors": factors,
    }
