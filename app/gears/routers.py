from django.conf.urls import url
from rest_framework_mongoengine import routers

from gears.views import GearViewSet

router = routers.DefaultRouter()
router.register(r'gears', GearViewSet)

urlpatterns = []

urlpatterns += router.urls