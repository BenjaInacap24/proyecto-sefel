import secrets, string
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

def make_confirmation_token(): return secrets.token_urlsafe(24)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class ClientProfile(models.Model):
    """Customer account details attached to Django's authenticated user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')
    rut = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.company_name or self.user.get_full_name() or self.user.username

class ServiceRequest(models.Model):
    STATES = [('pending','Pendiente de confirmación'),('confirmed','Confirmada'),('rejected','Rechazada')]
    TYPES = [('personal','Personal'),('company','Empresa')]
    CHANNELS = [('email','Correo'),('phone','Teléfono')]
    client = models.ForeignKey(ClientProfile, related_name='service_requests', on_delete=models.SET_NULL, null=True, blank=True)
    applicant_type = models.CharField(max_length=12, choices=TYPES)
    rut = models.CharField(max_length=20)
    company_name = models.CharField(max_length=160, blank=True)
    contact_name = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    channel = models.CharField(max_length=10, choices=CHANNELS)
    service = models.CharField(max_length=120)
    project_name = models.CharField(max_length=180)
    description = models.TextField()
    location = models.CharField(max_length=180, blank=True)
    state = models.CharField(max_length=12, choices=STATES, default='pending')
    confirmation_token = models.CharField(max_length=64, unique=True, default=make_confirmation_token)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return f'{self.project_name} ({self.get_state_display()})'

class RequestFile(models.Model):
    request = models.ForeignKey(ServiceRequest, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='requests/', validators=[FileExtensionValidator(['pdf','png','jpg','jpeg','doc','docx','xls','xlsx'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ClientProject(models.Model):
    STATES = [('progress','En progreso'),('finished','Terminado')]
    CONTACT_CHANNELS = [('email','Correo'),('phone','Teléfono')]
    request = models.OneToOneField(ServiceRequest, related_name='project', on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField(max_length=16, unique=True, blank=True)
    name = models.CharField(max_length=180)
    description = models.TextField()
    contact_name = models.CharField(max_length=160, blank=True)
    contact_company = models.CharField(max_length=160, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_channel = models.CharField(max_length=10, choices=CONTACT_CHANNELS, blank=True)
    state = models.CharField(max_length=12, choices=STATES, default='progress')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    def save(self,*args,**kwargs):
        if not self.code:
            alphabet=string.ascii_uppercase+string.digits
            while True:
                code='SFL'+''.join(secrets.choice(alphabet) for _ in range(10))
                if not ClientProject.objects.filter(code=code).exists(): self.code=code; break
        super().save(*args,**kwargs)
    def __str__(self): return f'{self.code} · {self.name}'

class ProjectFile(models.Model):
    project = models.ForeignKey(ClientProject, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='projects/', validators=[FileExtensionValidator(['pdf','png','jpg','jpeg','doc','docx','xls','xlsx'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ProgressUpdate(models.Model):
    project = models.ForeignKey(ClientProject, related_name='updates', on_delete=models.CASCADE)
    description = models.TextField()
    photo = models.ImageField(upload_to='updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']

class PortfolioItem(models.Model):
    source_project = models.OneToOneField(ClientProject, related_name='portfolio_item', on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    description = models.TextField()
    date = models.DateField()
    photo = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    def __str__(self): return self.name

class Notification(models.Model):
    channel = models.CharField(max_length=40, default='Demo local')
    recipient = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

class AdminAccess(models.Model):
    """Granular capabilities for staff accounts; superusers always retain full access."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_access')
    view_requests = models.BooleanField(default=False)
    edit_requests = models.BooleanField(default=False)
    decide_requests = models.BooleanField(default=False)
    delete_requests = models.BooleanField(default=False)
    view_progress_projects = models.BooleanField(default=False)
    create_progress_project = models.BooleanField(default=False)
    progress_add_update = models.BooleanField(default=False)
    progress_upload_file = models.BooleanField(default=False)
    progress_finish_project = models.BooleanField(default=False)
    view_finished_projects = models.BooleanField(default=False)
    finished_add_update = models.BooleanField(default=False)
    finished_upload_file = models.BooleanField(default=False)
    finished_send_portfolio = models.BooleanField(default=False)
    finished_reopen_progress = models.BooleanField(default=False)
    view_portfolio = models.BooleanField(default=False)
    add_portfolio = models.BooleanField(default=False)
    edit_portfolio = models.BooleanField(default=False)
    delete_portfolio = models.BooleanField(default=False)
    view_communications = models.BooleanField(default=False)

    @property
    def active_permissions_count(self):
        return sum(bool(getattr(self, field.name)) for field in self._meta.fields if isinstance(field, models.BooleanField))

    def __str__(self): return f'Permisos de {self.user.get_username()}'
