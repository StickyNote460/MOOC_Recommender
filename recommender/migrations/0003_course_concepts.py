# Generated by Django 5.1.7 on 2025-04-11 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0002_alter_courseconcept_id_alter_usercourse_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='concepts',
            field=models.ManyToManyField(through='recommender.CourseConcept', to='recommender.concept'),
        ),
    ]
