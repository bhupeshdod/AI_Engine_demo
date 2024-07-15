import numpy as np
import pandas as pd

class ImagePreprocessor:
    def __init__(self):
        pass

    def transform(self, X):
        X_ = X.copy()
        images = []
        for i in range(len(X_)):
            image_array = X_.iloc[i].values.reshape(28, 28, 1) / 255.0
            images.append(image_array)
        return np.array(images)

    def fit(self, X, y=None):
        return self