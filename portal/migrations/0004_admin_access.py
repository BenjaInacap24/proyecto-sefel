from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0003_manual_projects'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_requests', models.BooleanField(default=False)),
                ('edit_requests', models.BooleanField(default=False)),
                ('decide_requests', models.BooleanField(default=False)),
                ('delete_requests', models.BooleanField(default=False)),
                ('view_progress_projects', models.BooleanField(default=False)),
                ('create_progress_project', models.BooleanField(default=False)),
                ('progress_add_update', models.BooleanField(default=False)),
                ('progress_upload_file', models.BooleanField(default=False)),
                ('progress_finish_project', models.BooleanField(default=False)),
                ('view_finished_projects', models.BooleanField(default=False)),
                ('finished_add_update', models.BooleanField(default=False)),
                ('finished_upload_file', models.BooleanField(default=False)),
                ('finished_send_portfolio', models.BooleanField(default=False)),
                ('finished_reopen_progress', models.BooleanField(default=False)),
                ('view_portfolio', models.BooleanField(default=False)),
                ('add_portfolio', models.BooleanField(default=False)),
                ('edit_portfolio', models.BooleanField(default=False)),
                ('delete_portfolio', models.BooleanField(default=False)),
                ('view_communications', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_access', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
