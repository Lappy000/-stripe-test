# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.CharField(blank=True, help_text='Имя файла изображения в папке img (например: smartwatch.jpg)', max_length=255, null=True, verbose_name='Изображение'),
        ),
    ]
