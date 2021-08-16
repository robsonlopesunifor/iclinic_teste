from django.urls import path
from .views import PrescriptionsCreateAPIView


app_name = 'prescriptions'
urlpatterns = [
    path('prescriptions', PrescriptionsCreateAPIView.as_view(), name="prescriptions"),
]