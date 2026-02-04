from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
import json
import uuid
from .models import Order, OrderItem, FoodItem, Feedback, DiscountVoucher, Admin, KDS, AllergyInfo
from .sentiment_analysis import SentimentAnalyzer
import logging

# Configure logging for debugging
logger = logging.getLogger(__name__)

def home(request):
    logger.info(f"Home view accessed via URL: {request.path}")
    return render(request, 'home.html')

def menus(request):
    return render(request, 'menus.html')

def order(request):
    food_items = FoodItem.objects.all()
    categories = FoodItem.objects.values_list('category', flat=True).distinct()
    return render(request, 'order.html', {'food_items': food_items, 'categories': categories})

def feedback_page(request):
    return render(request, 'feedback.html')

def view_feedback(request):
    """
    Display all feedback entries in a table format
    """
    feedback_list = Feedback.objects.all().order_by('-created_at')
    return render(request, 'view_feedback.html', {'feedback_list': feedback_list})

@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_name = data.get('customer_name')
            feedback_category = data.get('feedback_category')
            rating = data.get('rating')
            feedback_text = data.get('feedback_text')
            
            if not all([customer_name, feedback_category, rating, feedback_text]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            # Perform sentiment analysis
            try:
                sentiment_result = SentimentAnalyzer.analyze_sentiment(feedback_text)
                sentiment = sentiment_result['sentiment']
                confidence = sentiment_result['confidence']
                logger.info(f"Sentiment analysis result: {sentiment} ({confidence}% confidence)")
            except RuntimeError as e:
                # Model not available - log warning and continue without sentiment
                logger.warning(f"Sentiment analysis unavailable: {e}")
                sentiment = None
                confidence = None
            
            # Create feedback entry with sentiment (or without if model unavailable)
            feedback_entry = Feedback.objects.create(
                customer_name=customer_name,
                category=feedback_category,
                rating=int(rating),
                feedback_text=feedback_text,
                sentiment=sentiment,
                confidence=confidence
            )
            
            logger.info(f"Feedback created: {feedback_entry} with sentiment: {sentiment}")
            
            # Handle sentiment-based responses
            response_data = {
                'message': 'Feedback submitted successfully',
                'customer': customer_name,
                'sentiment': sentiment or 'unknown'
            }
            
            # If sentiment is negative, create discount voucher and add special message
            if sentiment == 'negative':
                # Generate unique voucher code
                voucher_code = f"SORRY{str(uuid.uuid4())[:6].upper()}"
                
                # Create discount voucher
                discount_voucher = DiscountVoucher.objects.create(
                    customer_name=customer_name,
                    feedback=feedback_entry,
                    voucher_code=voucher_code,
                    discount_percentage=10
                )
                
                response_data.update({
                    'popup_message': "We're sorry your order experience wasn't great 😞 — You've earned a 10% discount voucher for your next visit!",
                    'voucher_code': voucher_code,
                    'discount_percentage': 10
                })
                
                logger.info(f"Created discount voucher {voucher_code} for negative feedback from {customer_name}")
                
            else:
                # Positive, Neutral, or Unknown sentiment
                response_data['popup_message'] = "Thank you for your feedback 💬!"
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return JsonResponse({'error': f'Error processing feedback: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_feedback_data(request):
    """
    API endpoint to get all feedback data for display
    """
    if request.method == 'GET':
        try:
            feedback_list = Feedback.objects.all().order_by('-created_at')
            feedback_data = []

            for fb in feedback_list:
                feedback_data.append({
                    'id': fb.id,
                    'customer_name': fb.customer_name,
                    'feedback_category': fb.get_category_display(),
                    'rating': fb.rating,
                    'feedback_text': fb.feedback_text,
                    'sentiment': fb.get_sentiment_display(),
                    'created_at': fb.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return JsonResponse({'feedback': feedback_data})
            
        except Exception as e:
            logger.error(f"Error retrieving feedback data: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def contact(request):
    return render(request, 'contact.html')

def order_history(request):
    """
    Display all order history entries in a table format
    """
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@csrf_exempt
def submit_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            ordered_by = data.get('ordered_by', name)  # Use name if ordered_by not provided
            table = data.get('table')
            cart = data.get('cart', [])
            allergy = data.get('allergy', '').strip()
            
            logger.info(f"Received order: name={name}, ordered_by={ordered_by}, table={table}, cart={cart}")
            
            if not name or not table or not cart:
                logger.error("Invalid data received: missing name, table, or cart")
                return JsonResponse({'error': 'Invalid data'}, status=400)
            
            # Calculate total amount and estimated wait time
            total_amount = 0
            item_count = 0
            for item in cart:
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                total_amount += quantity * price
                item_count += quantity
            
            # Calculate estimated wait time (15-25 minutes base + 2 minutes per item)
            estimated_wait = 15 + (item_count * 2)
            if estimated_wait > 45:
                estimated_wait = 45  # Cap at 45 minutes
            
            # Create the main order
            # Set food_item to a summary of items, e.g., first item or comma-separated
            food_item_summary = ', '.join([f"{item['name']} x{item['quantity']}" for item in cart[:3]])  # First 3 items
            if len(cart) > 3:
                food_item_summary += f" +{len(cart)-3} more"
            order = Order.objects.create(
                table_number=int(table),
                customer_name=name,
                food_item=food_item_summary,
                ordered_by=ordered_by,
                total_amount=total_amount,
                estimated_wait_time=estimated_wait,
                status='pending'
            )
            
            # Create individual order items
            for item in cart:
                item_name = item.get('name')
                quantity = item.get('quantity', 1)
                unit_price = item.get('price', 0)
                category = item.get('category', 'General')

                OrderItem.objects.create(
                    order=order,
                    item_name=item_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    category=category
                )
            
            # Save allergy info if provided
            if allergy:
                AllergyInfo.objects.create(order=order, allergy_type=allergy)

            logger.info(f"Order created: {order} with {len(cart)} items")

            return JsonResponse({
                'message': 'Order placed successfully',
                'order_id': order.id,
                'customer': name,
                'ordered_by': ordered_by,
                'table': table,
                'total_amount': float(total_amount),
                'estimated_wait_time': estimated_wait,
                'items_count': len(cart)
            })
            
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return JsonResponse({'error': f'Error processing order: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# New views for simple forms
def order_form(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        table_number = request.POST.get('table_number')
        food_item = request.POST.get('food_item')
        
        if customer_name and table_number and food_item:
            Order.objects.create(
                customer_name=customer_name,
                table_number=int(table_number),
                food_item=food_item
            )
            return redirect('order_success')
    
    return render(request, 'order_form.html')

def feedback_form(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        category = request.POST.get('category')
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text')

        if customer_name and category and rating and feedback_text:
            # Perform sentiment analysis
            try:
                sentiment_result = SentimentAnalyzer.analyze_sentiment(feedback_text)
                sentiment = sentiment_result['sentiment']
                confidence = sentiment_result['confidence']
                logger.info(f"Sentiment analysis result: {sentiment} ({confidence}% confidence)")
            except RuntimeError as e:
                # Model not available - log warning and continue without sentiment
                logger.warning(f"Sentiment analysis unavailable: {e}")
                sentiment = None
                confidence = None

            # Create feedback entry
            feedback_entry = Feedback.objects.create(
                customer_name=customer_name,
                category=category,
                rating=int(rating),
                feedback_text=feedback_text,
                sentiment=sentiment,
                confidence=confidence
            )
            
            # Handle negative sentiment - create discount voucher
            if sentiment == 'negative':
                voucher_code = f"SORRY{str(uuid.uuid4())[:6].upper()}"
                DiscountVoucher.objects.create(
                    customer_name=customer_name,
                    feedback=feedback_entry,
                    voucher_code=voucher_code,
                    discount_percentage=10
                )
                # Store voucher info in session for display on success page
                request.session['voucher_code'] = voucher_code
                request.session['is_negative_feedback'] = True
            else:
                request.session['is_negative_feedback'] = False
            
            return redirect('feedback_success')

    return render(request, 'feedback_form.html')

def order_success(request):
    return render(request, 'order_success.html')

def feedback_success(request):
    # Render the template with session data
    response = render(request, 'feedback_success.html')

    # Clear session data after rendering
    if 'voucher_code' in request.session:
        del request.session['voucher_code']
    if 'is_negative_feedback' in request.session:
        del request.session['is_negative_feedback']

    return response


def admin_login(request):
    """
    Admin login view - standalone page with centered login form.
    Uses Django's built-in authentication system.
    
    IMPORTANT: Always shows the login page, even if already authenticated.
    This allows users to logout and login as a different admin.
    """
    # Always show the login page - don't auto-redirect to dashboard
    # User can login or logout from here
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Use Django's authenticate() function
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is staff/admin
            if user.is_staff:
                # Django's login() creates session and handles CSRF
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                # Redirect to dashboard after successful login
                next_page = request.GET.get('next')
                return redirect(next_page if next_page else 'admin_dashboard')
            else:
                messages.error(request, 'Access denied. Staff credentials required.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Render standalone login template (no sidebar, centered form)
    # Pass user info to show logout option if already authenticated
    context = {
        'user': request.user if request.user.is_authenticated else None
    }
    return render(request, 'admin_login_standalone.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    now = timezone.now()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    ready_orders = Order.objects.filter(status='ready').count()

    # Delayed orders: pending and time exceeded
    delayed_orders = 0
    for order in Order.objects.filter(status='pending'):
        elapsed = (now - order.order_time).total_seconds() / 60  # minutes
        if elapsed > order.estimated_wait_time:
            delayed_orders += 1

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delayed_orders': delayed_orders,
        'ready_orders': ready_orders,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_orders(request):
    orders = Order.objects.all().order_by('-order_time')
    now = timezone.now()
    orders_with_pending = []
    for order in orders:
        elapsed = (now - order.order_time).total_seconds() / 60
        is_delayed = elapsed > order.estimated_wait_time and order.status == 'pending'
        orders_with_pending.append({
            'order': order,
            'pending_time': int(elapsed),
            'is_delayed': is_delayed,
        })
    return render(request, 'admin_orders.html', {'orders_with_pending': orders_with_pending})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    allergies = order.allergies.all()
    now = timezone.now()
    elapsed = (now - order.order_time).total_seconds() / 60
    pending_time = int(elapsed)
    is_delayed = elapsed > order.estimated_wait_time and order.status == 'pending'

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send_to_kitchen':
            order.status = 'preparing'
            order.save()
            KDS.objects.get_or_create(order=order, defaults={'kitchen_status': 'Preparing'})
        elif action == 'mark_completed':
            order.status = 'completed'
            order.save()
            kds, created = KDS.objects.get_or_create(order=order)
            kds.kitchen_status = 'Ready'
            kds.ready_time = timezone.now()
            kds.save()
        return redirect('admin_order_detail', order_id=order_id)

    return render(request, 'admin_order_detail.html', {
        'order': order,
        'items': items,
        'allergies': allergies,
        'pending_time': pending_time,
        'is_delayed': is_delayed,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_kds(request):
    kds_orders = KDS.objects.select_related('order').all()
    now = timezone.now()
    kds_with_time = []
    for kds in kds_orders:
        elapsed = (now - kds.order.order_time).total_seconds() / 60
        is_delayed = elapsed > kds.order.estimated_wait_time
        kds_with_time.append({
            'kds': kds,
            'elapsed_time': int(elapsed),
            'is_delayed': is_delayed,
        })

    # Sort: delayed first, then by order time ascending
    kds_with_time.sort(key=lambda x: (not x['is_delayed'], x['kds'].order.order_time))

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = get_object_or_404(Order, id=order_id)
        kds, created = KDS.objects.get_or_create(order=order)
        if action == 'start_cooking':
            kds.kitchen_status = 'Preparing'
            kds.start_time = timezone.now()
            kds.save()
        elif action == 'mark_ready':
            kds.kitchen_status = 'Ready'
            kds.ready_time = timezone.now()
            kds.save()
            order.status = 'ready'
            order.save()
        return redirect('admin_kds')

    return render(request, 'admin_kds.html', {'kds_with_time': kds_with_time})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_feedback(request):
    feedbacks = Feedback.objects.select_related('order').all().order_by('-created_at')
    positive_count = feedbacks.filter(sentiment='positive').count()
    negative_count = feedbacks.filter(sentiment='negative').count()
    neutral_count = feedbacks.filter(sentiment='neutral').count()

    emotion_counts = feedbacks.values('emotion').annotate(count=Count('emotion')).order_by('-count')

    return render(request, 'admin_feedback.html', {
        'feedbacks': feedbacks,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'emotion_counts': emotion_counts,
    })


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'admin_id' not in request.session:
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper
