from django.urls import path

from api.views import MediaListView

urlpatterns = [
    path("media/", MediaListView.as_view(), name="media-list-create"),
]