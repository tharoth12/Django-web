# Generated by Django 5.0 on 2025-02-24 20:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_author_remove_product_country_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='first_name',
            new_name='product_name',
        ),
        migrations.RemoveField(
            model_name='author',
            name='last_name',
        ),
    ]
