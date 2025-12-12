import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
DATASET_DIR = "dataset"
MODEL_SAVE_PATH = "models/cow_breed_model.keras"


def build_model(num_classes):
    base_model = MobileNetV2(
        weights="imagenet", include_top=False, input_shape=IMG_SIZE + (3,)
    )
    base_model.trainable = False  # Freeze base model

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.2)(x)
    predictions = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    return model


def train():
    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print(
            "Dataset directories not found. Please create 'dataset/train' and 'dataset/val'."
        )
        return

    # Data Generators
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_generator = train_datagen.flow_from_directory(
        train_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode="categorical"
    )

    val_generator = val_datagen.flow_from_directory(
        val_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode="categorical"
    )

    if train_generator.num_classes == 0:
        print("No classes found in training data.")
        return

    model = build_model(train_generator.num_classes)

    # Callbacks
    checkpoint = ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor="val_accuracy",
        verbose=1,
        save_best_only=True,
        mode="max",
    )
    early_stop = EarlyStopping(monitor="val_loss", patience=3, verbose=1)

    print(f"Starting training for {train_generator.num_classes} classes...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=[checkpoint, early_stop],
    )

    print("Training finished.")


if __name__ == "__main__":
    train()
