import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image
import os

# Define class names (update this list with your actual class labels)
CLASS_NAMES = [
    'afritada', 'arroz_caldo', 'bagnet', 'balut', 'bibingka', 
    'bicol_express', 'bistek_tagalog', 'buco_pie', 'bulalo', 
    'cassava_cake', 'champorado', 'chicharon', 'chicken_adobo',
    'chicken_bistek', 'chicken_inasal', 'crispy_pata', 
    'filipino_spaghetti', 'ginataang_gulay', 'halo-halo',
    'kaldereta', 'kare-kare', 'kilawin', 'kinilaw', 'laing', 
    'leche_flan', 'lechon', 'lechon_kawali', 'liempo', 
    'longganisa', 'lumpia', 'pancit_guisado', 'pancit_palabok',
    'pandesal', 'pinakbet', 'pork_adobo', 'pork_barbecue',
    'pork_sisig', 'sinigang', 'taho', 'tapa', 'tinola', 
    'tocino', 'turon', 'ube_ice_cream', 'ube_milkshake'
]

# Load the trained model
model_path = r"C:\Users\kimry\OneDrive\Desktop\DjangoTrainProject\core\ml_model\Filipino_Food_ResNet50_Final.h5"
if not os.path.exists(model_path):
    print(f"Model file not found: {model_path}")
else:
    print(f"Loading model from: {model_path}")
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully.")

# Load and preprocess a test image
image_path = r"C:\Users\kimry\OneDrive\Desktop\DjangoTrainProject\core\ml_model\sample_image\halo.jpeg"
if not os.path.exists(image_path):
    print(f"Image file not found: {image_path}")
else:
    print(f"Processing image: {image_path}")
    # Open and preprocess the image
    image = Image.open(image_path).convert('RGB')
    image = image.resize((224, 224))  # Resize to match model input size
    image_array = img_to_array(image)
    image_array = preprocess_input(np.expand_dims(image_array, axis=0))  # Apply same preprocessing as training

    # Make a prediction
    predictions = model.predict(image_array)
    predicted_class_index = np.argmax(predictions[0])  # Get index of the highest confidence
    confidence = float(predictions[0][predicted_class_index])  # Confidence score of the prediction

    # Retrieve class name
    class_name = CLASS_NAMES[predicted_class_index]

    # Print results
    print(f"Predicted class index: {predicted_class_index}")
    print(f"Predicted class name: {class_name}")
    print(f"Confidence: {confidence:.2f}")
