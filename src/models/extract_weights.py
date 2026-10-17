"""
Extract initializers from ONNX models into a unified NumPy weights artifact
for universal zero-dependency inference across IBM LinuxONE (s390x) and x86_64.
"""
import onnx
from onnx import numpy_helper
import joblib
from pathlib import Path
from src.config import ARTIFACTS_DIR

def extract_onnx_weights():
    weights = {}
    
    models = {
        "health": ARTIFACTS_DIR / "model1_health.onnx",
        "delays": ARTIFACTS_DIR / "model2_delays.onnx",
        "stock": ARTIFACTS_DIR / "model3_stock.onnx"
    }
    
    for name, path in models.items():
        if not path.exists():
            print(f"Skipping {name}: {path} not found")
            continue
        m = onnx.load(str(path))
        weights[name] = {init.name: numpy_helper.to_array(init) for init in m.graph.initializer}
        print(f"Extracted {len(weights[name])} weight tensors for {name}")
        
    out_path = ARTIFACTS_DIR / "model_weights_numpy.joblib"
    joblib.dump(weights, out_path)
    print(f"Saved universal NumPy weights artifact to: {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    extract_onnx_weights()
