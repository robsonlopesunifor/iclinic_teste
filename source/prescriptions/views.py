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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_servece = {
            'clinic': {
                'path': 'clinics',
                'token': settings.CLINICS_TOKEN},
            'physician': {
                'path': 'physicians',
                'token': settings.PHYSICIAN_TOKEN},
            'patient': {
                'path': 'patients',
                'token': settings.PATIENTS_TOKEN},
        }

    @transaction.atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            response_metric = self._structure_metric_request(data)
            data = serializer.add_metric(response_metric)
            return Response(data, status=status.HTTP_200_OK)
        return Response({
            "error": {
                "message": "malformed request",
                "code": "01"}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _structure_metric_request(self, data):
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
        return response_metric

    def _consult_clinics_with_error_handling(self, data):
        _id = data['clinic']['id']
        try:
            return self._consult(_id, 'clinic')
        except requests.HTTPError:
            return {'clinic_id': _id}

    def _consult_physician_with_error_handling(self, data):
        _id = data['physician']['id']
        try:
            return self._consult(_id, 'physician')
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
        _id = data['patient']['id']
        try:
            return self._consult(_id, 'patient')
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

    def _consult(self, _id, _path):
        url = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path=self.path_servece[_path]['path'],
            id=_id)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(
                self.path_servece[_path]['token'])
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response = response.json()
        response = self._add_prefix(response, _path)
        return response

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

    @staticmethod
    def _add_prefix(_data, _prefix):
        _data['id'] = int(_data['id'])
        data_prefixo = {f'{_prefix}_{k}': v for k, v in _data.items()}
        return data_prefixo
