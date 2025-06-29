# Generated by Django 5.0 on 2025-06-11 08:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_remove_rentalbooking_machine_size_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicerequest',
            options={'ordering': ['-submitted_at']},
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='actual_completion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='assigned_technician',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='estimated_completion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='final_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='onsite_fee',
            field=models.DecimalField(decimal_places=2, default=100.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='onsite_technician',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='preferred_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='service_type',
            field=models.CharField(default='Maintenance', help_text='Type of service (e.g., Maintenance, Repair, Installation)', max_length=100),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='customer_name',
            field=models.CharField(default='Anonymous', max_length=100),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='issue_description',
            field=models.TextField(default='No description provided'),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='machine_type',
            field=models.CharField(default='Generator', help_text='Type of machine (e.g., Generator, UPS)', max_length=100),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='phone',
            field=models.CharField(default='N/A', max_length=20),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='preferred_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
