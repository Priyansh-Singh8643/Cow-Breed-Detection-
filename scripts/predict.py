import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import argparse
import os
import json

MODEL_PATH = "models/cow_breed_model.keras"
CLASS_INDICES_PATH = "models/class_indices.json"


def load_class_indices():
    """Load class indices from JSON file."""
    if not os.path.exists(CLASS_INDICES_PATH):
        print(f"Class indices file not found at {CLASS_INDICES_PATH}.")
        print("Using default class mapping...")
        # Fallback to default mapping
        return {
            'breed_0': 0, 
            'breed_1': 1, 
            'breed_2': 2,
            'invalid': 3
        }
    
    with open(CLASS_INDICES_PATH, 'r') as f:
        class_indices = json.load(f)
    return class_indices


def get_display_names():
    """Get human-readable display names for each class."""
    return {
        0: 'Ayrshire cattle',
        1: 'Brown Swiss cattle',
        2: 'Holstein Friesian cattle',
        3: 'Invalid/Not a Cow'
    }


def predict_breed(img_path, class_indices=None):
    """Predicts the breed of a cow from an image."""
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Please train the model first.")
        return None, None

    if class_indices is None:
        class_indices = load_class_indices()

    model = tf.keras.models.load_model(MODEL_PATH)

    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)
    confidence = np.max(predictions)

    # Get display names
    display_names = get_display_names()
    predicted_label = display_names.get(predicted_class_index, "Unknown")

    print(f"Predicted: {predicted_label} (Confidence: {confidence:.2%})")
    
    # Show all class probabilities
    print("\nAll class probabilities:")
    labels = {v: k for k, v in class_indices.items()}
    for idx in range(len(predictions[0])):
        class_name = display_names.get(idx, labels.get(idx, f"Class {idx}"))
        prob = predictions[0][idx]
        print(f"  {class_name}: {prob:.2%}")
        
    return predicted_label, confidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict cow breed from image")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    args = parser.parse_args()
    
    predict_breed(args.image_path)

