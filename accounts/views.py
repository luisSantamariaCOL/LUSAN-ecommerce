from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem

def register(request):
    # Handle user registration
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Extract validated data from form
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            # Generate a username from the email address
            username = email.split('@')[0]

            # Create a new user account
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Send account activation email
            current_site = get_current_site(request)
            email_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            # Send the email
            to_email = email
            send_email = EmailMessage(email_subject, message, to=[to_email])
            send_email.send()

            # Redirect to login page after registration
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        # Display empty registration form for GET request
        form = RegistrationForm()

    context = {
        'form' : form,
    }

    # Render the registration template
    return render(request, 'accounts/register.html', context)

def login(request):
    # Handle user login
    if request.method == 'POST':
        # Process login form data if POST request
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate the user
        user = auth.authenticate(email=email, password=password)

        # Log the user in and redirect to dashboard
        if user.is_authenticated:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            # Show error message if credentials are invalid
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    # Handle user logout
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    # Handle account activation
    try:
        # Decode the uid and get the user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activate the user account if the token is valid
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is now activated.')
        return redirect('login')
    else:
        # Show error message if the activation link is invalid
        messages.error(request, 'Invalid activation link')
        return redirect('register')

@login_required(login_url = 'login')
def dashboard(request):
    # Render the dashboard page for logged-in users
    return render(request, 'accounts/dashboard.html')
    
def forgot_password(request):
    # Handle password reset requests
    if request.method == 'POST':
        # Process the form data if POST request
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            # Check if the account exists
            user = Account.objects.get(email__exact=email) # exact: case sensitive

            # Send password reset email
            current_site = get_current_site(request)
            email_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(email_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
    
    return render(request, 'accounts/forgot_password.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid') 
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset succesful')
            return redirect('login')
        
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    
    else:
        return render(request, 'accounts/reset_password.html')