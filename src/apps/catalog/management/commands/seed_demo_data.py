from decimal import Decimal
from os import getenv
from pathlib import Path
from shutil import copy2

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.cart.models import Cart
from apps.catalog.models import Category, Product, ProductImage
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.reviews.models import Review

DEMO_PASSWORD = "demo-password-123"

DEMO_CATEGORIES = (
    {
        "name": "Хмель",
        "slug": "hops",
        "description": "Ароматные и горькие сорта хмеля для IPA, пилснеров, лагеров и экспериментальных варок.",
    },
    {
        "name": "Солод",
        "slug": "malt",
        "description": "Базовый и специальный солод для классических и современных домашних рецептов.",
    },
    {
        "name": "Дрожжи",
        "slug": "yeast",
        "description": "Сухие и жидкие пивные дрожжи для чистого брожения, элей, лагеров и сочных IPA.",
    },
    {
        "name": "Добавки",
        "slug": "adjuncts",
        "description": "Несоложёное зерно и вспомогательные ингредиенты для текстуры, тела и фирменного характера пива.",
    },
    {
        "name": "Наборы",
        "slug": "kits",
        "description": "Готовые наборы ингредиентов с понятной логикой сборки рецепта.",
    },
)

DEMO_PRODUCTS = (
    {
        "category_slug": "hops",
        "name": "Хмель Citra",
        "slug": "citra-hops",
        "sku": "DEMO-HOPS-CITRA",
        "description": "Один из самых узнаваемых сортов для IPA и pale ale. Даёт яркий цитрус, грейпфрут, лайм, личи, маракуйю и тропический профиль.",
        "price": Decimal("520.00"),
        "old_price": None,
        "stock_quantity": 18,
        "image": "citra_hops.jpg",
    },
    {
        "category_slug": "malt",
        "name": "Солод Maris Otter Pale",
        "slug": "maris-otter-malt",
        "sku": "DEMO-MALT-MARIS-OTTER",
        "description": "Классический британский базовый солод с насыщенным хлебным и бисквитным профилем для биттеров, портеров и pale ale.",
        "price": Decimal("250.00"),
        "old_price": None,
        "stock_quantity": 40,
        "image": "maris_otter_malt.jpg",
    },
    {
        "category_slug": "yeast",
        "name": "Дрожжи SafAle US-05",
        "slug": "safale-us05-yeast",
        "sku": "DEMO-YEAST-US05",
        "description": "Популярные американские элевые дрожжи с чистым профилем, высокой сбраживаемостью и предсказуемым результатом.",
        "price": Decimal("310.00"),
        "old_price": None,
        "stock_quantity": 25,
        "image": "safale_us05_yeast.jpg",
    },
    {
        "category_slug": "hops",
        "name": "Хмель Cascade",
        "slug": "cascade-hops",
        "sku": "DEMO-HOPS-CASCADE",
        "description": "Классика американского крафта: умеренная горечь, цветочный характер, грейпфрут, апельсин и мягкий цитрусовый аромат.",
        "price": Decimal("390.00"),
        "old_price": Decimal("430.00"),
        "stock_quantity": 20,
        "image": "cascade_hops.jpg",
    },
    {
        "category_slug": "malt",
        "name": "Карамельный солод 60L",
        "slug": "caramel-malt",
        "sku": "DEMO-MALT-CARAMEL",
        "description": "Специальный солод для медно-янтарного цвета, карамельной сладости, полноты тела и устойчивой пены.",
        "price": Decimal("260.00"),
        "old_price": None,
        "stock_quantity": 35,
        "image": "caramel_malt.jpg",
    },
    {
        "category_slug": "hops",
        "name": "Хмель Saaz",
        "slug": "saaz-hops",
        "sku": "DEMO-HOPS-SAAZ",
        "description": "Благородный чешский хмель для пилснеров и лагеров: пряный, травяной, цветочный, с мягкой европейской элегантностью.",
        "price": Decimal("475.00"),
        "old_price": None,
        "stock_quantity": 28,
        "image": "saaz_hops.jpg",
    },
    {
        "category_slug": "malt",
        "name": "Солод Pilsner",
        "slug": "pilsner-malt",
        "sku": "DEMO-MALT-PILSNER",
        "description": "Светлый базовый солод для немецких и чешских пилснеров, лёгких лагеров, saison и чистых экспериментальных варок.",
        "price": Decimal("210.00"),
        "old_price": Decimal("240.00"),
        "stock_quantity": 50,
        "image": "pilsner_malt.jpg",
    },
    {
        "category_slug": "yeast",
        "name": "Дрожжи Imperial Organic A07",
        "slug": "imperial-yeast",
        "sku": "DEMO-YEAST-IMPERIAL-A07",
        "description": "Жидкая культура для сбалансированных американских элей с лёгкой фруктовостью и чистым, надёжным брожением.",
        "price": Decimal("899.00"),
        "old_price": None,
        "stock_quantity": 16,
        "image": "imperial_yeast.jpg",
    },
    {
        "category_slug": "hops",
        "name": "Хмель Centennial",
        "slug": "centennial-hops",
        "sku": "DEMO-HOPS-CENTENNIAL",
        "description": "«Super Cascade» с выраженным лимоном, грейпфрутом, цветочностью и чистой горечью для классических American IPA.",
        "price": Decimal("620.00"),
        "old_price": None,
        "stock_quantity": 22,
        "image": "centennial_hops.jpg",
    },
    {
        "category_slug": "hops",
        "name": "Хмель Mosaic",
        "slug": "mosaic-hops",
        "sku": "DEMO-HOPS-MOSAIC",
        "description": "Многослойный современный сорт с манго, гуавой, мандарином, черникой, персиком и лёгкими хвойными оттенками.",
        "price": Decimal("950.00"),
        "old_price": None,
        "stock_quantity": 14,
        "image": "mosaic_hops.jpg",
    },
    {
        "category_slug": "kits",
        "name": "Набор West Coast IPA",
        "slug": "west-coast-ipa-kit",
        "sku": "DEMO-KIT-WEST-COAST-IPA",
        "description": "Готовый all-grain набор для сухого, горького и ароматного West Coast IPA с солодовой базой и ярким хмелевым профилем.",
        "price": Decimal("6000.00"),
        "old_price": Decimal("6600.00"),
        "stock_quantity": 10,
        "image": "ipa_kit.jpg",
    },
    {
        "category_slug": "adjuncts",
        "name": "Несоложёная пшеница",
        "slug": "unmalted-wheat",
        "sku": "DEMO-ADJUNCT-WHEAT",
        "description": "Ингредиент для бельгийского witbier: даёт лёгкую мутность, шелковистую текстуру, свежесть и характерную пшеничную основу.",
        "price": Decimal("180.00"),
        "old_price": None,
        "stock_quantity": 45,
        "image": "unmalted_wheat.jpg",
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
        "first_name": "Иван",
        "last_name": "Пивовар",
        "phone": "+79990000002",
    },
    {
        "username": "demo_brewer",
        "email": "demo.brewer@example.com",
        "first_name": "Анна",
        "last_name": "Солодова",
        "phone": "+79990000003",
    },
    {
        "username": "demo_taster",
        "email": "demo.taster@example.com",
        "first_name": "Олег",
        "last_name": "Дегустатор",
        "phone": "+79990000004",
    },
)

REVIEWERS = ("demo_reviewer", "demo_brewer", "demo_taster")


class Command(BaseCommand):
    """Создать безопасные демонстрационные данные для локальной витрины."""

    help = "Создаёт идемпотентные demo-данные: категории, товары, изображения, пользователей, заказы, платежи и отзывы."

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
        """Создать или обновить reference-набор demo-товаров по стабильному slug."""

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
            self._seed_product_image(product, source_filename=payload["image"])
            products[product.slug] = product
        return products

    def _seed_product_image(self, product: Product, *, source_filename: str) -> None:
        """Скопировать tracked reference asset в MEDIA_ROOT и привязать его к ProductImage."""

        source = settings.BASE_DIR / "static" / "shop" / "img" / "products" / source_filename
        if not source.exists():
            self.stdout.write(self.style.WARNING(f"Skipping missing demo image: {source_filename}"))
            return

        destination_dir = Path(settings.MEDIA_ROOT) / "demo" / "products"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source_filename
        copy2(source, destination)

        image_name = f"demo/products/{source_filename}"
        image, _created = ProductImage.objects.update_or_create(
            product=product,
            image=image_name,
            defaults={
                "alt_text": product.name,
                "is_main": True,
                "sort_order": 0,
            },
        )
        product.images.filter(image__startswith="demo/products/").exclude(pk=image.pk).delete()
        product.images.exclude(pk=image.pk).update(is_main=False)

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
        """Пересоздать demo-заказы известных пользователей без дублей."""

        demo_users = list(users.values())
        demo_orders = Order.objects.filter(user__in=demo_users)
        Payment.objects.filter(order__in=demo_orders).delete()
        demo_orders.delete()

        product_list = list(products.values())
        for user_index, user in enumerate(demo_users, start=1):
            order = Order.objects.create(
                user=user,
                status=Order.Status.COMPLETED if user.username in REVIEWERS else Order.Status.PAID,
                customer_name=user.get_full_name() or user.username,
                customer_email=user.email,
                customer_phone=user.phone,
                delivery_address=f"Демо-город, улица Пивоваров, {user_index}",
                comment="Демонстрационный заказ для локальной витрины.",
                total_price=Decimal("0.00"),
            )

            for product in product_list:
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
                provider_payment_id=f"demo-payment-{user.username}",
                paid_at=timezone.now(),
            )

    def _seed_reviews(self, users: dict[str, object], products: dict[str, Product]) -> None:
        """Создать или обновить demo-отзывы по паре user + product."""

        for product_index, product in enumerate(products.values(), start=1):
            for reviewer_index, username in enumerate(REVIEWERS, start=1):
                rating = 5 if reviewer_index < 3 else 4
                title, text = _review_copy(product.name, product_index=product_index, reviewer_index=reviewer_index)
                Review.objects.update_or_create(
                    user=users[username],
                    product=product,
                    defaults={
                        "rating": rating,
                        "title": title,
                        "text": text,
                        "status": Review.Status.PUBLISHED,
                        "is_verified_purchase": True,
                        "moderated_at": timezone.now(),
                        "moderation_comment": "Опубликовано seed-командой для демонстрационного каталога.",
                    },
                )


def _review_copy(product_name: str, *, product_index: int, reviewer_index: int) -> tuple[str, str]:
    """Вернуть русскоязычный отзыв в стиле reference-витрины без англоязычного copy."""

    variants = (
        (
            "Отличный результат в варке",
            f"{product_name} хорошо показал себя в тестовой партии: аромат чистый, профиль понятный, результат легко повторить.",
        ),
        (
            "Стабильное качество",
            f"Использую {product_name} для демонстрационных рецептов. Удобная фасовка, предсказуемое поведение и хороший итоговый вкус.",
        ),
        (
            "Подходит для экспериментов",
            f"{product_name} даёт заметный характер и не требует сложной подготовки. Для учебной витрины и первых рецептов это удачный выбор.",
        ),
    )
    title, text = variants[(reviewer_index - 1) % len(variants)]
    return f"{title} #{product_index}", text
