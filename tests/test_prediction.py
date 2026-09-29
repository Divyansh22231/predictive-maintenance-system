import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestPredictiveMaintenanceAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """Test GET / returns 200 and expected metadata."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("docs_url", data)

    def test_health_endpoint(self):
        """Test GET /health verifies model readiness."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertTrue(data.get("model_loaded"))

    def test_predict_healthy_machine(self):
        """Test POST /predict with healthy machine operating data."""
        payload = {
            "air_temperature": 298.1,
            "process_temperature": 308.6,
            "rotational_speed": 1551.0,
            "torque": 42.8,
            "tool_wear": 0.0,
            "machine_type": "M",
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["prediction"], "No Machine Failure")
        self.assertFalse(data["failure_predicted"])
        self.assertLess(data["failure_probability"], 0.30)
        self.assertEqual(data["risk_level"], "LOW")

        # Verify mathematical feature engineering
        calc = data["calculated_features"]
        self.assertAlmostEqual(calc["temperature_difference"], 10.5, places=2)
        self.assertAlmostEqual(calc["power"], 42.8 * 1551.0, places=1)
        self.assertAlmostEqual(calc["wear_torque_product"], 0.0, places=1)

    def test_predict_high_risk_machine(self):
        """Test POST /predict with high-stress failure data."""
        payload = {
            "air_temperature": 298.9,
            "process_temperature": 309.1,
            "rotational_speed": 1412.0,
            "torque": 65.0,
            "tool_wear": 215.0,
            "machine_type": "L",
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["prediction"], "Machine Failure")
        self.assertTrue(data["failure_predicted"])
        self.assertGreaterEqual(data["failure_probability"], 0.60)
        self.assertEqual(data["risk_level"], "HIGH")

    def test_predict_invalid_inputs(self):
        """Test validation reject on invalid machine inputs."""
        # 1. Invalid machine type
        bad_type = {
            "air_temperature": 298.1,
            "process_temperature": 308.6,
            "rotational_speed": 1551.0,
            "torque": 42.8,
            "tool_wear": 0.0,
            "machine_type": "INVALID",
        }
        resp = self.client.post("/predict", json=bad_type)
        self.assertEqual(resp.status_code, 422)

        # 2. Temperature out of bounds
        bad_temp = {
            "air_temperature": 500.0,
            "process_temperature": 308.6,
            "rotational_speed": 1551.0,
            "torque": 42.8,
            "tool_wear": 0.0,
            "machine_type": "M",
        }
        resp = self.client.post("/predict", json=bad_temp)
        self.assertEqual(resp.status_code, 422)

        # 3. Negative torque
        bad_torque = {
            "air_temperature": 298.1,
            "process_temperature": 308.6,
            "rotational_speed": 1551.0,
            "torque": -10.0,
            "tool_wear": 0.0,
            "machine_type": "M",
        }
        resp = self.client.post("/predict", json=bad_torque)
        self.assertEqual(resp.status_code, 422)

    def test_response_structure_completeness(self):
        """Verify all required response fields and sub-objects exist."""
        payload = {
            "air_temperature": 300.0,
            "process_temperature": 310.0,
            "rotational_speed": 1500.0,
            "torque": 40.0,
            "tool_wear": 50.0,
            "machine_type": "H",
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check top-level keys
        for key in [
            "prediction",
            "failure_predicted",
            "failure_probability",
            "risk_level",
            "sensor_overview",
            "calculated_features",
            "potential_contributing_factors",
            "ai_analysis",
        ]:
            self.assertIn(key, data)

        # Check AI analysis sub-structure
        ai = data["ai_analysis"]
        for key in [
            "summary",
            "why_this_prediction",
            "potential_contributing_factors",
            "maintenance_recommendation",
            "operational_advice",
            "is_fallback",
        ]:
            self.assertIn(key, ai)


if __name__ == "__main__":
    unittest.main()
