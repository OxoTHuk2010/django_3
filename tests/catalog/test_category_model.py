import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_category_can_be_created(category):
    """Категория создаётся с обязательными полями и человекочитаемым __str__."""
    assert category.id is not None
    assert category.name == "Notebooks"
    assert category.slug == "notebooks"
    assert str(category) == category.name


def test_category_defaults_to_active_and_not_deleted(category):
    """Новая категория по умолчанию активна и не помечена как удалённая."""
    assert category.is_active is True
    assert category.is_deleted is False
    assert category.deleted_at is None


def test_category_can_have_parent(category):
    """Категории поддерживают вложенность через parent."""
    child = baker.make(
        "catalog.Category",
        name="Ultrabooks",
        slug="ultrabooks",
        parent=category,
    )

    assert child.parent == category
    assert list(category.children.all()) == [child]


def test_category_slug_is_unique(category):
    """Slug категории должен быть уникальным, потому что используется в URL."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make("catalog.Category", name="Duplicate", slug=category.slug)


def test_category_soft_delete_and_restore(category):
    """Soft delete не удаляет категорию физически и позволяет восстановить запись."""
    category.soft_delete()
    category.refresh_from_db()

    assert category.is_deleted is True
    assert category.deleted_at is not None

    category.restore()
    category.refresh_from_db()

    assert category.is_deleted is False
    assert category.deleted_at is None
