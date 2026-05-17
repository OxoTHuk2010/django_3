from django.db.models import Avg, Count, QuerySet

from apps.catalog.models import Category, Product, ProductImage
from apps.reviews.models import Review


def get_active_category_queryset() -> QuerySet[Category]:
    """
    Вернуть категории, доступные для публичного каталога.

    Публичный каталог не должен показывать неактивные категории и категории,
    скрытые через soft delete.
    """

    return Category.objects.filter(
        is_active=True,
        is_deleted=False,
    ).order_by("name")


def get_product_list_queryset() -> QuerySet[Product]:
    """
    Вернуть базовый queryset товаров для публичного списка.

    Здесь фиксируется общее правило видимости: пользователь видит только
    активные неудалённые товары из активных неудалённых категорий.
    """

    return (
        Product.objects.filter(
            is_active=True,
            is_deleted=False,
            category__is_active=True,
            category__is_deleted=False,
        )
        .select_related("category")
        .prefetch_related("images")
    )


def get_product_detail_queryset() -> QuerySet[Product]:
    """
    Вернуть queryset публичных товаров для детальной страницы.

    Детальная страница использует те же правила видимости, что и список товаров:
    неактивные, soft-deleted товары и товары из скрытых категорий недоступны.
    """

    return get_product_list_queryset()


def get_product_main_image(product: Product) -> ProductImage | None:
    """
    Выбрать основное изображение товара из ProductImage.

    ADR 0009 запрещает подбирать изображение по slug или из src/prepare, поэтому
    fallback ограничен только порядком связанных ProductImage.
    """

    return product.images.order_by("-is_main", "sort_order", "id").first()


def get_published_product_reviews(product: Product) -> QuerySet[Review]:
    """
    Вернуть опубликованные отзывы товара для read-only блока детальной страницы.

    На этапе 7 отзывы только читаются, а создание отзывов остаётся будущим этапом.
    """

    return (
        product.reviews.filter(
            status=Review.Status.PUBLISHED,
        )
        .select_related("user")
        .order_by("-created_at")
    )


def get_product_review_stats(product: Product) -> dict[str, int | float | None]:
    """
    Посчитать статистику отзывов только по опубликованным отзывам.

    Непубличные отзывы не должны влиять на рейтинг и количество отзывов.
    """

    return get_published_product_reviews(product).aggregate(
        average_rating=Avg("rating"),
        reviews_count=Count("id"),
    )


def get_related_products(product: Product) -> QuerySet[Product]:
    """
    Вернуть до трёх похожих товаров из той же активной категории.

    ADR 0012 фиксирует минимальное правило похожести: та же категория, активный
    неудалённый товар, без исключения товаров с нулевым остатком.
    """

    return (
        get_product_list_queryset()
        .filter(
            category=product.category,
        )
        .exclude(
            id=product.id,
        )
        .order_by("name")[:3]
    )
