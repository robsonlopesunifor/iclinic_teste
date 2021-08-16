import requests
import json
from urllib.error import HTTPError
from django.shortcuts import render
from django.db import transaction
from django.conf import settings
from rest_framework import generics
from rest_framework.exceptions import APIException, ParseError
from rest_framework.response import Response
from rest_framework import (permissions, status)
from .serializers import PrescriptionsSerializer

# Create your views here.

class PrescriptionsCreateAPIView(generics.CreateAPIView):

    serializer_class = PrescriptionsSerializer
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def create(self, request):
        print('++++', request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            print('mmm', data)
            request_data_metric = {}
            request_data_metric.update(self._consult_clinics_with_error_handling(data))
            request_data_metric.update(self._consult_physician_with_error_handling(data))
            request_data_metric.update(self._consult_patient_with_error_handling(data))
            request_data_metric_json = json.dumps(request_data_metric)
            response_metric = self._consult_metrics_with_error_handling(request_data_metric_json)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": {"message": "malformed request", "code": "01"}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _consult_clinics_with_error_handling(self, data):
        try:
            return self._consult_clinics(data['clinic']['id'])
        except requests.HTTPError as exception:
            return {'clinic_id': id}

    def _consult_physician_with_error_handling(self, data):
        print('data>>', data)
        try:
            return self._consult_physician(data['physician']['id'])
        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                raise APIException({"error": {"message": "physician not found", "code": "02"}})
            raise APIException({"error": {"message": "physicians service not available", "code": "05"}})

    def _consult_patient_with_error_handling(self, data):
        try:
            return self._consult_patients(data['clinic']['id'])
        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                raise APIException({"error": {"message": "patient not found", "code": "03"}})
            raise APIException({"error": {"message": "patients service not available", "code": "06"}})

    def _consult_metrics_with_error_handling(self, data):
        try:
            return self._consult_metrics(data)
        except requests.HTTPError as exception:
            raise APIException({"error": {'message': 'metrics service not available', 'code': '04'}})

    def _consult_clinics(self, id):
        url_clinics = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='clinics',
            id=id)
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer {}'.format(settings.CLINICS_TOKEN)
        }
        response = requests.get(url_clinics, headers = headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dict['id'] = int(response_dict['id'])
        response_prefixo = {f'clinic_{k}': v for k, v in response_dict.items()}
        return response_prefixo

    def _consult_physician(self, id):
        url_physicians = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='physicians',
            id=id)
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer {}'.format(settings.PHYSICIAN_TOKEN)
        }
        response = requests.get(url_physicians, headers = headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dict['id'] = int(response_dict['id'])
        response_prefixo = {f'physician_{k}': v for k, v in response_dict.items()}
        return response_prefixo

    def _consult_patients(self, id):
        url_patients = '{url}/{path}/{id}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='patients',
            id=id)
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer {}'.format(settings.PATIENTS_TOKEN)
        }
        response = requests.get(url_patients, headers = headers)
        response.raise_for_status()
        response_dict = response.json()
        response_dict['id'] = int(response_dict['id'])
        response_prefixo = {f'patient_{k}': v for k, v in response_dict.items()}
        return response_prefixo

    def _consult_metrics(self, data):
        url_metrics = '{url}/{path}'.format(
            url=settings.DEPENDENT_SERVICE,
            path='metrics')
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer {}'.format(settings.METRICS_TOKEN)
        }
        response = requests.post(url_metrics, data = data, headers = headers)
        response.raise_for_status()
        return response.json()
