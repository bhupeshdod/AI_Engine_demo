from flask import Flask, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

# Load the binary classification logistic regression model
with open('sample_bc_credit_sklearn_linear.LogisticRegression.sav', 'rb') as model_file:
    model = pickle.load(model_file)

# Define the expected columns based on your dataset
expected_columns = ['age', 'gender', 'income', 'race', 'home_ownership', 'prior_count', 'loan_amount', 'loan_interests']

@app.route('/')
def home():
    return "Binary Classification Model API"

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
        
        # Prepare the response
        response = {
            "prediction": int(prediction[0])
        }
        return jsonify(response)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)