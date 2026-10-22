import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('portal', '0002_client_profiles')]
    operations = [
        migrations.AlterField(
            model_name='clientproject', name='request',
            field=models.OneToOneField(blank=True, null=True, on_delete=models.deletion.PROTECT, related_name='project', to='portal.servicerequest'),
        ),
        migrations.AddField(model_name='clientproject', name='contact_name', field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name='clientproject', name='contact_company', field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name='clientproject', name='contact_email', field=models.EmailField(blank=True, max_length=254)),
        migrations.AddField(model_name='clientproject', name='contact_phone', field=models.CharField(blank=True, max_length=40)),
        migrations.AddField(model_name='clientproject', name='contact_channel', field=models.CharField(blank=True, choices=[('email', 'Correo'), ('phone', 'Teléfono')], max_length=10)),
    ]