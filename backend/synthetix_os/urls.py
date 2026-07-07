from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView



urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/system-admin/", include("system_admin.urls")),
    path('api/auth/',include('accounts.urls')),
    path('api/agent/',include('agent.urls')),
    path('api/workflows/', include('workflows.urls')),
    path('api/integrations/', include('integrations.urls')),
    path('api/email/webhook/', include('triggers.email_urls')),
    path('api/persona/', include('persona.urls')),
    path("api/dashboard/", include("dashboard.urls")),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


