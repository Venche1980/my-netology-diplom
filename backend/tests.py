from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from backend.models import Category, Order, Product, ProductInfo, Shop

User = get_user_model()


class UserRegistrationTest(TestCase):
    """Тесты регистрации и авторизации пользователей."""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        """Тест регистрации нового пользователя."""
        # Используем обычный Django test client вместо DRF APIClient для этого теста
        from django.test import Client

        client = Client()

        url = reverse("backend:user-register")
        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "password": "TestPassword123",
            "company": "ООО Тест",
            "position": "Менеджер",
        }

        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertTrue(response_data["Status"])

        # Проверяем что пользователь создан
        user = User.objects.get(email="ivan@example.com")
        self.assertEqual(user.first_name, "Иван")
        self.assertFalse(user.is_active)  # Неактивен до подтверждения

    def test_user_login(self):
        """Тест входа пользователя."""
        # Создаем активного пользователя
        User.objects.create_user(email="test@example.com", password="TestPassword123", is_active=True)

        url = reverse("backend:user-login")
        data = {"email": "test@example.com", "password": "TestPassword123"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["Status"])
        self.assertIn("Token", response.json())


class BasketTest(TestCase):
    """Тесты работы с корзиной."""

    def setUp(self):
        self.client = APIClient()

        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            email="buyer@example.com", password="TestPassword123", type="buyer", is_active=True
        )

        # Авторизуем клиента
        response = self.client.post(
            reverse("backend:user-login"), {"email": "buyer@example.com", "password": "TestPassword123"}
        )
        token = response.json()["Token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Создаем тестовый товар
        shop_user = User.objects.create_user(email="shop@example.com", password="TestPassword123", type="shop")
        self.shop = Shop.objects.create(name="Тестовый магазин", user=shop_user)
        self.category = Category.objects.create(name="Тестовая категория")
        self.product = Product.objects.create(name="Тестовый товар", category=self.category)
        self.product_info = ProductInfo.objects.create(
            product=self.product, shop=self.shop, external_id=1, quantity=10, price=1000, price_rrc=1200
        )

    def test_add_to_basket(self):
        """Тест добавления товара в корзину."""
        url = reverse("backend:basket")
        data = {"items": f'[{{"product_info": {self.product_info.id}, "quantity": 2}}]'}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["Status"])

        # Проверяем что товар в корзине
        order = Order.objects.get(user=self.user, state="basket")
        self.assertEqual(order.ordered_items.count(), 1)
        self.assertEqual(order.ordered_items.first().quantity, 2)

    def test_basket_unauthorized(self):
        """Тест доступа к корзине без авторизации."""
        self.client.credentials()  # Убираем токен

        url = reverse("backend:basket")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderTest(TestCase):
    """Тесты оформления заказов."""

    def setUp(self):
        self.client = APIClient()

        # Создаем и авторизуем пользователя
        self.user = User.objects.create_user(
            email="buyer@example.com", password="TestPassword123", type="buyer", is_active=True
        )

        response = self.client.post(
            reverse("backend:user-login"), {"email": "buyer@example.com", "password": "TestPassword123"}
        )
        token = response.json()["Token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_order_creation(self):
        """Тест создания заказа."""
        # Сначала нужно создать корзину с товарами
        # Здесь упрощенная версия теста

        url = reverse("backend:order")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class YAMLImportTest(TestCase):
    """Тесты загрузки товаров из YAML."""

    def setUp(self):
        self.client = APIClient()

        # Создаем пользователя-магазин
        self.shop_user = User.objects.create_user(
            email="shop@example.com", password="TestPassword123", type="shop", is_active=True
        )

        # Авторизуем
        response = self.client.post(
            reverse("backend:user-login"), {"email": "shop@example.com", "password": "TestPassword123"}
        )
        token = response.json()["Token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_partner_update_access(self):
        """Тест доступа к загрузке прайса."""
        url = reverse("backend:partner-update")

        # Пытаемся загрузить без URL
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["Status"])
        self.assertIn("Errors", response.json())

    def test_buyer_cannot_upload(self):
        """Тест что покупатель не может загружать товары."""
        # Создаем покупателя
        User.objects.create_user(
            email='buyer2@example.com',
            password='TestPassword123',
            type='buyer',
            is_active=True
        )

        # Авторизуемся как покупатель
        response = self.client.post(
            reverse('backend:user-login'),
            {'email': 'buyer2@example.com', 'password': 'TestPassword123'},
            format='json'  # Добавляем format='json'
        )

        # Проверяем успешность авторизации
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Token', response.json())

        token = response.json()['Token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        # Пытаемся загрузить
        url = reverse('backend:partner-update')
        response = self.client.post(url, {'url': 'http://example.com/test.yaml'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['Error'], 'Только для магазинов')
