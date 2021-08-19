import json
from urllib.parse import urlparse
from httmock import (urlmatch,
                     response,
                     HTTMock)
from django.test import TestCase
from django.conf import settings
from django.urls import reverse

RESPONSE_METRIC = {
    "clinic_id": 1,
    "clinic_name": "Kenneth Torp DDS",
    "physician_id": 1,
    "physician_name": "Wesley Marquardt",
    "physician_crm": "0bc31b08-04f2-4eb8-b1b4-fd52f21622f4",
    "patient_id": 1,
    "patient_email": "Danial.Kassulke59@hotmail.com",
    "patient_phone": "413-218-5913 x9333",
    "prescription_id": 26,
    "id": "1",
    "patient_name": "Boyd Crooks"
}


# Create your tests here.
class PrescriptionsCase(TestCase):

    def setUp(self):
        self.url = reverse('prescriptions:prescriptions')

        self.data = {
            "clinic": {"id": 1},
            "physician": {"id": 1},
            "patient": {"id": 1},
            "text": "Dipirona 1x ao dia"
        }

        self.data_return = {
            "data": {
                "id": 1,
                "clinic": {"id": 1},
                "physician": {"id": 1},
                "patient": {"id": 1},
                "text": "Dipirona 1x ao dia",
                "metric": {"id": 1}
            }
        }

    def test_correct_request(self):
        # requisição correta

        with HTTMock(metrics_mock):
            response_data = self.client.post(
                path=self.url,
                data=json.dumps(self.data),
                content_type='application/json')
        self.assertEqual(response_data.status_code, 200)
        self.assertEqual(response_data.json(), self.data_return)

    def test_malformed_request(self):
        # quando a estrutura da requisicao esta mal formada
        # erro 400 Bad Request
        # sem um dos campos
        incomplete_data = {
            "clinic": {"id": 1},
            "patient": {"id": 1},
            "text": "Dipirona 1x ao dia"
        }

        data_not_id = {
            "clinic": {"nn": 1},
            "physician": {"id": 1},
            "patient": {"id": 1},
            "text": "Dipirona 1x ao dia"
        }

        data_id_not_int = {
            "clinic": {"id": "1"},
            "physician": {"id": 1},
            "patient": {"id": 1},
            "text": "Dipirona 1x ao dia"
        }

        # dados incompleto
        response_data = self.client.post(
            path=self.url,
            data=json.dumps(incomplete_data),
            content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        resposta = response_data.json()
        self.assertEqual(resposta['error']['code'], '01')
        self.assertEqual(resposta['error']['message'], 'malformed request')

        # nao tem id
        response_data = self.client.post(
            path=self.url,
            data=json.dumps(data_not_id),
            content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        resposta = response_data.json()
        self.assertEqual(resposta['error']['code'], '01')
        self.assertEqual(resposta['error']['message'], 'malformed request')

        # id nao e inteiro
        response_data = self.client.post(
            path=self.url,
            data=json.dumps(data_id_not_int),
            content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        resposta = response_data.json()
        self.assertEqual(resposta['error']['code'], '01')
        self.assertEqual(resposta['error']['message'], 'malformed request')

    def test_physician_not_found(self):
        # quando o medico não foi encontrado
        # erro 404 Not found
        with HTTMock(physicians_404_mock):
            response_data = self.client.post(
                path=self.url,
                data=json.dumps(self.data),
                content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        # TODO: achar uma forma de não precisar converter
        # TODO: quando da erro e pra voutar no response_data.error ?
        resposta_content = json.loads(response_data.content)
        self.assertEqual(response_data.status_code, 500)
        self.assertEqual(resposta_content['error']['code'], '02')
        self.assertEqual(
            resposta_content['error']['message'],
            'physician not found')

    def test_patients_not_found(self):
        # quando o paciente não foi encontrado
        # erro 404 Not found
        with HTTMock(patients_404_mock):
            response_data = self.client.post(
                path=self.url,
                data=json.dumps(self.data),
                content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        # TODO: achar uma forma de não precisar converter
        resposta_content = json.loads(response_data.content)
        self.assertEqual(resposta_content['error']['code'], '03')
        self.assertEqual(
            resposta_content['error']['message'],
            'patient not found')

    def test_metrics_service_not_available(self):
        # quando nao e possivel acessar o servico de metrica
        # erro
        with HTTMock(metrics_not_available_mock):
            response_data = self.client.post(
                path=self.url,
                data=json.dumps(self.data),
                content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        resposta_content = json.loads(response_data.content)
        self.assertEqual(resposta_content['error']['code'], '04')
        self.assertEqual(
            resposta_content['error']['message'],
            'metrics service not available')

    def test_physicians_service_not_available(self):
        with HTTMock(physicians_not_available_mock):
            response_data = self.client.post(
                path=self.url,
                data=json.dumps(self.data),
                content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        resposta_content = json.loads(response_data.content)
        self.assertEqual(
            resposta_content['error']['code'],
            '05')
        self.assertEqual(
            resposta_content['error']['message'],
            'physicians service not available')

    def test_patients_service_not_available(self):
        with HTTMock(patients_not_available_mock):
            response_data = self.client.post(
                path=self.url,
                data=json.dumps(self.data),
                content_type='application/json')
        self.assertEqual(response_data.status_code, 500)
        resposta_content = json.loads(response_data.content)
        self.assertEqual(resposta_content['error']['code'], '06')
        self.assertEqual(
            resposta_content['error']['message'],
            'patients service not available')


DEPENDENT_SERVICE = urlparse(settings.DEPENDENT_SERVICE).netloc

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/clinics/', method='GET')
def clinics_404_mock(_, request):
    return response(
        404,
        content="404 not found",
        headers={},
        request=request)

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/physicians/', method='GET')
def physicians_404_mock(_, request):
    return response(
        404,
        content="404 not found",
        headers={},
        request=request)

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/patients/', method='GET')
def patients_404_mock(_, request):
    return response(
        404,
        content="404 not found",
        headers={},
        request=request)

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/physicians/', method='GET')
def physicians_not_available_mock(_, request):
    return response(
        503,
        content="503 Service Unavailable",
        headers={},
        request=request)

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/patients/', method='GET')
def patients_not_available_mock(_, request):
    return response(
        503,
        content="503 Service Unavailable",
        headers={},
        request=request)

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/metrics', method='POST')
def metrics_mock(_, request):
    return response(
        200,
        content=RESPONSE_METRIC,
        headers={},
        request=request)

@urlmatch(netloc=DEPENDENT_SERVICE, path=r'/v1/metrics', method='POST')
def metrics_not_available_mock(_, request):
    return response(
        503,
        content="503 Service Unavailable",
        headers={},
        request=request)
