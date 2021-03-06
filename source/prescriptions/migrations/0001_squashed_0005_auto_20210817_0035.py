# Generated by Django 2.2 on 2021-08-17 00:42

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('prescriptions', '0001_initial'), ('prescriptions', '0002_auto_20210815_2204'), ('prescriptions', '0003_prescriptionsmodel'), ('prescriptions', '0004_delete_prescriptions'), ('prescriptions', '0005_auto_20210817_0035')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prescriptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinic', django.contrib.postgres.fields.jsonb.JSONField()),
                ('physician', django.contrib.postgres.fields.jsonb.JSONField()),
                ('patient', django.contrib.postgres.fields.jsonb.JSONField()),
                ('text', models.CharField(max_length=80)),
            ],
        ),
    ]
