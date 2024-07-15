from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

# Initialize the Flask app
app = Flask(__name__)

# Define the CNN model
def create_model():
    model = Sequential([
        Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(28, 28, 1)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model = create_model()

# Endpoint to train the model
@app.route('/train', methods=['POST'])
def train():
    data = request.json
    if 'images' not in data or 'labels' not in data:
        return jsonify({'error': 'No training data provided'}), 400

    images = np.array(data['images']).astype(np.float32) / 255.0
    labels = to_categorical(np.array(data['labels']), num_classes=10)
    
    images = images.reshape(-1, 28, 28, 1)

    model.fit(images, labels, epochs=1, batch_size=128, validation_split=0.2)
    return jsonify({'status': 'Model trained successfully'})

# Endpoint to make predictions
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    image = np.array(data['image']).astype(np.float32) / 255.0
    image = image.reshape(1, 28, 28, 1)
    
    prediction = model.predict(image)
    predicted_class = np.argmax(prediction, axis=1)[0]
    
    return jsonify({'prediction': int(predicted_class)})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
