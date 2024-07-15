import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import numpy as np

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')

    def fit(self, X, y=None):
        X_filled = self.imputer.fit_transform(X)
        self.scaler.fit(X_filled)
        return self

    def transform(self, X, y=None):
        X_filled = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_filled)
        return X_scaled

    def fit_transform(self, X, y=None):
        X_filled = self.imputer.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X_filled)
        return X_scaled