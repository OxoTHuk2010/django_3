from django.conf import settings


def static_asset_version(request):
    """Передать версию статических ассетов для инвалидации браузерного кэша."""

    return {"STATIC_ASSET_VERSION": settings.STATIC_ASSET_VERSION}
