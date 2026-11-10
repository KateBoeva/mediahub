from django.urls import path

from api.views import (
    LoginView, LogoutView, MediaCreateView, MediaFileView, MediaListView, MediaRetrieveView, RegisterView,
)

app_name = 'core'

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("media/", MediaListView.as_view(), name="media-list"),
    path("media/<int:media_id>/", MediaRetrieveView.as_view(), name="media-retrieve"),
    path("media/<int:media_id>/file/", MediaFileView.as_view(), name="media-file"),
    path("media/create/", MediaCreateView.as_view(), name="media-create"),
]