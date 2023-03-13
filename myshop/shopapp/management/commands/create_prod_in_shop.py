from random import randint

from django.core.management import BaseCommand
from shopapp.models import Product, ProductToShop


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start create random products in random shop")
        products = Product.objects.filter(id__gt=3)
        for product in products:
            shop_index = randint(1, 2)
            if shop_index:
                pis, status = ProductToShop.objects.get_or_create(product=product, shop_id=shop_index, count=5)
                if status:
                    pis.save()
        self.stdout.write(self.style.SUCCESS("Finish"))