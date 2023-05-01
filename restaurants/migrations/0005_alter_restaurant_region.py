# Generated by Django 3.2.18 on 2023-05-01 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0004_alter_restaurant_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='region',
            field=models.CharField(choices=[('서울', '서울'), ('부산', '부산'), ('대구', '대구'), ('인천', '인천'), ('광주', '광주'), ('대전', '대전'), ('울산', '울산'), ('세종', '세종'), ('경기도', '경기도'), ('강원도', '강원도'), ('충청북도', '충청북도'), ('충청남도', '충청남도'), ('전라북도', '전라북도'), ('전라남도', '전라남도'), ('경상북도', '경상북도'), ('경상남도', '경상남도'), ('제주도', '제주도')], max_length=20),
        ),
    ]