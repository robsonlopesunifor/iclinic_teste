import json
import requests
import requests_cache
from requests.adapters import HTTPAdapter
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
        try:
            _id = data['clinic']['id']
            url = '{url}/clinics/{id}'.format(
                url=settings.DEPENDENT_SERVICE,
                id=_id)
            response = self._consult(
                url,
                settings.CLINICS_TOKEN,
                'get',
                timeout=settings.CLINICS_TIMEOUT,
                retry=settings.CLINICS_RETRY,
                cache_hours=settings.CLINICS_CACHE,
                cache_file='clinic')
            return self._add_prefix(response, 'clinic')
        except requests.HTTPError:
            return {'clinic_id': _id}

    def _consult_physician_with_error_handling(self, data):
        try:
            _id = data['physician']['id']
            url = '{url}/physicians/{id}'.format(
                url=settings.DEPENDENT_SERVICE,
                id=_id)
            response = self._consult(
                url,
                settings.PHYSICIAN_TOKEN,
                'get',
                timeout=settings.PHYSICIAN_TIMEOUT,
                retry=settings.PHYSICIAN_RETRY,
                cache_hours=settings.PHYSICIAN_CACHE,
                cache_file='physician')
            return self._add_prefix(response, 'physician')
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
            _id = data['patient']['id']
            url = '{url}/patients/{id}'.format(
                url=settings.DEPENDENT_SERVICE,
                id=_id)
            response = self._consult(
                url,
                settings.PATIENTS_TOKEN,
                'get',
                timeout=settings.PATIENTS_TIMEOUT,
                retry=settings.PATIENTS_RETRY,
                cache_hours=settings.PATIENTS_CACHE,
                cache_file='patient')
            return self._add_prefix(response, 'patient')
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

    def _consult_metrics_with_error_handling(self, _data):
        try:
            url = '{url}/metrics'.format(url=settings.DEPENDENT_SERVICE)
            response = self._consult(
                url,
                settings.METRICS_TOKEN,
                'post',
                data=_data,
                timeout=settings.METRICS_TIMEOUT,
                retry=settings.METRICS_RETRY,
                cache_file='metric',
                cache_hours=0)
            return response
        except requests.HTTPError:
            raise APIException({
                "error": {
                    'message': 'metrics service not available',
                    'code': '04'}})

    def _consult(self, _url, _token, _method, **_config):
        _data = _config.get('data', {})
        _timeout = _config.get('timeout', 0)
        _retry = _config.get('retry', 0)
        _cache_file = './cache/{}'.format(
            _config.get('cache_file', 'my_cache'))
        _cache_secundes = self._hours_to_seconds(
            _config.get('cache_hours', 0))
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(_token)
        }
        adapter = HTTPAdapter(max_retries=_retry)
        http = requests_cache.CachedSession(
            _cache_file, expire_after=_cache_secundes)
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        response = http.request(
            _method, _url, data=_data, headers=headers, timeout=_timeout)
        response.raise_for_status()
        response = response.json()
        return response

    @staticmethod
    def _add_prefix(_data, _prefix):
        _data['id'] = int(_data['id'])
        data_prefixo = {f'{_prefix}_{k}': v for k, v in _data.items()}
        return data_prefixo

    @staticmethod
    def _hours_to_seconds(_hours):
        return _hours * 60 * 60
