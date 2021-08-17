import json
import requests
from django.db import transaction
from django.conf import settings
from rest_framework import generics
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import (permissions, status)
from prescriptions.serializers import PrescriptionsSerializer

# Create your views here.

class PrescriptionsCreateAPIView(generics.CreateAPIView):

    serializer_class = PrescriptionsSerializer
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            request_data_metric = {}
            request_data_metric.update(
                self._consult_clinics_with_error_handling(data))
            request_data_metric.update(
                self._consult_physician_with_error_handling(data))
            request_data_metric.update(
                self._consult_patient_with_error_handling(data))
            request_data_metric_json = json.dumps(request_data_metric)
            response_metric = self._consult_metrics_with_error_handling(
                request_data_metric_json)
            data = serializer.add_metric(response_metric)
            return Response(data, status=status.HTTP_200_OK)
        return Response({
            "error": {
                "message": "malformed request",
                "code": "01"}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _consult_clinics_with_error_handling(self, data):
        try:
            return self._consult_clinics(data['clinic']['id'])
        except requests.HTTPError:
            return {'clinic_id': id}

    def _consult_physician_with_error_handling(self, data):
        try:
            return self._consult_physician(data['physician']['id'])
        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                raise APIException(
                    {"error": {
                        "message": "physician not found", "code": "02"}})
            raise APIException(
                {"error": {
                    "message": "physicians service not available",
                    "code": "05"}})

    def _consult_patient_with_error_handling(self, data):
        try:
            return self._consult_patients(data['clinic']['id'])
        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                raise APIException({
                    "error": {
                        "message": "patient not found",
                        "code": "03"}})
            raise APIException({
                "error": {
                    "message": "patients service not available",
                    "code": "06"}})

    def _consult_metrics_with_error_handling(self, data):
        try:
            return self._consult_metrics(data)
        except requests.HTTPError:
            raise APIException({
                "error": {
                    'message': 'metrics service not available',
                    'code': '04'}})

    @staticmethod
    def _consult_clinics(_id):
        url_clinics = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='clinics',
            id=_id)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(settings.CLINICS_TOKEN)
        }
        response = requests.get(url_clinics, headers=headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dict['id'] = int(response_dict['id'])
        response_prefixo = {f'clinic_{k}': v for k, v in response_dict.items()}
        return response_prefixo

    @staticmethod
    def _consult_physician(_id):
        url_physicians = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='physicians',
            id=_id)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(settings.PHYSICIAN_TOKEN)
        }
        response = requests.get(url_physicians, headers=headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dict['id'] = int(response_dict['id'])
        response_prefixo = {
            f'physician_{k}': v for k, v in response_dict.items()}
        return response_prefixo

    @staticmethod
    def _consult_patients(_id):
        url_patients = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='patients',
            id=_id)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(settings.PATIENTS_TOKEN)
        }
        response = requests.get(url_patients, headers=headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dict['id'] = int(response_dict['id'])
        response_prefixo = {
            f'patient_{k}': v for k, v in response_dict.items()}
        return response_prefixo

    @staticmethod
    def _consult_metrics(_data):
        url_metrics = '{url}/{path}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='metrics')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(settings.METRICS_TOKEN)
        }
        response = requests.post(url_metrics, data=_data, headers=headers)
        response.raise_for_status()
        return response.json()
