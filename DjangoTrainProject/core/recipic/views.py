import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Recipe
import io
import os
import numpy as np
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the class names
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

# Define a confidence threshold
CONFIDENCE_THRESHOLD = 0.5  # Adjust this as needed

# Function to load the model
def load_model():
    try:
        model_path = os.path.join(os.getcwd(), 'ml_model', 'Filipino_Food_ResNet50_Final.h5')
        logger.info(f"Attempting to load model from: {model_path}")
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            return None
        
        # Load the model
        model = tf.keras.models.load_model(model_path)
        logger.info("Model loaded successfully.")
        return model
    
    except Exception as e:
        logger.error(f"Failed to load the model. Error: {str(e)}")
        return None

# Load the model at startup
model = load_model()

# Preprocessing function for images
def preprocess_image(image):
    try:
        # Resize and preprocess the image
        image = image.resize((224, 224))  # Match model input size
        image_array = img_to_array(image)
        image_array = preprocess_input(np.expand_dims(image_array, axis=0))  # Normalize using ResNet preprocessing
        return image_array
    except Exception as e:
        logger.error(f"Error during image preprocessing: {str(e)}")
        raise e

# Django view for rendering the index page
def index(request):
    return render(request, 'user/food_camera.html')

# Django API endpoint for classifying images
@csrf_exempt
def classify_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    if model is None:
        logger.error("Model not loaded. Check server logs for details.")
        return JsonResponse({'error': 'Model not loaded. Check server logs for details.'}, status=500)

    try:
        # Get the image file from the request
        image_file = request.FILES.get('image')
        if not image_file:
            logger.error("No image file received in the request.")
            return JsonResponse({'error': 'No image file received.'}, status=400)

        # Process the image
        try:
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            processed_image = preprocess_image(image)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return JsonResponse({'error': 'Image preprocessing failed.'}, status=500)

        # Make predictions
        try:
            predictions = model.predict(processed_image)
            predicted_class_index = np.argmax(predictions[0])  # Get index of the highest probability
            confidence = float(predictions[0][predicted_class_index])  # Confidence score

            # Check confidence threshold for food classification
            if confidence < CONFIDENCE_THRESHOLD:
                logger.warning("Prediction confidence is too low to classify as food.")
                return JsonResponse({'error': 'Invalid food. That is not a food.'}, status=400)

            class_name = CLASS_NAMES[predicted_class_index]  # Map index to class name

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return JsonResponse({'error': 'Prediction failed.'}, status=500)

        # Fetch recipe from database
        recipe = Recipe.objects.filter(title__icontains=class_name).first()
        
        # Prepare the response
        response_data = {
            'class_name': class_name.replace('_', ' ').title(),  # Format the class name
            'confidence': round(confidence, 2)  # Round confidence for better readability
        }

        if recipe:
            response_data['recipe'] = {
                'title': recipe.title,
                'description': recipe.description,
                'cooking_time': recipe.cooking_time,
                'instructions': [instruction.description for instruction in recipe.instructions.all()]
            }
        else:
            response_data['recipe'] = None

        # Return the response as JSON
        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Unhandled exception in classify_image: {traceback.format_exc()}")
        return JsonResponse({'error': 'Internal server error.'}, status=500)

# API endpoint to get recipe by food name
def get_recipe_by_food(request):
    food_name = request.GET.get('food_name', '')
    try:
        recipe = Recipe.objects.filter(title__icontains=food_name).first()
        if recipe:
            return JsonResponse({
                'success': True,
                'recipe': {
                    'title': recipe.title,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'instructions': [instruction.description for instruction in recipe.instructions.all()]
                }
            })
        else:
            return JsonResponse({'success': False, 'message': 'Recipe not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})




# Django API endpoint to check the model's status
def check_model_status(request):
    if model is None:
        logger.error("Model not loaded. Check server logs for details.")
        return JsonResponse({'status': 'error', 'message': 'Model not loaded. Check server logs for details.'})
    return JsonResponse({'status': 'success', 'message': 'Model loaded successfully'})






#ADMIN
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Recipe, Instruction
from .forms import RecipeForm, InstructionFormSet

def admin_dashboard(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'admin/dashboard.html', {'recipes': recipes})

def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        instruction_formset = InstructionFormSet(request.POST)
        if form.is_valid() and instruction_formset.is_valid():
            recipe = form.save()
            instructions = instruction_formset.save(commit=False)
            for instruction in instructions:
                instruction.recipe = recipe
                instruction.save()
            return redirect('admin_dashboard')
    else:
        form = RecipeForm()
        instruction_formset = InstructionFormSet()
    return render(request, 'admin/recipe_form.html', {'form': form, 'instruction_formset': instruction_formset})

def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        instruction_formset = InstructionFormSet(request.POST, instance=recipe)
        if form.is_valid() and instruction_formset.is_valid():
            form.save()
            instruction_formset.save()
            return redirect('admin_dashboard')
    else:
        form = RecipeForm(instance=recipe)
        instruction_formset = InstructionFormSet(instance=recipe)
    return render(request, 'admin/recipe_form.html', {'form': form, 'instruction_formset': instruction_formset, 'recipe': recipe})

def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        return redirect('admin_dashboard')
    return render(request, 'admin/recipe_confirm_delete.html', {'recipe': recipe})




#Login Register
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from django.contrib import messages
from .forms import UserLoginForm
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode  
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.contrib.auth.models import User  



def home(request):
    return render(request, 'home.html')

def user_dashboard(request):
    return render(request, 'user/food_camera.html')

# def admin_dashboard(request):
#     return render(request, 'admin/dashboard.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Deactivate account until email is confirmed
            user.save()

            # Create confirmation link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = request.build_absolute_uri(
                reverse('confirm_email', kwargs={'uidb64': uid, 'token': token})
            )

            # Prepare email
            subject = 'Activate Your Account'
            message = render_to_string('activation_email.html', {
                'user': user,
                'confirmation_link': confirmation_link,
            })
            send_mail(subject, message, 'noreply@yourdomain.com', [form.cleaned_data['email']])  # Change sender email

            return render(request, 'registration_success.html')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64)) 
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user account
        user.save()
        login(request, user)  # Log the user in
        return render(request, 'email_confirmed.html')
    else:
        return render(request, 'home.html', {'show_invalid_link_modal': True})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    # messages.success(request, "Logged in successfully.")

                    # Redirect based on user type
                    if user.is_superuser or user.is_staff:
                        return redirect(reverse('admin_dashboard'))
                    else:
                        return redirect(reverse('user_dashboard'))
                else:
                    messages.error(request, "Your account is not active. Please check your email to activate your account.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})
