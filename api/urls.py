from django.urls import path, include

urlpatterns = [
    path("media/", include("api.views.media")),
]