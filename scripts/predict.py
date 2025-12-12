import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import argparse
import os

MODEL_PATH = "models/cow_breed_model.keras"


def predict_breed(img_path, class_indices):
    """Predicts the breed of a cow from an image."""
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Please train the model first.")
        return

    model = tf.keras.models.load_model(MODEL_PATH)

    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)

    # Invert class_indices dictionary to get label from index
    labels = {v: k for k, v in class_indices.items()}
    predicted_label = labels[predicted_class_index]
    confidence = np.max(predictions)

    print(f"Predicted Breed: {predicted_label} (Confidence: {confidence:.2f})")
    return predicted_label, confidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict cow breed from image")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    args = parser.parse_args()

    # NOTE: You need to know the class indices from training.
    # For now, we will assume a dummy mapping if not provided or load from a file if we had saved it.
    # In a real scenario, save class_indices.npy during training.
    # Here is an example assuming the dummy data classes:
    # Updated mapping with real names
    dummy_class_indices = {'Ayrshire cattle': 0, 'Brown Swiss cattle': 1, 'Holstein Friesian cattle': 2} 
    
    predict_breed(args.image_path, dummy_class_indices)
