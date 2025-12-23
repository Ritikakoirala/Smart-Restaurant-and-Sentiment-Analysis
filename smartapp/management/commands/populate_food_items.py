from django.core.management.base import BaseCommand
from smartapp.models import FoodItem

class Command(BaseCommand):
    help = 'Populate the database with food items'

    def handle(self, *args, **options):
        # Clear existing items
        FoodItem.objects.all().delete()

        # Menu data
        menu_data = [
            # Newari Cuisine
            {'name': 'Yomari', 'price': 120, 'category': 'Newari Cuisine'},
            {'name': 'Chatamari', 'price': 150, 'category': 'Newari Cuisine'},
            {'name': 'Bara (Wo)', 'price': 100, 'category': 'Newari Cuisine'},
            {'name': 'Choila (Buff/Chicken)', 'price': 180, 'category': 'Newari Cuisine'},
            {'name': 'Samay Baji Set', 'price': 300, 'category': 'Newari Cuisine'},
            {'name': 'Sapu Mhicha', 'price': 220, 'category': 'Newari Cuisine'},

            # Other Nepali Delicacies
            {'name': 'Momo (Buff/Chicken/Veg)', 'price': 130, 'category': 'Nepali Delicacies'},
            {'name': 'Thukpa', 'price': 110, 'category': 'Nepali Delicacies'},
            {'name': 'Dal Bhat Tarkari', 'price': 180, 'category': 'Nepali Delicacies'},

            # Italian Cuisine
            {'name': 'Margherita Pizza', 'price': 350, 'category': 'Italian Cuisine'},
            {'name': 'Spaghetti Carbonara', 'price': 400, 'category': 'Italian Cuisine'},
            {'name': 'Lasagna', 'price': 420, 'category': 'Italian Cuisine'},
            {'name': 'Penne Arrabbiata', 'price': 300, 'category': 'Italian Cuisine'},

            # Indian Cuisine
            {'name': 'Butter Chicken', 'price': 350, 'category': 'Indian Cuisine'},
            {'name': 'Paneer Tikka', 'price': 300, 'category': 'Indian Cuisine'},
            {'name': 'Biryani (Veg/Chicken)', 'price': 320, 'category': 'Indian Cuisine'},
            {'name': 'Naan / Garlic Naan', 'price': 50, 'category': 'Indian Cuisine'},

            # Bakery
            {'name': 'Chocolate Cake Slice', 'price': 120, 'category': 'Bakery'},
            {'name': 'Croissant', 'price': 90, 'category': 'Bakery'},
            {'name': 'Cinnamon Roll', 'price': 110, 'category': 'Bakery'},
            {'name': 'Muffins (Blueberry/Choco)', 'price': 100, 'category': 'Bakery'},

            # Beverages
            {'name': 'Espresso', 'price': 80, 'category': 'Beverages'},
            {'name': 'Cappuccino', 'price': 120, 'category': 'Beverages'},
            {'name': 'Masala Chai', 'price': 60, 'category': 'Beverages'},
            {'name': 'Lassi (Sweet/Salted)', 'price': 70, 'category': 'Beverages'},
            {'name': 'Fresh Juice (Seasonal)', 'price': 100, 'category': 'Beverages'},
        ]

        for item in menu_data:
            FoodItem.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f'Created {item["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated food items'))