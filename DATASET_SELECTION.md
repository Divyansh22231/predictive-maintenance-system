# Dataset Selection

## Project
Industrial Machine Failure Risk Prediction & Maintenance Recommendation System

## Selected Dataset

Dataset Name: AI4I 2020 Predictive Maintenance Dataset
Source: UCI Machine Learning Repository (S. Matzka, 2020)
Source URL: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
License: CC BY 4.0
Number of Rows: 10,000
Number of Columns: 14
Target Column: Machine failure (binary: 0 = No Failure, 1 = Failure)
Failure Records: 339 (≈3.39%)
Non-Failure Records: 9,661 (≈96.61%)

## Input Features

- Type (categorical: L / M / H)
- Air temperature [K]
- Process temperature [K]
- Rotational speed [rpm]
- Torque [Nm]
- Tool wear [min]

UID and Product ID are identifiers and are excluded from modeling.
TWF, HDF, PWF, OSF, and RNF are failure sub-type labels, not input features — they
are components of the target itself and must never be used to predict it (see
Data Dictionary for detail on this leakage risk).

## Why This Dataset Fits

- Machine failure prediction: binary target with a realistic, naturally
  imbalanced failure rate (~3.4%), enough failure cases to train and evaluate on.
- Random Forest / XGBoost: clean numeric + single categorical feature set with
  no missing values, well suited to tree-based ensembles.
- Risk classification: continuous failure probability output maps directly onto
  configurable Low/Medium/High thresholds.
- Explainability: small, physically meaningful feature set (temperature,
  vibration/torque, speed, tool wear) makes both global feature importance and
  local SHAP explanations interpretable and defensible in an interview setting.
- Operational recommendations: each feature maps to a concrete maintenance
  action (e.g. torque/load → inspect mechanical load, tool wear → inspect/replace
  tooling, temperature → inspect cooling).

## Limitations

This dataset is described by UCI as synthetic: it was generated to reflect
realistic predictive-maintenance conditions rather than measured directly from
a physical machine in operation. It is used here because it is the standard,
widely-validated benchmark dataset for this exact problem type, and because
genuinely real-world alternatives investigated for this project were rejected
for the reasons below. This trade-off is disclosed rather than hidden, and the
project should be described accordingly (a benchmark-dataset-based prototype,
not a system validated on live industrial sensor data).

The five failure sub-type columns (TWF, HDF, PWF, OSF, RNF) create a data
leakage risk if mistakenly included as input features, since Machine failure
is derived directly from them.

## Alternative Datasets Considered

- **APS Failure at Scania Trucks** (UCI, real-world truck sensor data, 60,000
  rows): genuinely real-world and large, but its 170 features are anonymized
  for proprietary reasons, so no feature has a stated operational meaning, and
  many rows have substantial missing data. Rejected for conflicting with the
  requirement that every feature have a clear, explainable meaning, and for
  exceeding the project's intended feature-count scope.
- **MetroPT-3** (UCI, real metro-train air compressor sensor data, ~1.5 million
  rows at 1Hz): genuinely real-world with interpretable signals, but it is a
  raw continuous time-series with no pre-built row-level failure label —
  building one requires windowing and manual labeling from separate
  maintenance reports. Rejected for requiring exactly the kind of complex
  time-series engineering this project is scoped to avoid.
