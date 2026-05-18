from decimal import Decimal
from os import getenv

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.cart.models import Cart
from apps.catalog.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.reviews.models import Review

DEMO_PASSWORD = "demo-password-123"

DEMO_CATEGORIES = (
    {
        "name": "Солод",
        "slug": "malt",
        "description": "Базовый и специальный солод для домашнего пивоварения.",
    },
    {
        "name": "Хмель",
        "slug": "hops",
        "description": "Ароматный и горький хмель для разных стилей пива.",
    },
    {
        "name": "Дрожжи",
        "slug": "yeast",
        "description": "Пивные дрожжи для элей, лагеров и экспериментальных партий.",
    },
)

DEMO_PRODUCTS = (
    {
        "category_slug": "malt",
        "name": "Pilsner Malt",
        "slug": "pilsner-malt",
        "sku": "DEMO-MALT-PILSNER",
        "description": "Светлый базовый солод для лагеров и лёгких элей.",
        "price": Decimal("210.00"),
        "old_price": Decimal("240.00"),
        "stock_quantity": 50,
    },
    {
        "category_slug": "malt",
        "name": "Caramel Malt",
        "slug": "caramel-malt",
        "sku": "DEMO-MALT-CARAMEL",
        "description": "Карамельный солод для цвета, тела и лёгкой сладости.",
        "price": Decimal("260.00"),
        "old_price": None,
        "stock_quantity": 35,
    },
    {
        "category_slug": "hops",
        "name": "Cascade Hops",
        "slug": "cascade-hops",
        "sku": "DEMO-HOPS-CASCADE",
        "description": "Классический американский хмель с цитрусовым профилем.",
        "price": Decimal("390.00"),
        "old_price": Decimal("430.00"),
        "stock_quantity": 20,
    },
    {
        "category_slug": "hops",
        "name": "Citra Hops",
        "slug": "citra-hops",
        "sku": "DEMO-HOPS-CITRA",
        "description": "Яркий ароматический хмель для IPA и pale ale.",
        "price": Decimal("520.00"),
        "old_price": None,
        "stock_quantity": 18,
    },
    {
        "category_slug": "yeast",
        "name": "Safale US-05",
        "slug": "safale-us05-yeast",
        "sku": "DEMO-YEAST-US05",
        "description": "Нейтральные элевые дрожжи для чистого профиля брожения.",
        "price": Decimal("310.00"),
        "old_price": None,
        "stock_quantity": 25,
    },
)

DEMO_USERS = (
    {
        "username": "demo_customer",
        "email": "demo.customer@example.com",
        "first_name": "Демо",
        "last_name": "Покупатель",
        "phone": "+79990000001",
    },
    {
        "username": "demo_reviewer",
        "email": "demo.reviewer@example.com",
        "first_name": "Демо",
        "last_name": "Обзорщик",
        "phone": "+79990000002",
    },
)


class Command(BaseCommand):
    """Создать безопасные демонстрационные данные для локальной витрины."""

    help = "Создаёт идемпотентные demo-данные: категории, товары, пользователей, заказы, платежи и отзывы."

    def add_arguments(self, parser) -> None:
        """Добавить безопасные флаги reset-режима."""

        parser.add_argument("--reset", action="store_true", help="Удалить seed-owned demo-данные перед созданием.")
        parser.add_argument("--yes", action="store_true", help="Подтвердить destructive reset-режим.")

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        """Создать или обновить demo-данные без зависимости от `src/prepare/`."""

        reset = options["reset"]
        yes = options["yes"]

        if reset:
            self._validate_reset_allowed(yes=yes)
            self._delete_demo_data()

        categories = self._seed_categories()
        products = self._seed_products(categories)
        users = self._seed_users()
        self._seed_orders(users, products)
        self._seed_reviews(users, products)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"Demo password: {DEMO_PASSWORD}")

    def _validate_reset_allowed(self, *, yes: bool) -> None:
        """Остановить destructive reset вне локального/demo окружения."""

        if not yes:
            raise CommandError("Refusing to reset demo data without --yes.")

        if not settings.DEBUG:
            raise CommandError("Refusing to reset demo data when DEBUG=False.")

        environment = getenv("ENVIRONMENT", "").lower()
        settings_module = getenv("DJANGO_SETTINGS_MODULE", "").lower()

        if environment == "production" or "production" in settings_module:
            raise CommandError("Refusing to reset demo data outside local/demo environment.")

    def _delete_demo_data(self) -> None:
        """Удалить только известные seed-owned данные."""

        User = get_user_model()
        demo_users = User.objects.filter(username__in=[user["username"] for user in DEMO_USERS])
        demo_orders = Order.objects.filter(user__in=demo_users)
        Payment.objects.filter(order__in=demo_orders).delete()
        demo_orders.delete()
        Review.objects.filter(user__in=demo_users).delete()
        Cart.objects.filter(user__in=demo_users).delete()
        demo_users.delete()
        Product.objects.filter(slug__in=[product["slug"] for product in DEMO_PRODUCTS]).delete()
        Category.objects.filter(slug__in=[category["slug"] for category in DEMO_CATEGORIES]).delete()

    def _seed_categories(self) -> dict[str, Category]:
        """Создать или обновить demo-категории по стабильному slug."""

        categories: dict[str, Category] = {}
        for payload in DEMO_CATEGORIES:
            category, _created = Category.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "name": payload["name"],
                    "description": payload["description"],
                    "is_active": True,
                    "is_deleted": False,
                    "deleted_at": None,
                },
            )
            categories[category.slug] = category
        return categories

    def _seed_products(self, categories: dict[str, Category]) -> dict[str, Product]:
        """Создать или обновить demo-товары по стабильному slug."""

        products: dict[str, Product] = {}
        for payload in DEMO_PRODUCTS:
            product, _created = Product.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "category": categories[payload["category_slug"]],
                    "name": payload["name"],
                    "sku": payload["sku"],
                    "description": payload["description"],
                    "price": payload["price"],
                    "old_price": payload["old_price"],
                    "stock_quantity": payload["stock_quantity"],
                    "is_active": True,
                    "is_deleted": False,
                    "deleted_at": None,
                },
            )
            products[product.slug] = product
        return products

    def _seed_users(self) -> dict[str, object]:
        """Создать или обновить demo-пользователей по username."""

        User = get_user_model()
        users = {}
        for payload in DEMO_USERS:
            user, _created = User.objects.update_or_create(
                username=payload["username"],
                defaults={
                    "email": payload["email"],
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                    "phone": payload["phone"],
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])
            users[user.username] = user
        return users

    def _seed_orders(self, users: dict[str, object], products: dict[str, Product]) -> None:
        """Пересоздать demo-заказы известных пользователей без дубликатов."""

        demo_users = list(users.values())
        demo_orders = Order.objects.filter(user__in=demo_users)
        Payment.objects.filter(order__in=demo_orders).delete()
        demo_orders.delete()

        customer = users["demo_customer"]
        order = Order.objects.create(
            user=customer,
            status=Order.Status.PAID,
            customer_name=customer.get_full_name() or customer.username,
            customer_email=customer.email,
            customer_phone=customer.phone,
            delivery_address="Москва, Демо-улица, 1",
            comment="Демонстрационный заказ.",
            total_price=Decimal("0.00"),
        )

        selected_products = (products["pilsner-malt"], products["cascade-hops"])
        for product in selected_products:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=1,
            )
        order.recalculate_total_price()

        Payment.objects.create(
            order=order,
            status=Payment.Status.SUCCEEDED,
            method=Payment.Method.OTHER,
            amount=order.total_price,
            provider="mock",
            provider_payment_id="demo-payment-paid",
            paid_at=timezone.now(),
        )

        reviewer = users["demo_reviewer"]
        review_order = Order.objects.create(
            user=reviewer,
            status=Order.Status.COMPLETED,
            customer_name=reviewer.get_full_name() or reviewer.username,
            customer_email=reviewer.email,
            customer_phone=reviewer.phone,
            delivery_address="Санкт-Петербург, Демо-проспект, 2",
            comment="Заказ для демонстрации отзывов.",
            total_price=products["citra-hops"].price,
        )
        OrderItem.objects.create(
            order=review_order,
            product=products["citra-hops"],
            product_name=products["citra-hops"].name,
            price=products["citra-hops"].price,
            quantity=1,
        )
        Payment.objects.create(
            order=review_order,
            status=Payment.Status.SUCCEEDED,
            method=Payment.Method.OTHER,
            amount=review_order.total_price,
            provider="mock",
            provider_payment_id="demo-payment-completed",
            paid_at=timezone.now(),
        )

    def _seed_reviews(self, users: dict[str, object], products: dict[str, Product]) -> None:
        """Создать или обновить demo-отзывы по паре user + product."""

        Review.objects.update_or_create(
            user=users["demo_reviewer"],
            product=products["citra-hops"],
            defaults={
                "rating": 5,
                "title": "Яркий аромат",
                "text": "Хмель хорошо подошёл для демонстрационного IPA.",
                "status": Review.Status.PUBLISHED,
                "is_verified_purchase": True,
            },
        )
        Review.objects.update_or_create(
            user=users["demo_customer"],
            product=products["pilsner-malt"],
            defaults={
                "rating": 4,
                "title": "Хорошая база",
                "text": "Солод даёт чистый профиль и хорошо подходит для старта.",
                "status": Review.Status.PUBLISHED,
                "is_verified_purchase": True,
            },
        )
