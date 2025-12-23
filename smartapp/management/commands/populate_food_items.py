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
            {'name': 'Yomari', 'price': 120, 'category': 'Newari Cuisine', 'img': 'https://century.com.np/wp-content/uploads/2021/12/yomari.jpg'},
            {'name': 'Chatamari', 'price': 150, 'category': 'Newari Cuisine', 'img': 'https://visitmadhyapur.com/storage/2024/12/chatamari-1.jpg'},
            {'name': 'Bara (Wo)', 'price': 100, 'category': 'Newari Cuisine', 'img': 'https://nepalicookbook.com/wp-content/uploads/2015/08/black-gram-pancake-maasko-bara.jpg'},
            {'name': 'Choila (Buff/Chicken)', 'price': 180, 'category': 'Newari Cuisine', 'img': 'https://junifoods.com/wp-content/uploads/2023/04/easy-chicken-choila-1024x693.png'},
            {'name': 'Samay Baji Set', 'price': 300, 'category': 'Newari Cuisine', 'img': 'https://english.onlinekhabar.com/wp-content/uploads/2019/05/Paalcha-Samay-Baji-768x512.jpg'},
            {'name': 'Sapu Mhicha', 'price': 220, 'category': 'Newari Cuisine', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Sapu_Micha.jpg/960px-Sapu_Micha.jpg?20200224090500'},

            # Other Nepali Delicacies
            {'name': 'Momo (Buff/Chicken/Veg)', 'price': 130, 'category': 'Nepali Delicacies', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Momo_nepal.jpg/960px-Momo_nepal.jpg?20230213214312'},
            {'name': 'Thukpa', 'price': 110, 'category': 'Nepali Delicacies', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Nepalese_Thuppa.jpg/960px-Nepalese_Thuppa.jpg?20170517163407'},
            {'name': 'Dal Bhat Tarkari', 'price': 180, 'category': 'Nepali Delicacies', 'img': 'https://english.onlinekhabar.com/wp-content/uploads/2017/12/Nepali_Dal_Bhat-768x576.jpg'},

            # Italian Cuisine
            {'name': 'Margherita Pizza', 'price': 350, 'category': 'Italian Cuisine', 'img': 'https://media.istockphoto.com/id/1168754685/photo/pizza-margarita-with-cheese-top-view-isolated-on-white-background.jpg?s=612x612&w=0&k=20&c=psLRwd-hX9R-S_iYU-sihB4Jx2aUlUr26fkVrxGDfNg='},
            {'name': 'Spaghetti Carbonara', 'price': 400, 'category': 'Italian Cuisine', 'img': 'https://media.istockphoto.com/id/1581084025/photo/plate-with-spaghetti-carbonara-on-a-laid-table.jpg?s=612x612&w=0&k=20&c=8tKlSwoS2e0TE4N7Hb2wgQnCtnY89hHCQ2WytnWU1ug='},
            {'name': 'Lasagna', 'price': 420, 'category': 'Italian Cuisine', 'img': 'https://media.istockphoto.com/id/1477739651/photo/portion-of-lasagna-in-baking-dish-top-view.jpg?s=612x612&w=0&k=20&c=q3NU_5dcP95OManS6khkLZdhk9XzfCBw-UkmQSn5IRI='},
            {'name': 'Penne Arrabbiata', 'price': 300, 'category': 'Italian Cuisine', 'img': 'https://media.istockphoto.com/id/2168058934/photo/classic-italian-pasta-penne-alla-arrabiata-with-basil-and-freshly-grated-parmesan-cheese-on.jpg?s=612x612&w=0&k=20&c=FrY9AvangfPnTcJ-kb5muty6nJYh_l1RcoD94xhxx7o='},

            # Indian Cuisine
            {'name': 'Butter Chicken', 'price': 350, 'category': 'Indian Cuisine', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Butter_Chicken.jpg/800px-Butter_Chicken.jpg'},
            {'name': 'Paneer Tikka', 'price': 300, 'category': 'Indian Cuisine', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Paneer_Tikka.jpg/800px-Paneer_Tikka.jpg'},
            {'name': 'Biryani (Veg/Chicken)', 'price': 320, 'category': 'Indian Cuisine', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Chicken_Biryani.jpg/800px-Chicken_Biryani.jpg'},
            {'name': 'Naan / Garlic Naan', 'price': 50, 'category': 'Indian Cuisine', 'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/NaanBread.jpg/800px-NaanBread.jpg'},

            # Bakery
            {'name': 'Chocolate Cake Slice', 'price': 120, 'category': 'Bakery', 'img': 'https://media.istockphoto.com/id/1411524598/photo/chicken-tikka-masala-cooked-marinated-chicken-in-spiced-curry-sauce.jpg?s=612x612&w=0&k=20&c=3JLbYigOnTQm-4exK-7uKeI3YoR0g9HxAkjxmuVmfpY='},
            {'name': 'Croissant', 'price': 90, 'category': 'Bakery', 'img': 'https://media.istockphoto.com/id/178462137/photo/croissant-isolated-on-white.jpg?s=612x612&w=0&k=20&c=jDNGlWLbufaPJuAxs5FH0-yyOC8SoPSwSE9FQKjGwJQ='},
            {'name': 'Cinnamon Roll', 'price': 110, 'category': 'Bakery', 'img': 'https://media.istockphoto.com/id/1299104835/photo/cinnamon-roll-with-white-icing.jpg?s=612x612&w=0&k=20&c=0TktSCIBtf8vODvAymGjRIRp1SR30wsLLc-8YYqJgZ8='},
            {'name': 'Muffins (Blueberry/Choco)', 'price': 100, 'category': 'Bakery', 'img': 'https://marleysmenu.com/wp-content/uploads/2022/05/Blueberry-Chocolate-Chip-Muffins-Featured-Image-750x750.jpg'},

            # Beverages
            {'name': 'Espresso', 'price': 80, 'category': 'Beverages', 'img': 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8ZXNwcmVzc28lMjBjb2ZmZWV8ZW58MHx8MHx8fDA%3D'},
            {'name': 'Cappuccino', 'price': 120, 'category': 'Beverages', 'img': 'https://media.istockphoto.com/id/523168994/photo/cappuccino-with-coffee-beans.jpg?s=612x612&w=0&k=20&c=qhRFxaeTppFykANecfXx8B17JSJYNJgW2KExDrUWKCk='},
            {'name': 'Masala Chai', 'price': 60, 'category': 'Beverages', 'img': 'https://media.istockphoto.com/id/1336601313/photo/top-view-of-indian-herbal-masala-chai-or-traditional-beverage-tea-with-milk-and-spices-kerala.jpg?s=612x612&w=0&k=20&c=txjXqXtu3_PcA0ztNxyNVXJ-YziORr2XnuHWIriNEKk='},
            {'name': 'Lassi (Sweet/Salted)', 'price': 70, 'category': 'Beverages', 'img': 'https://cdn3.didevelop.com/public/cdn/533_82bb2b9654e06e35949fb4f9f5ba970f.jpg'},
            {'name': 'Fresh Juice (Seasonal)', 'price': 100, 'category': 'Beverages', 'img': 'https://media.istockphoto.com/id/537837754/photo/orange-juice-splash.jpg?s=612x612&w=0&k=20&c=twbr5N3vTUl9Qw_cerGXX9zQlkTVa7ICatdUqyxgsvg='},
        ]

        for item in menu_data:
            FoodItem.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f'Created {item["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated food items'))