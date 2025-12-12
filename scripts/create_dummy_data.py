import os
import numpy as np
from PIL import Image


def create_dummy_data(base_dir, num_classes=3, images_per_class=5):
    """Creates dummy images for testing the training pipeline."""
    breeds = [f"breed_{i}" for i in range(num_classes)]

    for split in ["train", "val"]:
        for breed in breeds:
            path = os.path.join(base_dir, split, breed)
            os.makedirs(path, exist_ok=True)

            for i in range(images_per_class):
                # Create a random RGB image
                img_data = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
                img = Image.fromarray(img_data)
                img.save(os.path.join(path, f"img_{i}.jpg"))

    print(f"Created dummy dataset in {base_dir}")


if __name__ == "__main__":
    create_dummy_data("dataset")
