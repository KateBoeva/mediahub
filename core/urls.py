from django.urls import path

from api.views import LoginView, LogoutView, MediaListView, MediaRetrieveView, MediaCreateView, RegisterView

app_name = 'core'

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("media/", MediaListView.as_view(), name="media-list"),
    path("media/<int:media_id>/", MediaRetrieveView.as_view(), name="media-retrieve"),
    path("media/create/", MediaCreateView.as_view(), name="media-create"),
]