# Generated by Django 4.2.2 on 2023-06-21 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_pendingticket_recipients_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendingticket',
            name='mode',
            field=models.CharField(choices=[('single', 'Single'), ('multiple', 'Multiple')], max_length=25),
        ),
    ]
