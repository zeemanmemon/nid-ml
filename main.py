from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

app = FastAPI(title="Network Intrusion Detection API")

model = joblib.load("ids_model.pkl")
scaler = joblib.load("scaler.pkl")

# MITRE ATT&CK mapping
mitre_map = {
    "DoS":    {"id": "T1498", "name": "Network Denial of Service"},
    "Probe":  {"id": "T1046", "name": "Network Service Discovery"},
    "R2L":    {"id": "T1078", "name": "Valid Accounts (Remote Access)"},
    "U2R":    {"id": "T1068", "name": "Exploitation for Privilege Escalation"},
    "Normal": None
}

class Connection(BaseModel):
    features: list[float]  # 41 values

@app.get("/")
def root():
    return {"status": "NID API is running"}

@app.post("/predict")
def predict(conn: Connection):
    if len(conn.features) != 41:
        return {"error": f"Expected 41 features, got {len(conn.features)}"}

    x = np.array(conn.features).reshape(1, -1)
    x_scaled = scaler.transform(x)

    prediction = model.predict(x_scaled)[0]
    confidence = round(model.predict_proba(x_scaled).max(), 4)
    mitre = mitre_map.get(prediction)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "mitre": mitre
    }