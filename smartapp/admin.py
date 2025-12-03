from django.contrib import admin
from .models import Order, OrderItem, FoodItem, Feedback, DiscountVoucher
from django.utils.html import format_html
from django.db import models
from django.utils import timezone

# Inline for OrderItem in Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('item_name', 'category', 'quantity', 'unit_price', 'total_price', 'notes')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    list_filter = ['category']
    search_fields = ['name']
    ordering = ['category', 'name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'table_number', 'food_item', 'get_items', 'total_amount', 'status', 'order_time']
    list_filter = ['order_time', 'table_number', 'status']
    search_fields = ['customer_name', 'table_number', 'food_item']
    ordering = ['-order_time']
    readonly_fields = ['order_time']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item_name', 'category', 'quantity', 'unit_price', 'total_price']
    list_filter = ['category', 'created_at']
    search_fields = ['item_name', 'order__customer_name', 'order__table_number']
    readonly_fields = ('total_price',)
    ordering = ['-created_at']



@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'category', 'rating', 'feedback_text', 'sentiment', 'confidence', 'created_at']
    list_filter = ['category', 'rating', 'sentiment', 'created_at']
    search_fields = ['customer_name', 'feedback_text']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(DiscountVoucher)
class DiscountVoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_code', 'customer_name', 'discount_percentage', 'is_used', 'created_at', 'used_at']
    list_filter = ['is_used', 'discount_percentage', 'created_at']
    search_fields = ['customer_name', 'voucher_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'voucher_code']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['feedback', 'customer_name', 'discount_percentage']
        return self.readonly_fields
