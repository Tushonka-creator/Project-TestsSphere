from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("secure-panel-93f1/", admin.site.urls),
    path("registration/", include("django.contrib.auth.urls")),
    path("", include("tests.urls")),
]
