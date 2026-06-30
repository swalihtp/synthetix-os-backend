from rest_framework.routers import DefaultRouter
from .views import UserPersonaViewSet

router = DefaultRouter()
router.register('', UserPersonaViewSet, basename='persona')

urlpatterns = router.urls