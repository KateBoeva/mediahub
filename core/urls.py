from django.urls import path

from api.views import MediaListView, MediaRetrieveView, MediaCreateView

app_name = 'core'

urlpatterns = [
    path("media/", MediaListView.as_view(), name="media-list"),
    path("media/<int:media_id>/", MediaRetrieveView.as_view(), name="media-retrieve"),
    path("media/create/", MediaCreateView.as_view(), name="media-create"),
]