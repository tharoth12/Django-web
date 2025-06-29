# Generated by Django 5.0 on 2025-06-09 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_product_additional_image_1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='additional_image_1',
        ),
        migrations.RemoveField(
            model_name='product',
            name='additional_image_2',
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/additional/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.product')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
