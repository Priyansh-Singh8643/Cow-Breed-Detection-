from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationForm, ImageUploadForm, CowBreedForm
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from django.conf import settings
import json

# Load model once at startup (efficient)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'cow_breed_model.keras')
CLASS_INDICES_PATH = os.path.join(settings.BASE_DIR, 'models', 'class_indices.json')

try:
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        
        # Load class indices from JSON file
        if os.path.exists(CLASS_INDICES_PATH):
            with open(CLASS_INDICES_PATH, 'r') as f:
                CLASS_INDICES = json.load(f)
            print(f"Loaded class indices: {CLASS_INDICES}")
            # Invert dictionary to map index -> class name
            DISPLAY_NAMES = {v: k for k, v in CLASS_INDICES.items()}
        else:
            # Fallback to default mapping
            print("Using default class indices (class_indices.json not found)")
            DISPLAY_NAMES = {
                0: 'Ayrshire cattle',
                1: 'Brown Swiss cattle',
                2: 'Holstein Friesian cattle',
                3: 'Invalid/Not a Cow'
            }
    else:
        model = None
        print("Model file not found.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Log the user in directly after registration (Session created)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user) # Creates the session
                messages.info(request, f"You are now logged in as {username}.")
                # Redirect to 'next' if it exists
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request) # Clears the session
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

def index_view(request):
    prediction = None
    confidence = None
    uploaded_image_url = None

    breed_details = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img_file = request.FILES['image']
            
            # Save temporarily
            upload_dir = os.path.join(settings.BASE_DIR, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            img_path = os.path.join(upload_dir, img_file.name)
            
            with open(img_path, 'wb+') as destination:
                for chunk in img_file.chunks():
                    destination.write(chunk)
            
            uploaded_image_url = f"/static/uploads/{img_file.name}"

            if model:
                try:
                    # Preprocess and Predict
                    img = image.load_img(img_path, target_size=(224, 224))
                    img_array = image.img_to_array(img)
                    img_array = np.expand_dims(img_array, axis=0)
                    img_array /= 255.0
                    
                    preds = model.predict(img_array)
                    pred_index = np.argmax(preds)
                    confidence = float(np.max(preds)) * 100
                    
                    # Get the predicted class name
                    prediction = DISPLAY_NAMES.get(pred_index, "Unknown Breed")
                    
                    # Fetch Breed Details
                    from .models import CowBreed
                    breed_details = CowBreed.objects.filter(breed_name__iexact=prediction).first()
                    if not breed_details:
                        # try case insensitive contains
                        breed_details = CowBreed.objects.filter(breed_name__icontains=prediction).first()
                    
                    # Save to History if logged in
                    if request.user.is_authenticated:
                        from .models import SearchHistory
                        SearchHistory.objects.create(
                            user=request.user,
                            image=img_file,
                            predicted_breed=prediction
                        )
                except Exception as e:
                    print(f"Prediction Error: {e}")
                    messages.error(request, "Error processing image.")
            else:
                messages.warning(request, "Model not loaded. Cannot predict.")

    else:
        form = ImageUploadForm()

    return render(request, 'index.html', {
        'form': form,
        'prediction': prediction,
        'confidence': f"{confidence:.2f}" if confidence else None,
        'uploaded_image_url': uploaded_image_url,
        'breed_details': breed_details
    })

# Custom Admin Check
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser, login_url='/login/')
def custom_admin_view(request):
    from .models import CowBreed
    user_count = User.objects.count()
    breeds = CowBreed.objects.all()
    context = {
        'user_count': user_count,
        'users': User.objects.all(),
        'breeds': breeds
    }
    return render(request, 'custom_admin.html', context)

@login_required
@user_passes_test(is_superuser, login_url='/login/')
def add_breed_view(request):
    import shutil
    if request.method == 'POST':
        form = CowBreedForm(request.POST, request.FILES)
        if form.is_valid():
            breed = form.save()
            
            # Save to dataset folder so it can be trained later
            if breed.image:
                breed_name_safe = breed.breed_name.strip()
                train_dir = os.path.join(settings.BASE_DIR, 'dataset', 'train', breed_name_safe)
                val_dir = os.path.join(settings.BASE_DIR, 'dataset', 'val', breed_name_safe)
                
                os.makedirs(train_dir, exist_ok=True)
                os.makedirs(val_dir, exist_ok=True)
                
                # Copy image to dataset directory
                img_path = breed.image.path
                filename = os.path.basename(img_path)
                try:
                    shutil.copy(img_path, os.path.join(train_dir, filename))
                except Exception as e:
                    print(f"Failed to copy to dataset: {e}")
            
            messages.success(request, "Breed added successfully and synced to dataset!")
            return redirect('custom_admin')
    else:
        form = CowBreedForm()
    return render(request, 'add_breed.html', {'form': form})

@login_required
@user_passes_test(is_superuser, login_url='/login/')
def edit_breed_view(request, breed_id):
    from .models import CowBreed
    breed = get_object_or_404(CowBreed, id=breed_id)
    if request.method == 'POST':
        form = CowBreedForm(request.POST, request.FILES, instance=breed)
        if form.is_valid():
            form.save()
            messages.success(request, "Breed updated successfully!")
            return redirect('custom_admin')
    else:
        form = CowBreedForm(instance=breed)
    return render(request, 'edit_breed.html', {'form': form, 'breed': breed})

@login_required
@user_passes_test(is_superuser, login_url='/login/')
def delete_breed_view(request, breed_id):
    from .models import CowBreed
    breed = get_object_or_404(CowBreed, id=breed_id)
    if request.method == 'POST':
        breed.delete()
        messages.success(request, "Breed deleted successfully!")
        return redirect('custom_admin')
    return render(request, 'delete_breed.html', {'breed': breed})

@login_required
def user_dashboard_view(request):
    from .models import SearchHistory
    history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'dashboard/user.html', {'history': history})

