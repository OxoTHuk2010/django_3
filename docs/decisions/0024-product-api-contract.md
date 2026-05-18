# ADR 0024: Контракт Product API: идентификатор, поля, фильтры и пагинация

## Статус

Принято.

## Актуальная сжатая версия

- Действующий Product API использует `slug` для detail route и review route.
- Public list поддерживает пагинацию, поиск, фильтрацию и сортировку.
- Product API не должен показывать неактивные, soft-deleted товары и товары из скрытых категорий.
- После появления конфликта `C036` slug routes сохраняются, но этап 27 должен добавить compatibility route `GET /api/products/<int:id>/`.
- Swagger/OpenAPI и `docs/api.md` должны после реализации показывать both current slug routes and compatibility id routes.
- Большие примеры ниже считаются историческим контрактным контекстом.

## Контекст

В рамках этапа 12 реализуется REST API проекта.

В web-каталоге уже реализованы:

```text
- список товаров /products/;
- детальная страница /products/<slug>/;
- поиск;
- фильтр категории;
- фильтр цены;
- сортировка;
- пагинация;
- публичная видимость только активных неудалённых товаров;
- публичная видимость только товаров из активных неудалённых категорий;
- изображения через ProductImage;
- read-only опубликованные отзывы;
- средний рейтинг товара.
```

В docs/api.md ранее был указан предварительный план:

GET /api/products/
GET /api/products/<id>/

Однако web-интерфейс уже использует slug как публичный идентификатор товара:

/products/<slug>/

Перед реализацией Product API необходимо зафиксировать публичный контракт:

- какой lookup используется для detail endpoint;
- какие поля возвращаются в list;
- какие поля возвращаются в detail;
- какие фильтры поддерживаются;
- какие сортировки поддерживаются;
- какая пагинация используется;
- включаются ли отзывы в product detail;
- совпадают ли правила публичной видимости API и web-каталога.

Без отдельного решения API может начать возвращать случайный набор полей, зависящий от текущего serializer, а не от осознанного публичного контракта.

## Решение

Принимаем следующее решение:

Product API использует slug как публичный lookup товара.

Канонические endpoints:

GET /api/products/
GET /api/products/<slug>/

Endpoint вида:

GET /api/products/<id>/

не является публичным контрактом Product API.

id может возвращаться в ответе как внутренний технический идентификатор, но не используется как основной публичный lookup товара.

Причина:

web-каталог уже использует /products/<slug>/,
поэтому API должен быть согласован с публичной моделью товара.
Правило публичной видимости

Product API должен возвращать только публично доступные товары.

В API не должны попадать товары, если:

- Product.is_active=False;
- Product.is_deleted=True;
- Category.is_active=False;
- Category.is_deleted=True;

Это правило должно совпадать с web-каталогом.

Публичный queryset Product API:

только активные неудалённые товары из активных неудалённых категорий.
Product list endpoint

Endpoint:

GET /api/products/

Назначение:

Получить paginated список публичных товаров.

List serializer должен возвращать компактный набор данных, достаточный для карточек товара.

Минимальный контракт list item:

id
slug
name
short_description
price
old_price
category
main_image
average_rating
reviews_count
stock_status
url
Поля list serializer
id                 — внутренний идентификатор товара;
slug               — публичный идентификатор товара;
name               — название товара;
short_description  — краткое описание;
price              — актуальная цена;
old_price          — старая цена, если есть;
category           — краткая информация о категории;
main_image         — основное изображение товара;
average_rating     — средний рейтинг по опубликованным отзывам;
reviews_count      — количество опубликованных отзывов;
stock_status       — состояние наличия;
url                — API URL детальной карточки товара.

Пример ответа item в list:

{
  "id": 10,
  "slug": "iphone-15",
  "name": "iPhone 15",
  "short_description": "Смартфон Apple iPhone 15",
  "price": "89990.00",
  "old_price": "94990.00",
  "category": {
    "id": 2,
    "slug": "smartphones",
    "name": "Смартфоны"
  },
  "main_image": {
    "url": "/media/products/iphone-15-main.jpg",
    "alt_text": "iPhone 15"
  },
  "average_rating": "4.7",
  "reviews_count": 12,
  "stock_status": "in_stock",
  "url": "/api/products/iphone-15/"
}
Product detail endpoint

Endpoint:

GET /api/products/<slug>/

Назначение:

Получить подробную публичную информацию о товаре.

Detail serializer должен возвращать расширенный набор данных.

Минимальный контракт detail:

id
slug
name
sku
description
short_description
price
old_price
category
images
main_image
average_rating
reviews_count
stock_quantity
stock_status
is_available
related_products
url
web_url
created_at
updated_at
Поля detail serializer
id                 — внутренний идентификатор товара;
slug               — публичный идентификатор товара;
name               — название товара;
sku                — артикул;
description        — полное описание;
short_description  — краткое описание;
price              — актуальная цена;
old_price          — старая цена, если есть;
category           — краткая информация о категории;
images             — список изображений товара;
main_image         — основное изображение товара;
average_rating     — средний рейтинг по опубликованным отзывам;
reviews_count      — количество опубликованных отзывов;
stock_quantity     — текущий остаток;
stock_status       — состояние наличия;
is_available       — можно ли добавить товар в корзину;
related_products   — компактный список похожих товаров;
url                — API URL товара;
web_url            — web URL товара;
created_at         — дата создания;
updated_at         — дата обновления.

Пример detail response:

{
  "id": 10,
  "slug": "iphone-15",
  "name": "iPhone 15",
  "sku": "IPHONE-15-128-BLACK",
  "short_description": "Смартфон Apple iPhone 15",
  "description": "Подробное описание товара.",
  "price": "89990.00",
  "old_price": "94990.00",
  "category": {
    "id": 2,
    "slug": "smartphones",
    "name": "Смартфоны"
  },
  "main_image": {
    "url": "/media/products/iphone-15-main.jpg",
    "alt_text": "iPhone 15"
  },
  "images": [
    {
      "url": "/media/products/iphone-15-main.jpg",
      "alt_text": "iPhone 15",
      "is_main": true,
      "sort_order": 0
    }
  ],
  "average_rating": "4.7",
  "reviews_count": 12,
  "stock_quantity": 5,
  "stock_status": "in_stock",
  "is_available": true,
  "related_products": [
    {
      "id": 11,
      "slug": "iphone-15-plus",
      "name": "iPhone 15 Plus",
      "price": "99990.00",
      "url": "/api/products/iphone-15-plus/"
    }
  ],
  "url": "/api/products/iphone-15/",
  "web_url": "/products/iphone-15/",
  "created_at": "2026-05-18T10:00:00Z",
  "updated_at": "2026-05-18T10:00:00Z"
}
Отзывы в Product detail

Полные опубликованные отзывы не встраиваются в Product detail response.

Product detail возвращает только агрегированные данные:

average_rating
reviews_count

Полный список отзывов должен запрашиваться через отдельный review endpoint.

Например:

GET /api/reviews/?product=<slug>

или в будущем:

GET /api/products/<slug>/reviews/

Причина:

Отзывы являются отдельным ресурсом.
Product detail не должен разрастаться из-за вложенных коллекций.

Это упрощает пагинацию отзывов, фильтрацию, модерацию и будущую работу с review API.

Изображения

Product API использует ProductImage как единственный источник изображений товара.

Это согласуется с ADR 0009.

Правило выбора main_image:

1. изображение с is_main=True;
2. если такого нет — первое изображение по sort_order;
3. если sort_order одинаковый — первое изображение по id;
4. если изображений нет — main_image=null.

Placeholder на уровне API не подставляется.

Если у товара нет изображений:

{
  "main_image": null,
  "images": []
}
Фильтры Product API

Product API должен поддерживать фильтры, согласованные с web-каталогом.

Поддерживаемые query-параметры:

search
category
min_price
max_price
ordering
page
page_size
search
GET /api/products/?search=iphone

Ищет по публичным текстовым полям товара.

Минимально:

- name;
- short_description;
- description;
- sku, если это допустимо для публичного поиска.
category
GET /api/products/?category=smartphones

Фильтр по slug категории.

category принимает публичный Category.slug, а не Category.id.

Причина:

API публичного каталога должен быть согласован с человекочитаемыми URL.
min_price и max_price
GET /api/products/?min_price=1000&max_price=5000

Фильтр по актуальной цене товара.

ordering
GET /api/products/?ordering=price
GET /api/products/?ordering=-price
GET /api/products/?ordering=name
GET /api/products/?ordering=-created_at
GET /api/products/?ordering=rating

Разрешённые сортировки:

name
-name
price
-price
created_at
-created_at
rating
-rating
reviews_count
-reviews_count

Если передана неподдерживаемая сортировка, API должен вернуть 400 Bad Request, а не молча применять случайный порядок.

Пагинация

Product API использует стандартную page-number pagination.

Формат:

GET /api/products/?page=1&page_size=20

Базовые правила:

default page_size = 20
max page_size = 100

Формат ответа:

{
  "count": 125,
  "next": "http://example.com/api/products/?page=2",
  "previous": null,
  "results": []
}

Этот формат соответствует стандартной DRF PageNumberPagination и хорошо документируется через drf-spectacular.

Ошибки

Если товар по slug не найден или не является публично доступным:

GET /api/products/<slug>/

должен вернуть:

404 Not Found

API не должен раскрывать существование скрытых, удалённых или неактивных товаров.

Если переданы некорректные query-параметры:

- min_price больше max_price;
- price не является числом;
- ordering не входит в allowlist;
- page_size больше max page_size;

API должен вернуть:

400 Bad Request

с понятным описанием ошибки.

Последствия

Плюсы решения:

- API согласован с web URL товара;
- slug становится единым публичным идентификатором товара;
- id остаётся доступен как техническое поле, но не как основной lookup;
- list и detail serializers имеют явный контракт;
- отзывы остаются отдельным ресурсом;
- Product detail не становится тяжёлым из-за вложенных отзывов;
- фильтры API совпадают с web-каталогом по смыслу;
- пагинация стандартная и понятная;
- Swagger/OpenAPI будет описывать осознанный контракт.

Минусы решения:

- detail endpoint по slug требует уникальности slug;
- если slug товара изменится, старый API URL перестанет работать;
- client-приложениям нужно использовать slug для detail-запросов;
- фильтр category по slug требует дополнительного lookup категории;
- для отзывов нужен отдельный endpoint.
Связанные документы / файлы / настройки
- docs/api.md
- docs/architecture.md
- docs/conflicts.md
- docs/decisions/0024-product-api-contract.md
- docs/conflicts.md
- docs/decisions/0009-img-source.md
- docs/decisions/0011-reviews-rating.md
- docs/decisions/0012-rule-product.md
- apps/api/serializers/catalog.py
- apps/api/views/catalog.py
- apps/api/filters/catalog.py
- apps/api/routers.py
- apps/api/tests/test_catalog_api.py
- apps/catalog/models.py
- apps/reviews/models.py
Инварианты для реализации
1. Product API detail использует slug как lookup.
2. /api/products/<id>/ не является публичным endpoint MVP.
3. Product API возвращает только активные неудалённые товары.
4. Product API не возвращает товары из неактивных или удалённых категорий.
5. Product list serializer и detail serializer имеют разные наборы полей.
6. ProductImage является единственным источником изображений.
7. main_image может быть null.
8. Полные отзывы не встраиваются в Product detail.
9. Product detail возвращает average_rating и reviews_count.
10. Фильтр category использует category slug.
11. Поддерживаемые ordering значения должны быть явно ограничены allowlist.
12. Product API использует page-number pagination.
13. Некорректные фильтры возвращают 400 Bad Request.
14. Непубличный товар возвращает 404 Not Found.
Пример ViewSet
# apps/api/views/catalog.py

from rest_framework import viewsets

from apps.api.serializers.catalog import (
    ProductDetailSerializer,
    ProductListSerializer,
)
from apps.catalog.models import Product


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API для публичного каталога товаров.
    """

    lookup_field = "slug"

    def get_queryset(self):
        return (
            Product.objects
            .filter(
                is_active=True,
                is_deleted=False,
                category__is_active=True,
                category__is_deleted=False,
            )
            .select_related("category")
            .prefetch_related("images", "reviews")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer

        return ProductListSerializer
Пример router
# apps/api/routers.py

from rest_framework.routers import DefaultRouter

from apps.api.views.catalog import ProductViewSet

router = DefaultRouter()

router.register(
    r"products",
    ProductViewSet,
    basename="product",
)

При lookup_field = "slug" router должен формировать detail endpoint:

/api/products/<slug>/
Пример serializer-полей
# apps/api/serializers/catalog.py

from rest_framework import serializers


class ProductListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.SlugField()
    name = serializers.CharField()
    short_description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    old_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        allow_null=True,
    )
    category = serializers.DictField()
    main_image = serializers.DictField(allow_null=True)
    average_rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        allow_null=True,
    )
    reviews_count = serializers.IntegerField()
    stock_status = serializers.CharField()
    url = serializers.CharField()


class ProductDetailSerializer(ProductListSerializer):
    sku = serializers.CharField()
    description = serializers.CharField()
    images = serializers.ListField()
    stock_quantity = serializers.IntegerField()
    is_available = serializers.BooleanField()
    related_products = serializers.ListField()
    web_url = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

Фактическая реализация может использовать ModelSerializer, но публичный набор полей должен соответствовать этому ADR.

Пример тестовых ожиданий
1. GET /api/products/ возвращает только активные неудалённые товары.
2. GET /api/products/ не возвращает товары из неактивных категорий.
3. GET /api/products/<slug>/ возвращает товар по slug.
4. GET /api/products/<id>/ не используется как публичный контракт.
5. Product list содержит id, slug, name, price, category, main_image, rating.
6. Product detail содержит расширенное описание, images, related_products.
7. Product detail не содержит полный список отзывов.
8. Product detail содержит average_rating и reviews_count.
9. Фильтр search работает по публичным полям товара.
10. Фильтр category принимает slug категории.
11. Фильтры min_price и max_price ограничивают цену.
12. Неподдерживаемый ordering возвращает 400 Bad Request.
13. Pagination возвращает count, next, previous, results.
14. main_image=null допустим, если у товара нет изображений.
15. Скрытый или soft-deleted товар по slug возвращает 404.
Примечание по будущему развитию

Если в будущем потребуется стабильный API lookup, не зависящий от изменения slug, можно будет добавить отдельный immutable public identifier.

Например:

public_id
uuid

Но на этапе MVP принимается правило:

slug является публичным lookup Product API.

Переход на другой lookup должен быть оформлен отдельным ADR, потому что это изменение публичного API-контракта.
