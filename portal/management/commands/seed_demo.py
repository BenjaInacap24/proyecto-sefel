from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from portal.models import Category, ServiceRequest, ClientProject, PortfolioItem, ProgressUpdate
from django.db import connection

def ensure_sqlite_schema():
    if connection.vendor != 'sqlite': return
    q=connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute(f'PRAGMA table_info({q(ClientProject._meta.db_table)})')
        project_columns={row[1] for row in cursor.fetchall()}
        if 'finished_at' not in project_columns:
            cursor.execute(f'ALTER TABLE {q(ClientProject._meta.db_table)} ADD COLUMN {q("finished_at")} datetime NULL')
        cursor.execute(f'PRAGMA table_info({q(PortfolioItem._meta.db_table)})')
        portfolio_columns={row[1] for row in cursor.fetchall()}
        if 'source_project_id' not in portfolio_columns:
            cursor.execute(f'ALTER TABLE {q(PortfolioItem._meta.db_table)} ADD COLUMN {q("source_project_id")} integer NULL REFERENCES {q(ClientProject._meta.db_table)} ({q("id")})')
        cursor.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS {q("portal_portfolio_source_project_uniq")} ON {q(PortfolioItem._meta.db_table)} ({q("source_project_id")})')

class Command(BaseCommand):
    help = 'Crea contenido de demostración SEFEL para el prototipo local.'
    def handle(self,*args,**kwargs):
        if not settings.DEBUG:
            raise CommandError('seed_demo solo se puede ejecutar con DEBUG activo; no crea cuentas de demostración en producción.')
        ensure_sqlite_schema()
        user,created=get_user_model().objects.get_or_create(username='admin',defaults={'email':'demo@sefel.local','is_staff':True,'is_superuser':True})
        user.is_staff=True; user.is_superuser=True
        if created: user.set_password('sefel-demo')
        user.save()
        names=['Estructuras metálicas','Construcción y obras civiles','Mantenimiento mecánico','Mantenimiento eléctrico','Fabricación especial','Apoyo industrial','Otros']
        cats={n:Category.objects.get_or_create(name=n)[0] for n in names}
        samples=[('Pasarela metálica',names[0],'Referencia de estructura metálica y montaje.',True,0),('Galpón industrial',names[1],'Obras de edificación e infraestructura.',True,1),('Intervención de mecánica y piping',names[2],'Mantenimiento y modificaciones mecánicas.',False,2),('Carro de arrastre',names[4],'Fabricación especial a requerimiento.',True,3),('Obra de edificación',names[1],'Ejecución y mejoramiento de infraestructura.',False,4),('Servicio industrial',names[5],'Apoyo a la continuidad operativa.',False,5)]
        for i,(title,category,desc,featured,days) in enumerate(samples):
            PortfolioItem.objects.get_or_create(name=title,defaults={'category':cats[category],'description':desc,'date':date.today()-timedelta(days=days*90),'featured':featured})
        req,_=ServiceRequest.objects.get_or_create(rut='76.123.456-7',project_name='Montaje de estructura metálica',defaults={'applicant_type':'company','company_name':'Constructora Ejemplo SpA','contact_name':'Ana Pérez','email':'ana@ejemplo.cl','phone':'+56 9 1234 5678','channel':'email','service':names[0],'description':'Proyecto de ejemplo para mostrar el recorrido completo de seguimiento.','location':'Coelemu, Región de Ñuble','state':'confirmed'})
        project,_=ClientProject.objects.get_or_create(request=req,defaults={'name':req.project_name,'description':req.description,'code':'SFL9K4M2R8TZ'})
        if not project.updates.exists():
            ProgressUpdate.objects.create(project=project,description='Montaje de estructura principal: primer tramo completado.',created_at=timezone.now()-timedelta(days=2))
            ProgressUpdate.objects.create(project=project,description='Preparación del área de trabajo finalizada.',created_at=timezone.now()-timedelta(days=5))
        self.stdout.write(self.style.SUCCESS('Datos demo listos. Admin: admin / sefel-demo. Código de proyecto: SFL9K4M2R8TZ'))
