from django.conf.urls import url
from django.urls import path
from rest_framework_mongoengine import routers

from accounts.views import AuthToken, Logout, CreateUser, UpdateUser

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^login$', AuthToken.as_view()),
    url(r'^logout$', Logout.as_view()),
    url(r'^users/signup$', CreateUser.as_view()),
    # ?P<username> is a part of url but will be accepted as a url parameter
    url(r'^users/(?P<username>\w+)$', UpdateUser.as_view()) 
    #url(r'users/', UpdateUser.as_view())
]

urlpatterns += router.urls