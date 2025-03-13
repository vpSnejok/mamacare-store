from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from accounts.views import DatabaseConnectionCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


    path('api/auth/', include('accounts.urls')),

    path('check-db-connection/', DatabaseConnectionCheckView.as_view(), name='check-db-connection'),
]
