# Generated by Django 3.2.18 on 2023-05-07 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='region',
            field=models.CharField(choices=[('서울', '서울특별시'), ('경기도', '경기도'), ('인천', '인천광역시'), ('강원도', '강원도'), ('전라북도', '전라북도'), ('전라남도', '전라남도'), ('경상북도', '경상북도'), ('경상남도', '경상남도')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
