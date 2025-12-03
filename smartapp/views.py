from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
import uuid
from .models import Order, OrderItem, FoodItem, Feedback, DiscountVoucher
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
    return render(request, 'order.html')

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
            sentiment_result = SentimentAnalyzer.analyze_sentiment(feedback_text)
            
            # Create feedback entry with sentiment
            feedback_entry = Feedback.objects.create(
                customer_name=customer_name,
                category=feedback_category,
                rating=int(rating),
                feedback_text=feedback_text,
                sentiment=sentiment_result['sentiment'],
                confidence=sentiment_result['confidence']
            )
            
            logger.info(f"Feedback created: {feedback_entry} with sentiment: {sentiment_result['sentiment']}")
            
            # Handle sentiment-based responses
            response_data = {
                'message': 'Feedback submitted successfully',
                'customer': customer_name,
                'sentiment': sentiment_result['sentiment']
            }
            
            # If sentiment is negative, create discount voucher and add special message
            if sentiment_result['sentiment'] == 'negative':
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
                # Positive or Neutral sentiment
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
            
            logger.info(f"Received order: name={name}, ordered_by={ordered_by}, table={table}, cart={cart}")
            
            if not name or not table or not cart:
                logger.error("Invalid data received: missing name, table, or cart")
                return JsonResponse({'error': 'Invalid data'}, status=400)
            
            # Calculate total amount and estimated wait time
            total_amount = 0
            item_count = 0
            for item in cart:
                quantity = item.get('qty', 1)
                price = item.get('price', 0)
                total_amount += quantity * price
                item_count += quantity
            
            # Calculate estimated wait time (15-25 minutes base + 2 minutes per item)
            estimated_wait = 15 + (item_count * 2)
            if estimated_wait > 45:
                estimated_wait = 45  # Cap at 45 minutes
            
            # Create the main order
            # Set food_item to a summary of items, e.g., first item or comma-separated
            food_item_summary = ', '.join([f"{item['name']} x{item['qty']}" for item in cart[:3]])  # First 3 items
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
                quantity = item.get('qty', 1)
                unit_price = item.get('price', 0)
                category = item.get('category', 'General')
                
                OrderItem.objects.create(
                    order=order,
                    item_name=item_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    category=category
                )
            
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
            sentiment_result = SentimentAnalyzer.analyze_sentiment(feedback_text)

            # Create feedback entry
            feedback_entry = Feedback.objects.create(
                customer_name=customer_name,
                category=category,
                rating=int(rating),
                feedback_text=feedback_text,
                sentiment=sentiment_result['sentiment'],
                confidence=sentiment_result['confidence']
            )
            
            # Handle negative sentiment - create discount voucher
            if sentiment_result['sentiment'] == 'negative':
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
