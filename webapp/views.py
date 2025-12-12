from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationForm, ImageUploadForm
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from django.conf import settings

# Load model once at startup (efficient)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'cow_breed_model.keras')
try:
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        # Dummy class indices - in real app, load these from a file generated during training
        CLASS_INDICES = {'breed_0': 0, 'breed_1': 1, 'breed_2': 2}
        # Map indices to human readable names
        DISPLAY_NAMES = {
            0: 'Ayrshire cattle',
            1: 'Brown Swiss cattle',
            2: 'Holstein Friesian cattle'
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

@login_required
def index_view(request):
    prediction = None
    confidence = None
    uploaded_image_url = None

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
                    prediction = DISPLAY_NAMES.get(pred_index, "Unknown Breed")
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
        'uploaded_image_url': uploaded_image_url
    })

# Custom Admin Check
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser, login_url='/login/') # Enforce session check
def custom_admin_view(request):
    user_count = User.objects.count()
    # In a real app, you could add PredictionHistory model and count that too
    context = {
        'user_count': user_count,
        'users': User.objects.all()
    }
    return render(request, 'custom_admin.html', context)
