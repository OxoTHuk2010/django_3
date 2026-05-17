from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from django.http import HttpRequest

from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product

SESSION_CART_KEY = "cart"
MAX_CART_ITEM_QUANTITY = 99
ZERO_MONEY = Decimal("0.00")


@dataclass(frozen=True)
class CartItemSnapshot:
    """Нормализованная позиция корзины для шаблонов и checkout."""

    product: Product
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    is_available: bool
    availability_message: str | None = None


@dataclass(frozen=True)
class CartSnapshot:
    """Нормализованное состояние корзины после пересчёта актуальных товаров."""

    items: list[CartItemSnapshot] = field(default_factory=list)
    total_quantity: int = 0
    total_price: Decimal = ZERO_MONEY
    available_total_price: Decimal = ZERO_MONEY
    is_empty: bool = True
    has_unavailable_items: bool = False
    can_checkout: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CartOperationResult:
    """Результат операции корзины с сообщением для web-слоя."""

    success: bool
    message: str
    errors: list[str] = field(default_factory=list)
    snapshot: CartSnapshot | None = None


def get_cart_snapshot(request: HttpRequest) -> CartSnapshot:
    """Вернуть актуальное состояние корзины для текущего пользователя."""

    if _should_use_db_cart(request):
        return _build_db_cart_snapshot(request)

    return _build_session_cart_snapshot(request)


def add_to_cart(
    request: HttpRequest,
    product: Product,
    quantity: int,
) -> CartOperationResult:
    """Добавить товар в корзину или увеличить количество существующей позиции."""

    return _change_cart_item_quantity(
        request=request,
        product=product,
        quantity=quantity,
        mode="add",
    )


def update_cart_item(
    request: HttpRequest,
    product: Product,
    quantity: int,
) -> CartOperationResult:
    """Заменить количество товара в корзине."""

    return _change_cart_item_quantity(
        request=request,
        product=product,
        quantity=quantity,
        mode="update",
    )


def remove_from_cart(
    request: HttpRequest,
    product: Product,
) -> CartOperationResult:
    """Удалить товар из корзины текущего пользователя."""

    if _should_use_db_cart(request):
        cart = _get_or_create_db_cart(request.user)
        CartItem.objects.filter(cart=cart, product=product).delete()
    else:
        session_cart = _get_session_cart(request)
        session_cart.pop(str(product.id), None)
        _save_session_cart(request, session_cart)

    return CartOperationResult(
        success=True,
        message="Товар удалён из корзины.",
        snapshot=get_cart_snapshot(request),
    )


def clear_cart(request: HttpRequest) -> CartOperationResult:
    """Полностью очистить корзину текущего пользователя."""

    if _should_use_db_cart(request):
        cart = _get_or_create_db_cart(request.user)
        cart.items.all().delete()
    else:
        _save_session_cart(request, {})

    return CartOperationResult(
        success=True,
        message="Корзина очищена.",
        snapshot=get_cart_snapshot(request),
    )


def merge_session_cart_to_user_cart(
    request: HttpRequest,
    user,
) -> CartOperationResult:
    """Объединить гостевую session-cart с постоянной DB-корзиной пользователя."""

    session_cart = _get_session_cart(request)

    if not session_cart:
        return CartOperationResult(
            success=True,
            message="Гостевая корзина пуста.",
            snapshot=_build_db_cart_snapshot_for_user(user),
        )

    cart = _get_or_create_db_cart(user)
    product_map = _get_product_map(session_cart)

    for raw_product_id, raw_quantity in session_cart.items():
        product = product_map.get(_parse_product_id(raw_product_id))
        quantity = _parse_quantity(raw_quantity)

        if product is None or quantity < 1 or not _is_product_visible(product):
            continue

        if product.stock_quantity < 1:
            continue

        item = CartItem.objects.filter(cart=cart, product=product).first()
        current_quantity = item.quantity if item else 0
        target_quantity = min(
            current_quantity + quantity,
            product.stock_quantity,
            MAX_CART_ITEM_QUANTITY,
        )
        if target_quantity < 1:
            continue

        if item is None:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=target_quantity,
            )
        else:
            item.quantity = target_quantity
            item.save(update_fields=["quantity", "updated_at"])

    _save_session_cart(request, {})

    return CartOperationResult(
        success=True,
        message="Гостевая корзина объединена с корзиной пользователя.",
        snapshot=_build_db_cart_snapshot_for_user(user),
    )


def _change_cart_item_quantity(
    request: HttpRequest,
    product: Product,
    quantity: int,
    mode: str,
) -> CartOperationResult:
    if quantity < 1:
        return _error_result(request, "Количество должно быть больше нуля.", "quantity_lt_1")

    if not _is_product_visible(product):
        return _error_result(request, "Товар недоступен для покупки.", "product_unavailable")

    current_quantity = _get_current_quantity(request, product)
    target_quantity = current_quantity + quantity if mode == "add" else quantity

    validation_error = _validate_target_quantity(product, target_quantity)
    if validation_error is not None:
        message, code = validation_error
        return _error_result(request, message, code)

    if _should_use_db_cart(request):
        _set_db_cart_item_quantity(request, product, target_quantity)
    else:
        session_cart = _get_session_cart(request)
        session_cart[str(product.id)] = target_quantity
        _save_session_cart(request, session_cart)

    message = "Товар добавлен в корзину." if mode == "add" else "Количество обновлено."
    return CartOperationResult(
        success=True,
        message=message,
        snapshot=get_cart_snapshot(request),
    )


def _validate_target_quantity(product: Product, quantity: int) -> tuple[str, str] | None:
    if quantity > MAX_CART_ITEM_QUANTITY:
        return (
            f"В одной позиции корзины может быть не больше {MAX_CART_ITEM_QUANTITY} шт.",
            "quantity_gt_max",
        )

    if quantity > product.stock_quantity:
        return ("Недостаточно товара на складе.", "quantity_gt_stock")

    return None


def _error_result(
    request: HttpRequest,
    message: str,
    code: str,
) -> CartOperationResult:
    return CartOperationResult(
        success=False,
        message=message,
        errors=[code],
        snapshot=get_cart_snapshot(request),
    )


def _build_session_cart_snapshot(request: HttpRequest) -> CartSnapshot:
    session_cart = _get_session_cart(request)
    product_map = _get_product_map(session_cart)
    normalized_cart: dict[str, int] = {}
    items: list[CartItemSnapshot] = []
    warnings: list[str] = []
    removed_items_count = 0

    for raw_product_id, raw_quantity in session_cart.items():
        product_id = _parse_product_id(raw_product_id)
        quantity = _parse_quantity(raw_quantity)
        product = product_map.get(product_id)

        if product is None or quantity < 1 or not _is_product_visible(product):
            removed_items_count += 1
            continue

        normalized_cart[str(product.id)] = quantity
        item_snapshot = _build_item_snapshot(product, quantity)
        items.append(item_snapshot)

    if removed_items_count:
        warnings.append("Некоторые товары удалены из корзины, потому что больше недоступны.")

    snapshot = _build_snapshot(items=items, warnings=warnings)

    if normalized_cart != session_cart:
        _save_session_cart(request, normalized_cart)

    return snapshot


def _build_db_cart_snapshot(request: HttpRequest) -> CartSnapshot:
    return _build_db_cart_snapshot_for_user(request.user)


def _build_db_cart_snapshot_for_user(user) -> CartSnapshot:
    cart = _get_or_create_db_cart(user)
    items: list[CartItemSnapshot] = []
    warnings: list[str] = []
    removed_items_count = 0

    for cart_item in cart.items.select_related("product__category"):
        product = cart_item.product
        if not _is_product_visible(product):
            cart_item.delete()
            removed_items_count += 1
            continue

        items.append(_build_item_snapshot(product, cart_item.quantity))

    if removed_items_count:
        warnings.append("Некоторые товары удалены из корзины, потому что больше недоступны.")

    return _build_snapshot(items=items, warnings=warnings)


def _build_item_snapshot(product: Product, quantity: int) -> CartItemSnapshot:
    availability_message = None
    is_available = True

    if product.stock_quantity < 1:
        is_available = False
        availability_message = "Нет в наличии."
    elif quantity > product.stock_quantity:
        is_available = False
        availability_message = "Количество превышает доступный остаток."
    elif quantity > MAX_CART_ITEM_QUANTITY:
        is_available = False
        availability_message = "Количество превышает системный лимит позиции."

    return CartItemSnapshot(
        product=product,
        quantity=quantity,
        unit_price=product.price,
        total_price=product.price * quantity,
        is_available=is_available,
        availability_message=availability_message,
    )


def _build_snapshot(
    items: list[CartItemSnapshot],
    warnings: list[str],
) -> CartSnapshot:
    for item in items:
        if item.availability_message:
            warnings.append(f"{item.product.name}: {item.availability_message}")

    total_quantity = sum(item.quantity for item in items)
    total_price = sum((item.total_price for item in items), ZERO_MONEY)
    available_total_price = sum(
        (item.total_price for item in items if item.is_available),
        ZERO_MONEY,
    )
    has_unavailable_items = any(not item.is_available for item in items)
    is_empty = len(items) == 0

    return CartSnapshot(
        items=items,
        total_quantity=total_quantity,
        total_price=total_price,
        available_total_price=available_total_price,
        is_empty=is_empty,
        has_unavailable_items=has_unavailable_items,
        can_checkout=not is_empty and not has_unavailable_items,
        warnings=warnings,
    )


def _get_current_quantity(request: HttpRequest, product: Product) -> int:
    if _should_use_db_cart(request):
        cart = _get_or_create_db_cart(request.user)
        item = CartItem.objects.filter(cart=cart, product=product).first()
        return item.quantity if item else 0

    return _parse_quantity(_get_session_cart(request).get(str(product.id), 0))


def _set_db_cart_item_quantity(
    request: HttpRequest,
    product: Product,
    quantity: int,
) -> None:
    cart = _get_or_create_db_cart(request.user)
    item, _created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )
    if item.quantity != quantity:
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])


def _get_or_create_db_cart(user) -> Cart:
    cart, _created = Cart.objects.get_or_create(user=user)
    return cart


def _get_session_cart(request: HttpRequest) -> dict[str, int]:
    raw_cart = request.session.get(SESSION_CART_KEY, {})
    if not isinstance(raw_cart, dict):
        return {}

    return dict(raw_cart)


def _save_session_cart(request: HttpRequest, cart_data: dict[str, int]) -> None:
    if cart_data:
        request.session[SESSION_CART_KEY] = cart_data
    else:
        request.session.pop(SESSION_CART_KEY, None)
    request.session.modified = True


def _get_product_map(session_cart: dict[str, int]) -> dict[int, Product]:
    product_ids = [product_id for raw_product_id in session_cart if (product_id := _parse_product_id(raw_product_id)) is not None]

    return Product.objects.select_related("category").in_bulk(product_ids)


def _parse_product_id(raw_product_id) -> int | None:
    try:
        return int(raw_product_id)
    except (TypeError, ValueError):
        return None


def _parse_quantity(raw_quantity) -> int:
    try:
        return int(raw_quantity)
    except (TypeError, ValueError):
        return 0


def _is_product_visible(product: Product) -> bool:
    return product.is_active and not product.is_deleted and product.category.is_active and not product.category.is_deleted


def _should_use_db_cart(request: HttpRequest) -> bool:
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated)
