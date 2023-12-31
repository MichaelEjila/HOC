# Generated by Django 4.2.2 on 2023-06-20 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.CharField(default='Default description', help_text='Task Description', max_length=200, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('debit', 'Debit'), ('credit', 'Credit')], default='debit', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='card',
            name='type',
            field=models.CharField(choices=[('diamond', 'Diamond'), ('club', 'Club')], default='dynamic', max_length=25),
        ),
    ]
