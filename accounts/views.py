from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.is_superuser:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Redirect based on user type
            if user.is_superuser:
                return redirect('accounts:admin_dashboard')
            return redirect('accounts:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address=address,
            city=city,
            postal_code=postal_code
        )
        
        login(request, user)
        messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
        
        # Redirect based on user type
        if user.is_superuser:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:home')
    
    return render(request, 'accounts/register.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def admin_dashboard_view(request):
    # Check if user is superuser
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'user': request.user,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'recent_users': recent_users,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)