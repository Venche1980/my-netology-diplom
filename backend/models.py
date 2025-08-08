from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_rest_passwordreset.tokens import get_token_generator

# Выборы для статусов заказа
STATE_CHOICES = (
    ("basket", "Статус корзины"),
    ("new", "Новый"),
    ("confirmed", "Подтвержден"),
    ("assembled", "Собран"),
    ("sent", "Отправлен"),
    ("delivered", "Доставлен"),
    ("canceled", "Отменен"),
)

# Типы пользователей в системе
USER_TYPE_CHOICES = (
    ("shop", "Магазин"),
    ("buyer", "Покупатель"),
)


# Create your models here.


class UserManager(BaseUserManager):
    """
    Менеджер для кастомной модели пользователя.

    Переопределяет стандартные методы создания пользователей для работы
    с email в качестве основного идентификатора вместо username.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создание и сохранение пользователя с email и паролем.

        Args:
            email (str): Email адрес пользователя
            password (str): Пароль пользователя
            **extra_fields: Дополнительные поля модели User

        Returns:
            User: Созданный пользователь

        Raises:
            ValueError: Если email не указан
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создание обычного пользователя.

        Args:
            email (str): Email адрес
            password (str, optional): Пароль
            **extra_fields: Дополнительные поля

        Returns:
            User: Созданный пользователь
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создание суперпользователя.

        Args:
            email (str): Email адрес
            password (str): Пароль (обязателен для суперпользователя)
            **extra_fields: Дополнительные поля

        Returns:
            User: Созданный суперпользователь

        Raises:
            ValueError: Если is_staff или is_superuser не True
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Расширяет стандартную модель Django, используя email как основной
    идентификатор для входа. Поддерживает два типа пользователей:
    покупатели и магазины.

    Attributes:
        email (EmailField): Уникальный email адрес
        company (CharField): Название компании
        position (CharField): Должность
        type (CharField): Тип пользователя ('buyer' или 'shop')
        is_active (BooleanField): Активен ли пользователь (по умолчанию False)
    """

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = "email"
    email = models.EmailField(_("email address"), unique=True)
    company = models.CharField(verbose_name="Компания", max_length=40, blank=True)
    position = models.CharField(verbose_name="Должность", max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )
    type = models.CharField(verbose_name="Тип пользователя", choices=USER_TYPE_CHOICES, max_length=5, default="buyer")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ("email",)


class Shop(models.Model):
    """
    Модель магазина-поставщика.

    Магазин может загружать свой прайс-лист через YAML файл
    и управлять статусом приема заказов.
    """

    objects = models.manager.Manager()
    name = models.CharField(max_length=50, verbose_name="Название")
    url = models.URLField(verbose_name="Ссылка", null=True, blank=True)
    user = models.OneToOneField(User, verbose_name="Пользователь", blank=True, null=True, on_delete=models.CASCADE)
    state = models.BooleanField(
        verbose_name="статус получения заказов", default=True, help_text="Если True - магазин принимает заказы"
    )

    # filename

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ("-name",)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Категория товаров.

    Категории могут быть связаны с несколькими магазинами через M2M связь.
    """

    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name="Название")
    shops = models.ManyToManyField(Shop, verbose_name="Магазины", related_name="categories", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ("-name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель товара.

    Товар принадлежит одной категории и может иметь несколько
    вариантов (ProductInfo) в разных магазинах.
    """

    objects = models.manager.Manager()
    name = models.CharField(max_length=80, verbose_name="Название")
    category = models.ForeignKey(
        Category, verbose_name="Категория", related_name="products", blank=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"
        ordering = ("-name",)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
    Информация о товаре в конкретном магазине.

    Содержит цену, количество и другие параметры товара
    специфичные для магазина.
    """

    objects = models.manager.Manager()
    model = models.CharField(max_length=80, verbose_name="Модель", blank=True)
    external_id = models.PositiveIntegerField(
        verbose_name="Внешний ИД", help_text="ID товара во внешней системе магазина"
    )
    product = models.ForeignKey(
        Product, verbose_name="Продукт", related_name="product_infos", blank=True, on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop, verbose_name="Магазин", related_name="product_infos", blank=True, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name="Цена")
    price_rrc = models.PositiveIntegerField(verbose_name="Рекомендуемая розничная цена")

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=["product", "shop", "external_id"], name="unique_product_info"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.shop.name} ({self.price} руб.)"


class Parameter(models.Model):
    """
    Модель для хранения названий характеристик товаров.

    Например: "Диагональ", "Цвет", "Объем памяти" и т.д.
    """

    objects = models.manager.Manager()
    name = models.CharField(max_length=40, verbose_name="Название")

    class Meta:
        verbose_name = "Имя параметра"
        verbose_name_plural = "Список имен параметров"
        ordering = ("-name",)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Значение параметра для конкретного товара.

    Связывает ProductInfo с Parameter и хранит значение характеристики.
    """

    objects = models.manager.Manager()
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="product_parameters",
        blank=True,
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        Parameter, verbose_name="Параметр", related_name="product_parameters", blank=True, on_delete=models.CASCADE
    )
    value = models.CharField(verbose_name="Значение", max_length=100)

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=["product_info", "parameter"], name="unique_product_parameter"),
        ]

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


class Contact(models.Model):
    """
    Контактная информация пользователя для доставки.

    Пользователь может иметь несколько адресов доставки.
    """

    objects = models.manager.Manager()
    user = models.ForeignKey(
        User, verbose_name="Пользователь", related_name="contacts", blank=True, on_delete=models.CASCADE
    )

    city = models.CharField(max_length=50, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house = models.CharField(max_length=15, verbose_name="Дом", blank=True)
    structure = models.CharField(max_length=15, verbose_name="Корпус", blank=True)
    building = models.CharField(max_length=15, verbose_name="Строение", blank=True)
    apartment = models.CharField(max_length=15, verbose_name="Квартира", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f"{self.city} {self.street} {self.house}"


class Order(models.Model):
    """
    Модель заказа.

    Заказ проходит через различные статусы от корзины до доставки.
    При изменении статуса отправляется уведомление пользователю.
    """

    objects = models.manager.Manager()
    user = models.ForeignKey(
        User, verbose_name="Пользователь", related_name="orders", blank=True, on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(verbose_name="Статус", choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(Contact, verbose_name="Контакт", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказ"
        ordering = ("-dt",)

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    """
    Позиция в заказе.

    Связывает заказ с конкретным товаром из магазина
    и указывает количество.
    """

    objects = models.manager.Manager()
    order = models.ForeignKey(
        Order, verbose_name="Заказ", related_name="ordered_items", blank=True, on_delete=models.CASCADE
    )

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="ordered_items",
        blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Заказанная позиция"
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=["order_id", "product_info"], name="unique_order_item"),
        ]

    def __str__(self):
        return f"{self.product_info} - {self.quantity} шт."


class ConfirmEmailToken(models.Model):
    """
    Токен для подтверждения email адреса.

    Создается при регистрации пользователя и отправляется на email.
    После подтверждения токен удаляется.

    Attributes:
        user (ForeignKey): Связь с пользователем
        key (CharField): Уникальный токен
        created_at (DateTimeField): Время создания токена
    """

    objects = models.manager.Manager()

    class Meta:
        verbose_name = "Токен подтверждения Email"
        verbose_name_plural = "Токены подтверждения Email"

    @staticmethod
    def generate_key():
        """
        Генерация псевдослучайного токена.

        Использует os.urandom и binascii.hexlify для создания
        криптографически стойкого токена.

        Returns:
            str: Сгенерированный токен
        """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name="confirm_email_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("When was this token generated"))

    # Key field, though it is not the primary key of the model
    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автогенерации ключа.

        Если ключ не задан, генерирует новый перед сохранением.

        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы

        Returns:
            Model: Сохраненный объект
        """
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        """
        Строковое представление токена.

        Returns:
            str: Описание токена с указанием пользователя
        """
        return "Password reset token for user {user}".format(user=self.user)
