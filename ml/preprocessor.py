import numpy as np
from sklearn.preprocessing import MinMaxScaler


class Preprocessor:
	# we basically take the raw data and turn it into a format the model can use
    # handling normalization, data cleaning
    def __init__(self, sequence_length: int = 20):
        # how many past data points the LSTM looks at to make a prediction
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self._is_fitted = False

    def fit_transform(self, values: list) -> np.ndarray:
        # fit the scaler on the data and transform it
        # this function is meant to be called when training the model for the first time
        data = np.array(values).reshape(-1, 1)
        scaled = self.scaler.fit_transform(data)
        self._is_fitted = True
        return scaled
    
	# the function for the moment we need to make predictions on new data:
    def transform(self, values: list) -> np.ndarray:
        # after we fit the scaler, we neet to transform the data
        if not self._is_fitted:
            raise ValueError("Scaler not fitted yet - call fit_transform first")
        data = np.array(values).reshape(-1, 1)
        return self.scaler.transform(data)

    def inverse_transform(self, values: np.ndarray) -> np.ndarray:
        # converting the normalized predictions back to real values:
        return self.scaler.inverse_transform(values)

    def create_sequences(self, scaled_data: np.ndarray):
        # we turn a flat array of values into sequences for the LSTM
        # ex.: [1,2,3,4,5] with sequence_length = 3 becomes:
    	# X = [[1,2,3], [2,3,4]]
        # y = [4, 5]
        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i:i + self.sequence_length])
            y.append(scaled_data[i + self.sequence_length])
        return np.array(X), np.array(y)

    def prepare_for_prediction(self, recent_values: list) -> np.ndarray:
        # we take the last N values and prepare them for a single prediction
        # this is the function we call when new data comes in:
        if len(recent_values) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} values, got {len(recent_values)}")
        # we only take the last sequence_length values
        last_sequence = recent_values[-self.sequence_length:]
        scaled = self.transform(last_sequence)
        # reshaping to (1, sequence_length, 1): what pytorch expects
        return scaled.reshape(1, self.sequence_length, 1)