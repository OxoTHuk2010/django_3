# Модель данных

## Назначение

Документ описывает целевую модель данных MyShop. Текущий прогресс реализации и незакрытые пункты ведутся отдельно в `docs/roadmap.md`.

## Общие базовые модели

### TimeStampedModel

Абстрактная модель для временных меток:

- `created_at` — дата создания;
- `updated_at` — дата последнего обновления.

Используется как базовый класс для доменных сущностей.

### ActiveModel

Абстрактная модель для признака активности:

- `is_active`.

Используется для сущностей, которые можно временно отключить без удаления.

### SoftDeleteModel

Абстрактная модель для мягкого удаления. По ADR `0006-soft-delete.md` используется ограниченно и не входит в `TimeStampedModel`.

- `is_deleted`;
- `deleted_at`.

На текущем этапе `SoftDeleteModel` разрешён только для:

- `catalog.Category`;
- `catalog.Product`.

Публичные selectors каталога должны исключать записи с `is_deleted=True`.

## Users

### User

Кастомная модель пользователя.

Поля:

- `email`;
- `phone`;
- `first_name`;
- `last_name`;
- стандартные поля `AbstractUser`.

Планируемое правило: email используется как основной идентификатор входа.

## Catalog

### Category

Категория товаров.

Поля:

- `name`;
- `slug`;
- `description`;
- `parent` для вложенных категорий;
- `is_active`;
- `is_deleted`;
- `deleted_at`;
- `created_at`;
- `updated_at`.

Правила:

- `slug` уникален;
- категории сортируются по названию;
- неактивные категории не отображаются в публичном каталоге.

### Product

Товар.

Поля:

- `category`;
- `name`;
- `slug`;
- `description`;
- `price`;
- `old_price` при необходимости;
- `stock` или `stock_quantity`;
- `sku`;
- `is_active`;
- `is_deleted`;
- `deleted_at`;
- `created_at`;
- `updated_at`.

Правила:

- `slug` уникален;
- `sku` уникален;
- цена не может быть отрицательной;
- остаток не может быть отрицательным;
- товар доступен, если активен, не удалён через soft delete и остаток больше нуля.

### ProductImage

Изображение товара.

Поля:

- `product`;
- `image`;
- `alt_text`;
- `is_main`;
- `sort_order`.

## Cart

Корзина использует гибридный подход из ADR `0002-session-cart.md`.

Для неавторизованного пользователя:

- корзина хранится в session;
- в session хранится только `product_id` и `quantity`;
- цена, название, активность товара и остаток не хранятся в session.

Для авторизованного пользователя:

- `Cart` связан с пользователем;
- `CartItem` связан с корзиной и товаром;
- пара `cart + product` уникальна;
- количество позиции положительное.

После логина гостевая session-cart должна объединяться с DB-корзиной пользователя.

Корзина не хранит snapshot цены. Snapshot цены и названия товара сохраняется только в `OrderItem` при создании заказа.

## Orders

### Order

Заказ пользователя.

Поля:

- `user`;
- `status`;
- `customer_name`;
- `customer_email`;
- `customer_phone`;
- `delivery_address`;
- `total_price`;
- `comment`;
- `created_at`;
- `updated_at`.

Статусы:

- `new`;
- `paid`;
- `processing`;
- `shipped`;
- `completed`;
- `cancelled`.

### OrderItem

Позиция заказа.

Поля:

- `order`;
- `product`;
- `product_name`;
- `price`;
- `quantity`.

`product_name` и `price` являются snapshot-данными на момент оформления заказа. Старые заказы не должны изменяться при изменении товара.

## Reviews

### Review

Отзыв пользователя о товаре.

Поля:

- `user`;
- `product`;
- `rating`;
- `title`;
- `text`;
- `status`;
- `is_verified_purchase`;
- `moderated_at`;
- `moderation_comment`.

Правила:

- рейтинг находится в диапазоне от 1 до 5;
- один пользователь может оставить один отзыв на один товар;
- опубликованные отзывы отображаются в карточке товара.

## Payments

### Payment

Платёж по заказу.

Поля:

- `order`;
- `status`;
- `method`;
- `amount`;
- `currency`;
- `provider`;
- `provider_payment_id`;
- `paid_at`;
- `failure_reason`.

Правила:

- сумма платежа не может быть отрицательной;
- платёж не хранит данные банковской карты, CVV или секретные данные провайдера;
- для MVP может использоваться mock-провайдер.

## Карта связей

```text
User 1 -> N Order
Order 1 -> N OrderItem
Product 1 -> N OrderItem
Category 1 -> N Product
Product 1 -> N ProductImage
User 1 -> N Review
Product 1 -> N Review
Order 1 -> N Payment
```

User 1 -> 1 Cart
Cart 1 -> N CartItem
Product 1 -> N CartItem
