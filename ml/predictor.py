import os
import numpy as np
import torch
from ml.lstm_model import LSTMModel
from ml.preprocessor import Preprocessor


# we use this class to make predictions on new data coming from collectors
class Predictor:
    def __init__(self):
        self.model = LSTMModel()
        self.preprocessor = Preprocessor()
        self.model_path = os.path.join("ml", "saved_models", "lstm.pt")
        self._is_ready = False

    def load(self):
        # we check if a trained model exists, before trying to load it:
        if not os.path.exists(self.model_path):
            print("[Predictor] no trained model found, train first")
            return False
        self.model.load(self.model_path)
        self._is_ready = True
        return True

    def predict_next(self, recent_values: list) -> dict:
        # we can't predict if the model hasn't been loaded yet
        if not self._is_ready:
            return {"error": "model not ready, train first"}
        try:
            # we prepare the last N values and run them through the model
            X = self.preprocessor.prepare_for_prediction(recent_values)
            X_tensor = torch.FloatTensor(X)
            # we switch to eval. mode, so that dropout doesn't affect predictions
            self.model.eval()
            with torch.no_grad():
                output = self.model(X_tensor)
            # convert the normalized output back into a real value
            predicted_scaled = output.numpy().reshape(-1, 1)
            predicted_value = self.preprocessor.inverse_transform(predicted_scaled)

            return {
                "predicted_value": round(float(predicted_value[0][0]), 4),
                "based_on_points": len(recent_values),
                "status": "ok",
            }
        except Exception as e:
            return {"error": str(e)}

    def predict_next_n(self, recent_values: list, steps: int = 10) -> list:
        # we predict some steps into the future by feeding each prediction back as input
        if not self._is_ready:
            return []
        predictions = []
        current_sequence = list(recent_values)
        for step in range(steps):
            result = self.predict_next(current_sequence)
            if "error" in result:
                break
            predicted = result["predicted_value"]
            predictions.append({
                "step": step + 1,
                "predicted_value": predicted,
            })
            # we append the prediction to the sequence, so the next step uses it:
            current_sequence.append(predicted)
        return predictions