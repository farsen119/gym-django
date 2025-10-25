from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

def home_view(request):
    # Get products for display on home page
    try:
        from product.models import Product, Category
        featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
        recent_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        categories = Category.objects.all()[:6]
    except ImportError:
        featured_products = []
        recent_products = []
        categories = []
    
    context = {
        'featured_products': featured_products,
        'recent_products': recent_products,
        'categories': categories,
    }
    
    return render(request, 'home.html', context)

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
    
    # Get product statistics
    try:
        from product.models import Product, Category, Brand, ProductImage
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        total_brands = Brand.objects.count()
        total_images = ProductImage.objects.count()
        recent_products = Product.objects.select_related('category', 'brand').order_by('-created_at')[:5]
    except ImportError:
        total_products = 0
        active_products = 0
        total_categories = 0
        total_brands = 0
        total_images = 0
        recent_products = []
    
    # Get order statistics
    try:
        from orders.models import Order, OrderItem
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        paid_orders = Order.objects.filter(payment_status='paid').count()
        pending_payments = Order.objects.filter(payment_status='pending').count()
        
        # Calculate total revenue
        total_revenue = sum(order.total_amount for order in Order.objects.filter(payment_status='paid'))
        
        # Recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
        
        # Orders by status
        orders_by_status = {
            'pending': Order.objects.filter(status='pending').count(),
            'processing': Order.objects.filter(status='processing').count(),
            'shipped': Order.objects.filter(status='shipped').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
        }
        
    except ImportError:
        total_orders = 0
        pending_orders = 0
        processing_orders = 0
        shipped_orders = 0
        delivered_orders = 0
        paid_orders = 0
        pending_payments = 0
        total_revenue = 0
        recent_orders = []
        orders_by_status = {}
    
    context = {
        'user': request.user,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'recent_users': recent_users,
        'total_products': total_products,
        'active_products': active_products,
        'total_categories': total_categories,
        'total_brands': total_brands,
        'total_images': total_images,
        'recent_products': recent_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'paid_orders': paid_orders,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def reports_view(request):
    """Admin reports and analytics view"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    # Get order statistics
    try:
        from orders.models import Order, OrderItem
        from product.models import Product, Category, Brand
        from django.db.models import Count, Sum, Avg
        from datetime import datetime, timedelta
        
        # Basic statistics
        total_orders = Order.objects.count()
        total_revenue = sum(order.total_amount for order in Order.objects.filter(payment_status='paid'))
        total_customers = User.objects.filter(is_staff=False).count()
        total_products = Product.objects.count()
        
        # Recent orders (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago)
        recent_revenue = sum(order.total_amount for order in recent_orders.filter(payment_status='paid'))
        
        # Orders by status
        orders_by_status = {
            'pending': Order.objects.filter(status='pending').count(),
            'processing': Order.objects.filter(status='processing').count(),
            'shipped': Order.objects.filter(status='shipped').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
        }
        
        # Payment status breakdown
        payment_status = {
            'paid': Order.objects.filter(payment_status='paid').count(),
            'pending': Order.objects.filter(payment_status='pending').count(),
            'failed': Order.objects.filter(payment_status='failed').count(),
            'refunded': Order.objects.filter(payment_status='refunded').count(),
        }
        
        # Top selling products (by quantity ordered)
        top_products = OrderItem.objects.values('product__name', 'product__category__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_quantity')[:10]
        
        # Orders by month (last 6 months)
        monthly_orders = []
        monthly_revenue = []
        for i in range(6):
            month_start = datetime.now() - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            month_orders = Order.objects.filter(created_at__gte=month_start, created_at__lt=month_end)
            monthly_orders.append(month_orders.count())
            monthly_revenue.append(sum(order.total_amount for order in month_orders.filter(payment_status='paid')))
        
        # Category performance
        category_stats = OrderItem.objects.values('product__category__name').annotate(
            total_orders=Count('order'),
            total_revenue=Sum('price')
        ).order_by('-total_revenue')[:5]
        
        # Average order value
        avg_order_value = Order.objects.filter(payment_status='paid').aggregate(
            avg_value=Avg('total_amount')
        )['avg_value'] or 0
        
    except ImportError:
        total_orders = 0
        total_revenue = 0
        total_customers = 0
        total_products = 0
        recent_revenue = 0
        orders_by_status = {}
        payment_status = {}
        top_products = []
        monthly_orders = []
        monthly_revenue = []
        category_stats = []
        avg_order_value = 0
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'total_products': total_products,
        'recent_revenue': recent_revenue,
        'orders_by_status': orders_by_status,
        'payment_status': payment_status,
        'top_products': top_products,
        'monthly_orders': monthly_orders,
        'monthly_revenue': monthly_revenue,
        'category_stats': category_stats,
        'avg_order_value': avg_order_value,
    }
    
    return render(request, 'accounts/reports.html', context)