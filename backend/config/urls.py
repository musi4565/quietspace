from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/places/", include("apps.places.urls")),
    path("api/favorites/", include("apps.favorites.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/rankings/", include("apps.rankings.urls")),
    path("api/ai/", include("apps.ai.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/telegram/", include("apps.telegram.urls")),
    path("api/panel/", include("apps.panel.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
