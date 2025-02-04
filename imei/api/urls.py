from django.urls import path, include

from api.views import IMEIView


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path("check-imei", IMEIView.as_view(), name="check-imei")
]
