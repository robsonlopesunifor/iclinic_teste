from django.urls import path
from .views import PrescriptionsCreateAPIView


app_name = 'prescriptions'  # pylint: disable=C0103
urlpatterns = [
    path(
        'prescriptions',
        PrescriptionsCreateAPIView.as_view(),
        name="prescriptions"),
]
