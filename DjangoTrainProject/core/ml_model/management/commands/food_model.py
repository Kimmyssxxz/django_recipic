import os
import numpy as np
import pandas as pd
from PIL import Image
import tensorflow as tf

# Set the data directory
data_dir = 'ml_model/data_collection/filipino_food/'  # Root directory containing food folders
csv_dir = 'ml_model/data_collection/food_recipe/'  # Directory to save CSV files
os.makedirs(csv_dir, exist_ok=True)

# Define the target image size
img_size = (128, 128)

# Step 1: Create a label mapping based on folder names
def get_label_map(data_dir):
    classes = sorted(os.listdir(data_dir))  # Ensure that class names are sorted
    label_map = {cls_name: idx for idx, cls_name in enumerate(classes)}
    return label_map

# Step 2: Convert images to CSV files with grayscale conversion
def convert_images_to_csv(data_dir, csv_dir):
    label_map = get_label_map(data_dir)
    
    # Data storage for all images
    data = []
    labels = []
    
    for cls_name, label in label_map.items():
        cls_folder = os.path.join(data_dir, cls_name)
        
        # Process each image file in the folder
        for img_name in os.listdir(cls_folder):
            img_path = os.path.join(cls_folder, img_name)
            
            # Open, resize, and convert the image to grayscale
            with Image.open(img_path) as img:
                img = img.resize(img_size)
                img = img.convert('L')  # Convert to grayscale (L mode for 1 channel)
                img_array = np.array(img).flatten()  # Flatten the image to a 1D array
                data.append(img_array)
                labels.append(label)
    
    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(data)
    df['label'] = labels
    csv_file = os.path.join(csv_dir, 'filipino_food_data_grayscale.csv')
    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")
    return csv_file

# Step 3: Preprocess the data for training
def load_data_from_csv(csv_file):
    # Load the data from CSV file
    df = pd.read_csv(csv_file)
    labels = df['label'].values
    data = df.drop(columns=['label']).values
    data = data.reshape(-1, img_size[0], img_size[1], 1)  # Reshape for CNN with 1 channel (128x128x1)
    data = data / 255.0  # Normalize to [0, 1] range
    return data, labels

# Step 4: Convert images to CSV and load the dataset
csv_file = convert_images_to_csv(data_dir, csv_dir)
data, labels = load_data_from_csv(csv_file)

# Split the dataset into training and testing sets
train_size = int(0.8 * len(data))
train_data, train_labels = data[:train_size], labels[:train_size]
test_data, test_labels = data[train_size:], labels[train_size:]

# Step 5: Define a simple CNN model for grayscale images
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(img_size[0], img_size[1], 1)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(len(np.unique(labels)), activation='softmax')  # Number of output classes
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Step 6: Train the model
epochs = 20
history = model.fit(
    train_data, train_labels,
    validation_data=(test_data, test_labels),
    epochs=epochs
)

# Step 7: Evaluate the model on the test set
test_loss, test_acc = model.evaluate(test_data, test_labels)
print(f"Test accuracy: {test_acc:.2f}")

# Step 8: Save the model (optional)
model.save('ml_model/data_collection/trained_data/food_classification_model_grayscale.h5')
print("Model saved as 'ml_model/data_collection/trained_data/food_classification_model_grayscale.h5'")
