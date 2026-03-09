import os

dataset_dir = "dataset/train"
classes = os.listdir(dataset_dir)

print("Current Dataset Distribution:")
print("-" * 40)
for class_name in sorted(classes):
    class_path = os.path.join(dataset_dir, class_name)
    if os.path.isdir(class_path):
        num_images = len([f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        print(f"{class_name}: {num_images} images")
