from django.urls import path, re_path
from api import views as api_views

urlpatterns = [
    path('upload/', api_views.new_image, name="upload"),
    re_path(r'^(?P<path>.*)/$', api_views.images, name="images_path"),
]
