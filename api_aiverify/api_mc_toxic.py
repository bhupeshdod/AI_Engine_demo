from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the multi-class classification logistic regression model
with open('sample_mc_toxic_sklearn_linear.LogisticRegression.sav', 'rb') as model_file:
    model = pickle.load(model_file)

# Define the expected columns based on your dataset
expected_columns = ['age', 'gender', 'race', 'ban_count', 'prior_count', 'toxic_words']

@app.route('/')
def home():
    return "Multi-class Classification Model API"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Convert input data to DataFrame
        features = pd.DataFrame([data], columns=expected_columns)
        
        # Perform prediction
        prediction = model.predict(features)
        prediction_proba = model.predict_proba(features)
        
        # Prepare the response
        response = {
            "prediction": int(prediction[0]),
            "probability": prediction_proba[0].tolist()
        }
        return jsonify(response)
    except KeyError:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
