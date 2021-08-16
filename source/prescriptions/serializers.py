from .models import Prescriptions
from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Field

class JSONSerializerField(Field):
    def to_internal_value(self, data):
        print('to_internal_value', data)
        return data
    def to_representation(self, value):
        print('to_representation', value)
        return value

class PrescriptionsSerializer(ModelSerializer):
    #clinic = JSONSerializerField()
    #physician = JSONSerializerField()
    #patient = JSONSerializerField()

    class Meta:
        model = Prescriptions
        read_only_fields = ('id',)
        fields = ('id', 'clinic', 'physician', 'patient', 'text', )

    def validate_clinic(self, value):
        return self._validate(value)

    def validate_physician(self, value):
        return self._validate(value)

    def validate_patient(self, value):
        return self._validate(value)

    def _validate(self, value):
        value = self._have_id_key(value)
        value = self._id_value_is_integer(value)
        return value

    @staticmethod
    def _have_id_key(value):
        if "id" not in value:
            raise ValidationError('Deve existir um dicionario com chave "id"')
        return value

    @staticmethod
    def _id_value_is_integer(value):
        if "id" in value and type(value['id']) != int:
            raise ValidationError('O valor do "id" tem que ser inteiro')
        return value