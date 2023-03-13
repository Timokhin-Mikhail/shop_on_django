from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product


class TheMostPurchasedProductsViewAuthTestCase(TestCase):
    fixtures = ['orders-fixture.json',
                'products-fixture.json',
                'producttoorder-fixture.json',
                'users-fixture.json',]

    def test_the_most_purchased_products(self):
        response = self.client.get(reverse('shopapp:popular_products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The most popular products')
        self.assertTemplateUsed(response, 'shopapp/the_most_purchased_products_list.html')
        self.assertTrue(len(response.context['products']) == 7)


class ProductsInteractionWithTheUserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="Jon", password="Jon", )
        cls.user.user_permissions.add(Permission.objects.get(codename='add_product'))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_products_list_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Products')
        self.assertTemplateUsed(response, 'shopapp/products-list.html')
        self.assertContains(response, 'Create a new product')
        self.assertContains(response, 'No products yet')
        self.client.logout()
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertNotContains(response, 'Create a new product')


    def test_product_create_page(self):
        response = self.client.get(reverse('shopapp:product_create'))
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get(reverse('shopapp:product_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopapp/product_form.html')
        self.client.post(reverse('shopapp:product_create'), {"name": "Test product 1",
                                                             "price": '100',
                                                             "description": "about test product 1",
                                                             "discount": '11'})
        self.assertTrue(Product.objects.get(name="Test product 1"))
        Product.objects.get(name="Test product 1").delete()


class ProductsDetailsTestCase(TestCase):
    fixtures = ['products-fixture.json', 'users-fixture.json',]

    def test_product_details(self):
        response = self.client.get(reverse('shopapp:product_details', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Зеленые яблоки')
        self.assertTemplateUsed(response, "shopapp/products-details.html")







