# Imports needed
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import tensorflow as tf
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

img_height = 224  # VGG16 requires input size of (224, 224)
img_width = 224
batch_size = 16  # Adjust batch size as needed

# Load VGG16 model with pre-trained weights and without the top classification layers
base_model = VGG16(
    weights="imagenet",
    include_top=False,
    input_shape=(img_height, img_width, 3),  # VGG16 expects RGB images
)

# Freeze the pre-trained layers
for layer in base_model.layers:
    layer.trainable = False

# Add custom classification layers on top of VGG16
model = models.Sequential([
    base_model,
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(2, activation='softmax')  # 2 classes: 'rusak' and 'sehat'
])

# Print model summary to check the architecture
model.summary()

# Define data generators
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=5,
    horizontal_flip=False,
    vertical_flip=False,
    data_format="channels_last",
    validation_split=0.1,
)

train_generator = datagen.flow_from_directory(
    "data/kubis/",
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode="categorical",  # Use categorical mode for multiple classes
    subset="training",
    seed=123,
)

validation_generator = datagen.flow_from_directory(
    "data/kubis/",
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation",
    seed=123,
)

# Compile the model
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Train the model
model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator,
    verbose=2
)

# Save the trained model
model.save("vgg16_model.h5")
