import os
import json
import logging
from typing import Dict, Any
import httpx
from backend.schemas import AIAnalysis

logger = logging.getLogger(__name__)


def generate_fallback_analysis(ml_output: Dict[str, Any]) -> AIAnalysis:
    """
    Generates a deterministic, domain-grounded engineering explanation
    when the external LLM API is unavailable, unconfigured, or errors.
    """
    prediction = ml_output["prediction"]
    probability = ml_output["failure_probability"]
    risk = ml_output["risk_level"]
    sensors = ml_output["sensor_overview"]
    calculated = ml_output["calculated_features"]
    factors = ml_output["potential_contributing_factors"]

    percent_str = f"{probability * 100:.1f}%"

    if risk == "HIGH":
        summary = (
            f"High risk condition detected: The machine demonstrates an estimated failure probability "
            f"of {percent_str}, indicating significant mechanical or thermal operational strain."
        )
        why = (
            f"The Random Forest model classified this state as '{prediction}' due to abnormal interaction "
            f"between mechanical load ({sensors.torque} Nm), rotational speed ({sensors.rotational_speed} rpm), "
            f"and tool wear accumulation ({sensors.tool_wear} min)."
        )
        contributing = "; ".join(factors)
        recommendation = (
            "Immediate maintenance action required: Schedule urgent tool inspection and spindle load audit. "
            "Inspect cutter inserts for severe chipping or wear, and verify lubrication levels."
        )
        advice = (
            "Halt or reduce feed rate and cutting speed temporarily until physical inspection is complete. "
            "Do not exceed rated spindle torque limits during high-hardness workpiece operations."
        )
    elif risk == "MEDIUM":
        summary = (
            f"Elevated risk alert: Machine failure probability is moderately elevated at {percent_str}, "
            f"warranting preventive inspection before the next production shift."
        )
        why = (
            f"Operating conditions show emerging stress patterns (delta T = {calculated.temperature_difference} K, "
            f"power = {calculated.power:,.0f} W). While not an imminent crash, parameters approach upper tolerance thresholds."
        )
        contributing = "; ".join(factors)
        recommendation = (
            "Preventive maintenance recommended: Inspect cutting tool wear profile during the next scheduled downtime. "
            "Check heat exchange radiators and coolant fluid flow rates."
        )
        advice = (
            "Maintain continuous sensor telemetry monitoring. Plan tool replacement if tool wear exceeds 180 minutes."
        )
    else:
        summary = (
            f"Nominal operating status: The machine operates in a healthy state with a low failure probability of {percent_str}."
        )
        why = (
            f"All telemetry readings (speed = {sensors.rotational_speed} rpm, torque = {sensors.torque} Nm, "
            f"tool wear = {sensors.tool_wear} min) remain well within verified safe baseline thresholds."
        )
        contributing = "; ".join(factors)
        recommendation = (
            "Routine maintenance only: Continue standard operating procedures and maintain regular shift inspection logs."
        )
        advice = (
            "Proceed with regular production throughput. Keep monitoring thermal and vibration indicators continuously."
        )

    return AIAnalysis(
        summary=summary,
        why_this_prediction=why,
        potential_contributing_factors=contributing,
        maintenance_recommendation=recommendation,
        operational_advice=advice,
        is_fallback=True,
    )


def generate_llm_analysis(ml_output: Dict[str, Any]) -> AIAnalysis:
    """
    Calls an external LLM API if configured to provide an intelligent maintenance explanation.
    Falls back gracefully to the rule-based expert analysis if unavailable.
    """
    api_key = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_fallback_analysis(ml_output)

    model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")

    prediction = ml_output["prediction"]
    probability = ml_output["failure_probability"]
    risk = ml_output["risk_level"]
    sensors = ml_output["sensor_overview"]
    calculated = ml_output["calculated_features"]
    factors = ml_output["potential_contributing_factors"]

    prompt = f"""You are an industrial predictive maintenance expert assisting plant operators.
A Random Forest machine learning model has already performed the prediction and risk classification.
Your role is SOLELY to explain the machine condition and recommend maintenance steps.

DO NOT change the prediction, probability, or risk.
DO NOT claim absolute certainty.
DO use the wording 'Potential contributing factor' when referencing factors.

MACHINE DATA:
- Prediction: {prediction}
- Failure Probability: {probability * 100:.1f}%
- Risk Level: {risk}
- Air Temperature: {sensors.air_temperature} K
- Process Temperature: {sensors.process_temperature} K
- Rotational Speed: {sensors.rotational_speed} rpm
- Torque: {sensors.torque} Nm
- Tool Wear: {sensors.tool_wear} min
- Machine Type: {sensors.machine_type}
- Calculated Temp Difference: {calculated.temperature_difference} K
- Calculated Power: {calculated.power} W
- Calculated Wear-Torque Product: {calculated.wear_torque_product} min*Nm
- Identified Potential Factors: {', '.join(factors)}

Respond in valid JSON format ONLY with the following exact keys:
{{
  "summary": "<1-2 sentence overview of machine status>",
  "why_this_prediction": "<explanation of why the model reached this result based on the sensors>",
  "potential_contributing_factors": "<discussion of potential contributing factors using cautious terminology>",
  "maintenance_recommendation": "<concrete shop-floor actions for maintenance technicians>",
  "operational_advice": "<immediate operational guidance for machine operators>"
}}
"""

    try:
        # Determine provider: Gemini API vs OpenAI-compatible API
        if "gemini" in model_name.lower():
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # Standard OpenAI-compatible API
            base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
            url = f"{base_url.rstrip('/')}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"]

        parsed = json.loads(raw_text)
        return AIAnalysis(
            summary=parsed.get("summary", "Analysis completed."),
            why_this_prediction=parsed.get("why_this_prediction", "Based on machine telemetry."),
            potential_contributing_factors=parsed.get("potential_contributing_factors", "; ".join(factors)),
            maintenance_recommendation=parsed.get("maintenance_recommendation", "Inspect machine condition."),
            operational_advice=parsed.get("operational_advice", "Monitor ongoing operations."),
            is_fallback=False,
        )
    except Exception as e:
        logger.warning(f"LLM API call failed ({e}). Using deterministic expert fallback analysis.")
        return generate_fallback_analysis(ml_output)
