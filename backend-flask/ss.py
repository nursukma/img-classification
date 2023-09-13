import os
from sklearn.model_selection import train_test_split
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, BatchNormalization

train_data_dir = 'data/kubis'
test_data_dir = 'data/kubis'

# Load the dataset from your own folders
x_train = []
y_train = []
x_test = []
y_test = []

# Load training data
for class_label in os.listdir(train_data_dir):
    class_dir = os.path.join(train_data_dir, class_label)
    if os.path.isdir(class_dir):
        for image_file in os.listdir(class_dir):
            if image_file.endswith('.jpg'):  # Filter image files
                img = tf.keras.preprocessing.image.load_img(
                    os.path.join(class_dir, image_file),
                    target_size=(32, 32)  # Set your desired image size
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                x_train.append(img_array)
                # Assuming class folders are named with class labels
                y_train.append(int(class_label))

# Load test data
for class_label in os.listdir(test_data_dir):
    class_dir = os.path.join(test_data_dir, class_label)
    if os.path.isdir(class_dir):
        for image_file in os.listdir(class_dir):
            if image_file.endswith('.jpg'):  # Filter image files
                img = tf.keras.preprocessing.image.load_img(
                    os.path.join(class_dir, image_file),
                    target_size=(32, 32)  # Set your desired image size
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                x_test.append(img_array)
                # Assuming class folders are named with class labels
                y_test.append(int(class_label))

# Convert lists to numpy arrays
x_train = np.array(x_train)
y_train = np.array(y_train)
x_test = np.array(x_test)
y_test = np.array(y_test)


def normalize(x):
    x = x.astype('float32')
    x = x/255.0
    return x


datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
)

x_test, x_val, y_test, y_val = train_test_split(
    x_test, y_test, test_size=0.5, random_state=0)

x_train = normalize(x_train)
x_test = normalize(x_test)
x_val = normalize(x_val)

y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)
y_val = tf.keras.utils.to_categorical(y_val, 10)

datagen.fit(x_train)


def results(model):
    epoch = 100
    r = model.fit(datagen.flow(x_train, y_train, batch_size=4), epochs=epoch,
                  steps_per_epoch=len(x_train)/4, validation_data=(x_val, y_val), verbose=1)
    acc = model.evaluate(x_test, y_test)
    print("test set loss : ", acc[0])
    print("test set accuracy :", acc[1]*100)

    epoch_range = range(1, epoch+1)
    plt.plot(epoch_range, r.history['accuracy'])
    plt.plot(epoch_range, r.history['val_accuracy'])
    plt.title('Classification Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Val'], loc='lower right')
    plt.show()

    # Plot training & validation loss values
    plt.plot(epoch_range, r.history['loss'])
    plt.plot(epoch_range, r.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Val'], loc='lower right')
    plt.show()


weight_decay = 1e-4
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', padding='same',
           kernel_regularizer=tf.keras.regularizers.l2(weight_decay), input_shape=(32, 32, 3)),
    BatchNormalization(),
    Conv2D(32, (3, 3), activation='relu', kernel_regularizer=tf.keras.regularizers.l2(
        weight_decay), padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.2),
    Conv2D(64, (3, 3), activation='relu', kernel_regularizer=tf.keras.regularizers.l2(
        weight_decay), padding='same'),
    BatchNormalization(),
    Conv2D(64, (3, 3), activation='relu', kernel_regularizer=tf.keras.regularizers.l2(
        weight_decay), padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.3),
    Conv2D(128, (3, 3), activation='relu', kernel_regularizer=tf.keras.regularizers.l2(
        weight_decay), padding='same'),
    BatchNormalization(),
    Conv2D(128, (3, 3), activation='relu', kernel_regularizer=tf.keras.regularizers.l2(
        weight_decay), padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.3),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])

opt = tf.keras.optimizers.SGD(lr=0.001, momentum=0.9)
model.compile(optimizer=opt, loss='categorical_crossentropy',
              metrics=['accuracy'])
