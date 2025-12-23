from django.db import models
from django.contrib.auth.models import User  # Django's built-in user
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100, default='General')

    def __str__(self):
        return self.name



class Order(models.Model):
    table_number = models.IntegerField()
    customer_name = models.CharField(max_length=100)
    food_item = models.CharField(max_length=200, default='Unknown Item')
    ordered_by = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_wait_time = models.IntegerField(default=15)  # in minutes
    status = models.CharField(max_length=20, default='pending')
    order_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - Table {self.table_number} - {self.customer_name}"

    def get_items(self):
        return ', '.join([f"{item.item_name} x{item.quantity}" for item in self.items.all()])
    get_items.short_description = 'Items'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100, default='General')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.item_name} (Order #{self.order.id})"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Service", "Service"),
        ("Cleanliness", "Cleanliness"),
        ("Ambience", "Ambience"),
    ]

    SENTIMENT_CHOICES = [
        ("positive", "Positive"),
        ("negative", "Negative"),
        ("neutral", "Neutral"),
    ]

    customer_name = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Food')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    feedback_text = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    emotion = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.customer_name} - {self.category}"


class DiscountVoucher(models.Model):
    """
    Model to track discount vouchers given for negative feedback
    """
    customer_name = models.CharField(max_length=100)
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='vouchers')
    voucher_code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.IntegerField(default=10)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Discount Voucher"
        verbose_name_plural = "Discount Vouchers"
    
    def __str__(self):
        return f"Voucher {self.voucher_code} for {self.customer_name} ({self.discount_percentage}% off)"


class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # hashed
    role = models.CharField(max_length=50, default='admin')
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.email})"


class KDS(models.Model):
    STATUS_CHOICES = [
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='kds')
    kitchen_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Preparing')
    start_time = models.DateTimeField(null=True, blank=True)
    ready_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"KDS for Order #{self.order.id} - {self.kitchen_status}"


class AllergyInfo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='allergies')
    allergy_type = models.CharField(max_length=100)  # e.g., Nuts, Dairy
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Allergy: {self.allergy_type} for Order #{self.order.id}"
