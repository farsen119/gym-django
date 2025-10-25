from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Brand, ProductImage

@login_required
def product_list_view(request):
    """List all products - Admin view"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
    }
    
    return render(request, 'product/product_list.html', context)

def customer_product_list_view(request):
    """List all products - Customer view with filtering"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Apply filters
    category_filter = request.GET.get('category')
    brand_filter = request.GET.get('brand')
    search_query = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Filter by category
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Filter by brand
    if brand_filter:
        products = products.filter(brand_id=brand_filter)
    
    # Search filter (only if search_query is not None, not empty, and not the string "None")
    if search_query and search_query.strip() and search_query != 'None':
        products = products.filter(name__icontains=search_query)
    
    # Price range filter
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sort products
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_category': category_filter,
        'current_brand': brand_filter,
        'current_search': search_query,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_sort': sort_by,
    }
    
    return render(request, 'product/customer_product_list.html', context)

def product_detail_view(request, product_id):
    """Show individual product details"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'product/product_detail.html', context)

@login_required
def add_product_view(request):
    """Add new product"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        stock_quantity = request.POST.get('stock_quantity')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        if name and description and price and category_id and brand_id:
            try:
                category = Category.objects.get(id=category_id)
                brand = Brand.objects.get(id=brand_id)
                
                product = Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    brand=brand,
                    stock_quantity=stock_quantity or 0,
                    is_featured=is_featured,
                    is_active=is_active,
                    created_by=request.user
                )
                
                # Handle image uploads
                images = request.FILES.getlist('images')
                if images:
                    for i, image in enumerate(images):
                        ProductImage.objects.create(
                            product=product,
                            image=image,
                            is_primary=(i == 0)  # First image is primary
                        )
                
                messages.success(request, f'Product "{product.name}" added successfully!')
                return redirect('product:admin_product_list')
            except (Category.DoesNotExist, Brand.DoesNotExist):
                messages.error(request, 'Invalid category or brand selected.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'categories': categories,
        'brands': brands,
    }
    
    return render(request, 'product/add_product.html', context)

@login_required
def edit_product_view(request, product_id):
    """Edit existing product"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        product.stock_quantity = request.POST.get('stock_quantity') or 0
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_active = request.POST.get('is_active') == 'on'
        
        if product.name and product.description and product.price and category_id and brand_id:
            try:
                product.category = Category.objects.get(id=category_id)
                product.brand = Brand.objects.get(id=brand_id)
                product.save()
                
                # Handle new image uploads
                images = request.FILES.getlist('images')
                if images:
                    # Check if product already has a primary image
                    has_primary = product.images.filter(is_primary=True).exists()
                    
                    for i, image in enumerate(images):
                        # Set first image as primary if no primary exists
                        is_primary = (i == 0 and not has_primary)
                        ProductImage.objects.create(
                            product=product,
                            image=image,
                            is_primary=is_primary
                        )
                
                messages.success(request, f'Product "{product.name}" updated successfully!')
                return redirect('product:admin_product_list')
            except (Category.DoesNotExist, Brand.DoesNotExist):
                messages.error(request, 'Invalid category or brand selected.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
    }
    
    return render(request, 'product/edit_product.html', context)

@login_required
def delete_product_view(request, product_id):
    """Delete product"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('product:product_list')
    
    return render(request, 'product/delete_product.html', {'product': product})

@login_required
def add_category_view(request):
    """Add new category"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            category = Category.objects.create(
                name=name,
                description=description or ''
            )
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('product:admin_product_list')
        else:
            messages.error(request, 'Category name is required.')
    
    return render(request, 'product/add_category.html')

@login_required
def add_brand_view(request):
    """Add new brand"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            brand = Brand.objects.create(
                name=name,
                description=description or ''
            )
            messages.success(request, f'Brand "{brand.name}" added successfully!')
            return redirect('product:admin_product_list')
        else:
            messages.error(request, 'Brand name is required.')
    
    return render(request, 'product/add_brand.html')

@login_required
def manage_product_images_view(request, product_id):
    """Manage product images"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Handle image uploads
        images = request.FILES.getlist('images')
        if images:
            # Check if product already has a primary image
            has_primary = product.images.filter(is_primary=True).exists()
            
            for i, image in enumerate(images):
                # Set first image as primary if no primary exists
                is_primary = (i == 0 and not has_primary)
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=is_primary
                )
            
            messages.success(request, f'{len(images)} image(s) uploaded successfully!')
        else:
            messages.warning(request, 'No images were selected for upload.')
        return redirect('product:manage_images', product_id=product.id)
    
    # Auto-fix: If no primary image exists but images do exist, set the first one as primary
    all_images = product.images.all()
    if all_images.exists() and not product.images.filter(is_primary=True).exists():
        first_image = all_images.first()
        first_image.is_primary = True
        first_image.save()
    
    context = {
        'product': product,
        'images': product.images.all()
    }
    
    return render(request, 'product/manage_images.html', context)

@login_required
def delete_image_view(request, image_id):
    """Delete product image"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('product:manage_images', product_id=product_id)
    
    return render(request, 'product/delete_image.html', {'image': image})

@login_required
def set_primary_image_view(request, image_id):
    """Set image as primary"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    image = get_object_or_404(ProductImage, id=image_id)
    
    # Remove primary from all other images of this product
    ProductImage.objects.filter(product=image.product).update(is_primary=False)
    
    # Set this image as primary
    image.is_primary = True
    image.save()
    
    messages.success(request, 'Primary image updated successfully!')
    return redirect('product:manage_images', product_id=image.product.id)