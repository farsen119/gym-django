from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from product.models import Product

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get or create cart for user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # If item already exists, increase quantity
        cart_item.quantity += 1
        cart_item.save()
        message = f'Updated {product.name} quantity in cart'
    else:
        message = f'{product.name} added to cart'
    
    # Check if this is an AJAX request
    if request.headers.get('Content-Type') == 'application/json' or request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
    
    # For non-AJAX requests, redirect to cart page
    messages.success(request, message)
    return redirect('cart:view_cart')

@login_required
def view_cart(request):
    """View cart contents"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().order_by('-added_at')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'cart/view_cart.html', context)

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, f'{cart_item.product.name} removed from cart')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'{cart_item.product.name} quantity updated')
    
    return redirect('cart:view_cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'{product_name} removed from cart')
    return redirect('cart:view_cart')

@login_required
def clear_cart(request):
    """Clear all items from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    
    messages.success(request, 'Cart cleared successfully')
    return redirect('cart:view_cart')

@login_required
def cart_count(request):
    """Get cart item count for AJAX requests"""
    try:
        cart = Cart.objects.get(user=request.user)
        count = cart.total_items
    except Cart.DoesNotExist:
        count = 0
    
    return JsonResponse({'count': count})
