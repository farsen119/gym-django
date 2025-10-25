from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem
from cart.models import Cart, CartItem

@login_required
def checkout_view(request):
    """Checkout page - create order from cart"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:view_cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:view_cart')
    
    if request.method == 'POST':
        # Create order from cart
        order = create_order_from_cart(request, cart)
        if order:
            # Clear cart after successful order creation
            cart.items.all().delete()
            messages.success(request, f'Order {order.order_number} created successfully!')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Failed to create order. Please try again.')
    
    # Calculate totals
    subtotal = cart.total_price
    shipping_cost = Decimal('0.00')  # Free shipping
    tax_amount = subtotal * Decimal('0.08')  # 8% tax
    total_amount = subtotal + shipping_cost + tax_amount
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
    }
    
    return render(request, 'orders/checkout.html', context)

def create_order_from_cart(request, cart):
    """Create order from cart items"""
    try:
        # Get user information
        user = request.user
        
        # Create order
        order = Order.objects.create(
            user=user,
            subtotal=cart.total_price,
            shipping_cost=Decimal('0.00'),
            tax_amount=cart.total_price * Decimal('0.08'),
            total_amount=cart.total_price + (cart.total_price * Decimal('0.08')),
            shipping_address=user.address or 'Not provided',
            shipping_city=user.city or 'Not provided',
            shipping_postal_code=user.postal_code or 'Not provided',
            contact_email=user.email,
            contact_phone=user.phone_number or '',
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        return order
    except Exception as e:
        print(f"Error creating order: {e}")
        return None

@login_required
def order_detail_view(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_history_view(request):
    """View user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_history.html', context)

@login_required
def process_payment_view(request, order_id):
    """Process payment for order (dummy payment)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return JsonResponse({'success': False, 'message': 'Order already paid'})
    
    # Simulate payment processing
    order.payment_status = 'paid'
    order.status = 'processing'
    order.paid_at = timezone.now()
    order.save()
    
    return JsonResponse({
        'success': True, 
        'message': 'Payment successful!',
        'order_number': order.order_number
    })

@login_required
def payment_success_view(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/payment_success.html', context)

@login_required
def admin_orders_view(request):
    """Admin view to manage all orders"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:home')
    
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter orders by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter orders by payment status if requested
    payment_filter = request.GET.get('payment_status')
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)
    
    context = {
        'orders': orders,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
        'current_status': status_filter,
        'current_payment_status': payment_filter,
    }
    
    return render(request, 'orders/admin_orders.html', context)

@login_required
def update_order_status_view(request, order_id):
    """Update order status (admin only)"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_payment_status = request.POST.get('payment_status')
        
        if new_status and new_status in [choice[0] for choice in Order.ORDER_STATUS_CHOICES]:
            order.status = new_status
            order.save()
            return JsonResponse({
                'success': True, 
                'message': f'Order status updated to {order.get_status_display()}'
            })
        
        if new_payment_status and new_payment_status in [choice[0] for choice in Order.PAYMENT_STATUS_CHOICES]:
            order.payment_status = new_payment_status
            order.save()
            return JsonResponse({
                'success': True, 
                'message': f'Payment status updated to {order.get_payment_status_display()}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def cancel_order_view(request, order_id):
    """Allow customers to cancel their own orders"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order can be cancelled
        if order.status in ['shipped', 'delivered']:
            return JsonResponse({
                'success': False, 
                'message': 'Cannot cancel order that has already been shipped or delivered'
            })
        
        if order.status == 'cancelled':
            return JsonResponse({
                'success': False, 
                'message': 'Order is already cancelled'
            })
        
        # Cancel the order
        order.status = 'cancelled'
        order.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Order cancelled successfully'
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Order not found or you do not have permission to cancel this order'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'An error occurred: {str(e)}'
        })
