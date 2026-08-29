from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ─── Feature Engineering ───────────────────────────────────────────────────────

WEATHER_RISK_MAP = {
    'HURRICANE': 0.95, 'TYPHOON': 0.92, 'BLIZZARD': 0.88,
    'STORM': 0.75,     'HEAVY_RAIN': 0.65, 'FLOOD': 0.80,
    'FOG': 0.45,       'SNOW': 0.50,       'ICE': 0.55,
    'RAIN': 0.35,      'CLOUDY': 0.20,
    'CLEAR': 0.05,     'SUNNY': 0.05,      'UNKNOWN': 0.30
}

GEO_RISK_REGIONS = {
    'UKRAINE': 0.85, 'RUSSIA': 0.80, 'SUDAN': 0.75, 'MYANMAR': 0.70,
    'SYRIA': 0.90,   'IRAN': 0.75,   'NORTH KOREA': 0.95,
    'CHINA': 0.40,   'INDIA': 0.20,  'US': 0.10, 'GERMANY': 0.08,
    'BRAZIL': 0.30,  'MEXICO': 0.35, 'EGYPT': 0.40, 'TURKEY': 0.45
}

CARRIER_RELIABILITY = {
    'FEDEX': 0.92, 'DHL': 0.90, 'UPS': 0.91, 'MAERSK': 0.88,
    'MSC': 0.85,   'COSCO': 0.75, 'EVERGREEN': 0.80,
    'LOCAL_CARRIER': 0.55, 'UNKNOWN': 0.40
}

# ─── Model (trained on synthetic data) ─────────────────────────────────────────

class RiskModel:
    def __init__(self):
        self.weather_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.geo_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.supplier_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.risk_classifier = RandomForestClassifier(n_estimators=200, random_state=42)
        self.is_trained = False

    def generate_training_data(self, n=2000):
        np.random.seed(42)
        weather_base = np.random.uniform(0, 1, n)
        geo_base = np.random.uniform(0, 1, n)
        supplier_base = np.random.uniform(0, 1, n)
        delay_days = np.random.randint(0, 30, n)
        cargo_value = np.random.uniform(1000, 1000000, n)
        temperature = np.random.uniform(-20, 50, n)

        # Weather risk model features
        X_weather = np.column_stack([weather_base, temperature, delay_days])
        y_weather = np.clip(weather_base + (delay_days / 100) + (np.abs(temperature - 20) / 200), 0, 1)

        # Geo risk model features
        X_geo = np.column_stack([geo_base, delay_days, cargo_value / 1e6])
        y_geo = np.clip(geo_base + (delay_days / 150), 0, 1)

        # Supplier risk model features
        X_supplier = np.column_stack([supplier_base, delay_days, cargo_value / 1e6])
        y_supplier = np.clip(supplier_base + (delay_days / 80), 0, 1)

        overall = 0.3 * y_weather + 0.3 * y_geo + 0.4 * y_supplier
        labels = np.digitize(overall, [0.25, 0.50, 0.75]) # 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL

        X_clf = np.column_stack([y_weather, y_geo, y_supplier, delay_days, cargo_value / 1e6])

        return X_weather, y_weather, X_geo, y_geo, X_supplier, y_supplier, X_clf, labels

    def train(self):
        logger.info("Training risk models...")
        X_w, y_w, X_g, y_g, X_s, y_s, X_clf, labels = self.generate_training_data()
        self.weather_model.fit(X_w, y_w)
        self.geo_model.fit(X_g, y_g)
        self.supplier_model.fit(X_s, y_s)
        self.risk_classifier.fit(X_clf, labels)
        self.is_trained = True
        logger.info("Models trained successfully.")

    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            self.train()

        weather_condition = str(features.get('weather_condition', 'UNKNOWN')).upper()
        weather_base = WEATHER_RISK_MAP.get(weather_condition, 0.30)

        origin = str(features.get('origin', '')).upper()
        destination = str(features.get('destination', '')).upper()
        geo_base = max(
            next((v for k, v in GEO_RISK_REGIONS.items() if k in origin), 0.20),
            next((v for k, v in GEO_RISK_REGIONS.items() if k in destination), 0.20)
        )

        carrier = str(features.get('carrier', 'UNKNOWN')).upper()
        carrier_reliability = next((v for k, v in CARRIER_RELIABILITY.items() if k in carrier), 0.50)
        supplier_base = 1.0 - carrier_reliability

        delay_days = float(features.get('delay_days', 0))
        cargo_value = float(features.get('cargo_value', 10000))
        temperature = float(features.get('temperature', 20))

        X_weather = np.array([[weather_base, temperature, delay_days]])
        X_geo = np.array([[geo_base, delay_days, cargo_value / 1e6]])
        X_supplier = np.array([[supplier_base, delay_days, cargo_value / 1e6]])

        weather_risk = float(np.clip(self.weather_model.predict(X_weather)[0], 0, 1))
        geo_risk = float(np.clip(self.geo_model.predict(X_geo)[0], 0, 1))
        supplier_risk = float(np.clip(self.supplier_model.predict(X_supplier)[0], 0, 1))
        overall_risk = round(0.3 * weather_risk + 0.3 * geo_risk + 0.4 * supplier_risk, 4)

        X_clf = np.array([[weather_risk, geo_risk, supplier_risk, delay_days, cargo_value / 1e6]])
        risk_class = int(self.risk_classifier.predict(X_clf)[0])
        risk_labels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        risk_level = risk_labels[min(risk_class, 3)]

        return {
            'weather_risk_score': round(weather_risk, 4),
            'geopolitical_risk_score': round(geo_risk, 4),
            'supplier_risk_score': round(supplier_risk, 4),
            'overall_risk_score': overall_risk,
            'risk_level': risk_level,
            'confidence': round(float(max(self.risk_classifier.predict_proba(X_clf)[0])), 4)
        }


model = RiskModel()
model.train()

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_trained': model.is_trained})


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        result = model.predict(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Prediction error: {e}") 
        return jsonify({'error': str(e)}), 500


@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'error': 'Expected a list of shipments'}), 400
        results = [model.predict(item) for item in data]
        return jsonify(results)
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/retrain', methods=['POST'])
def retrain():
    try:
        model.train()
        return jsonify({'message': 'Model retrained successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
