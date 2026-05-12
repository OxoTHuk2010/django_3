import pytest
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_product_image_can_be_created(product):
    """Изображение товара связывается с Product и хранит данные для отображения/SEO."""
    image = baker.make(
        "catalog.ProductImage",
        product=product,
        image="products/test.jpg",
        alt_text="Front view",
        is_main=True,
        sort_order=1,
    )

    assert image.id is not None
    assert image.product == product
    assert image.image.name == "products/test.jpg"
    assert image.alt_text == "Front view"
    assert image.is_main is True
    assert str(image).endswith(product.name)
