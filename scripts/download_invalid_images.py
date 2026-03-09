"""
Helper script to download random images for the 'invalid' class.
This script downloads random images from the internet to populate the invalid class folders.

You can also manually add your own images to:
- dataset/train/invalid/
- dataset/val/invalid/

The images should be random objects, animals (non-cows), landscapes, people, etc.
"""

import os
import urllib.request
import ssl

# Create SSL context to avoid certificate verification issues
ssl._create_default_https_context = ssl._create_unverified_context

def download_sample_images():
    """
    Downloads sample images from publicly available sources.
    These are just examples - you should add your own diverse invalid images.
    """
    
    # Sample URLs for random images (these are placeholder examples)
    # In practice, you would use a dataset like CIFAR-10, ImageNet samples, or your own images
    sample_urls = [
        # You can add URLs to random images here
        # For example: cars, dogs, cats, landscapes, buildings, etc.
    ]
    
    train_dir = "dataset/train/invalid"
    val_dir = "dataset/val/invalid"
    
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    
    print("=" * 60)
    print("MANUAL DATASET PREPARATION REQUIRED")
    print("=" * 60)
    print("\nThis script is a template. To use the 'invalid' class feature:")
    print("\n1. Add 50-100 random images to: dataset/train/invalid/")
    print("   - Images of cars, dogs, cats, people, landscapes, etc.")
    print("   - Anything that is NOT a cow")
    print("\n2. Add 10-20 random images to: dataset/val/invalid/")
    print("   - Similar variety as training set")
    print("\n3. Make sure images are in common formats (jpg, png, etc.)")
    print("\nSuggested sources for random images:")
    print("  - Google Images (search for random objects)")
    print("  - Unsplash.com (free stock photos)")
    print("  - Pexels.com (free stock photos)")
    print("  - Your own photos")
    print("\nAfter adding images, run: python scripts/train_model.py")
    print("=" * 60)

if __name__ == "__main__":
    download_sample_images()
