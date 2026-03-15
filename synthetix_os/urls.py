"""
URL configuration for synthetix_os project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'accounts': {
            'register':  reverse('register', request=request, format=format),
            'login':     reverse('login', request=request, format=format),
            'logout':    reverse('logout', request=request, format=format),
        },
    })



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/',include('accounts.urls')),
    path('api/agent/',include('agent.urls')),
    path('api/workflows/', include('workflows.urls')),
    path('api/events/', include('events.urls')),
    path('api/triggers/', include('triggers.urls')),
    path('api/integrations/', include('integrations.urls')),
    path('api/email/webhook/', include('triggers.email_urls')),

    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
