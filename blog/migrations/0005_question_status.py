# Generated by Django 2.1.1 on 2018-10-25 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20181024_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='status',
            field=models.CharField(choices=[('hidden', 'Oculto'), ('public', 'Público')], default='public', max_length=10),
        ),
    ]
