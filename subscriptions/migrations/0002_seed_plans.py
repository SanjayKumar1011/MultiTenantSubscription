from django.db import migrations

def create_plans(apps, schema_editor):
    Plan = apps.get_model('subscriptions', 'Plan')

    Plan.objects.get_or_create(
        name='FREE',
        defaults={
            'price': 0,
            'max_users': 3,
            'max_projects': 2,
        }
    )

    Plan.objects.get_or_create(
        name='PRO',
        defaults={
            'price': 999,
            'max_users': 20,
            'max_projects': 50,
        }
    )

def reverse_plans(apps, schema_editor):
    Plan = apps.get_model('subscriptions', 'Plan')
    Plan.objects.filter(name__in=['FREE', 'PRO']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_plans, reverse_plans),
    ]
