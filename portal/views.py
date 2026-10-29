import secrets
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import AdminAccess, Category, ServiceRequest, RequestFile, ClientProject, ProjectFile, ProgressUpdate, PortfolioItem, Notification

SERVICES=['Estructuras metálicas','Construcción y obras civiles','Mantenimiento mecánico','Mantenimiento eléctrico','Fabricación especial','Apoyo industrial','Otros']
ADMIN_PERMISSION_GROUPS=[
    ('Solicitudes', [('view_requests','Ver solicitudes'),('edit_requests','Editar antecedentes'),('decide_requests','Aceptar o rechazar'),('delete_requests','Eliminar solicitudes pendientes')]),
    ('Proyectos en progreso', [('view_progress_projects','Ver y gestionar proyectos'),('create_progress_project','Crear proyectos manualmente'),('progress_add_update','Registrar avances'),('progress_upload_file','Subir o eliminar archivos'),('progress_finish_project','Marcar como terminado')]),
    ('Proyectos terminados', [('view_finished_projects','Ver y gestionar proyectos'),('finished_add_update','Registrar avances'),('finished_upload_file','Subir o eliminar archivos'),('finished_send_portfolio','Enviar al portafolio'),('finished_reopen_progress','Regresar a progreso')]),
    ('Portafolio', [('view_portfolio','Ver portafolio'),('add_portfolio','Añadir proyecto'),('edit_portfolio','Editar o publicar/retirar'),('delete_portfolio','Eliminar proyectos')]),
    ('Comunicaciones', [('view_communications','Ver comunicaciones registradas')]),
]
def has_admin_access(user,permission):
    if user.is_superuser: return True
    access=AdminAccess.objects.filter(user=user).first()
    return bool(access and getattr(access,permission,False))
def staff_required(request,permission=None):
    if not request.user.is_authenticated or not request.user.is_staff: return redirect('signin')
    if request.user.is_superuser: return None
    if permission and has_admin_access(request.user,permission): return None
    messages.error(request,'Tu cuenta no tiene permiso para realizar esa acción.')
    return redirect('dashboard')
def superuser_required(request):
    if not request.user.is_authenticated or not request.user.is_superuser: return redirect('signin')
def home(request):
    all_items=list(PortfolioItem.objects.filter(published=True).select_related('category').order_by('-date')[:6])
    featured=list(PortfolioItem.objects.filter(published=True,featured=True).select_related('category').order_by('-date')[:5])
    projects=featured or all_items
    # Keep every carousel page full when another published project is available.
    if len(projects)%2 and len(all_items)>len(projects):
        projects.append(next(item for item in all_items if item not in projects))
    carousel_pages=[projects[i:i+2] for i in range(0,len(projects),2)]
    return render(request,'home.html',{'carousel_pages':carousel_pages})
def about(request): return render(request,'about.html')
def services(request): return render(request,'services.html',{'services':SERVICES})
def portfolio(request):
    cats=Category.objects.all(); selected=request.GET.get('categoria',''); items=PortfolioItem.objects.filter(published=True).select_related('category').order_by('-date')
    recent=PortfolioItem.objects.filter(published=True).select_related('category').order_by('-date')
    if selected.isdigit(): items=items.filter(category_id=int(selected))
    if selected.isdigit(): recent=recent.exclude(category_id=int(selected))
    latest=[(c,PortfolioItem.objects.filter(category=c,published=True).order_by('-date').first()) for c in cats]
    return render(request,'portfolio.html',{'categories':cats,'items':items,'recent':recent[:6],'selected':selected,'latest':[(c,p) for c,p in latest if p]})
def request_service(request):
    applicant_type=request.POST.get('applicant_type','') if request.method=='POST' else request.GET.get('tipo','')
    if request.method!='POST' and applicant_type not in ['personal','company']:
        return render(request,'request_type.html')
    if request.method=='POST':
        d=request.POST; errors=[]
        if applicant_type not in ['personal','company']: errors.append('Selecciona si solicitas como Persona o Empresa.')
        if not all(d.get(k,'').strip() for k in ['applicant_type','rut','contact_name','service','project_name','description','channel']): errors.append('Completa los campos obligatorios.')
        if applicant_type=='company' and not d.get('company_name','').strip(): errors.append('La razón social es obligatoria para empresas.')
        try:
            if d.get('channel')=='email': validate_email(d.get('email',''))
            elif not d.get('phone','').strip(): errors.append('Ingresa un teléfono de contacto.')
        except ValidationError: errors.append('Ingresa un correo válido.')
        files=request.FILES.getlist('files')
        if len(files)>5: errors.append('Máximo 5 archivos.')
        for f in files:
            if f.size>10*1024*1024: errors.append(f'{f.name} supera 10 MB.')
            if f.name.rsplit('.',1)[-1].lower() not in ['pdf','png','jpg','jpeg','doc','docx','xls','xlsx']: errors.append(f'Tipo no permitido: {f.name}.')
        if not errors:
            obj=ServiceRequest.objects.create(applicant_type=applicant_type,rut=d['rut'],company_name=d.get('company_name',''),contact_name=d['contact_name'],email=d.get('email',''),phone=d.get('phone',''),channel=d['channel'],service=d['service'],project_name=d['project_name'],description=d['description'],location=d.get('location',''))
            for f in files: RequestFile.objects.create(request=obj,file=f)
            url=request.build_absolute_uri(f'/confirmar/{obj.confirmation_token}/')
            Notification.objects.create(channel='Demo local',recipient=obj.email if obj.channel=='email' else obj.phone,message=f'Confirma la solicitud {obj.pk}: {url}')
            return render(request,'request_sent.html',{'item':obj,'confirmation_url':url})
        for e in errors: messages.error(request,e)
    return render(request,'request_form.html',{'services':SERVICES,'applicant_type':applicant_type})
def confirm_request(request,token):
    item=get_object_or_404(ServiceRequest,confirmation_token=token)
    if item.state=='pending':
        item.state='confirmed'; item.save(update_fields=['state']); Notification.objects.create(recipient='SEFEL',message=f'Solicitud confirmada: {item.project_name}')
        messages.success(request,'Solicitud confirmada. SEFEL ya puede revisarla.')
    return redirect('home')
def lookup(request):
    code=request.GET.get('codigo','').strip().upper(); project=ClientProject.objects.filter(code=code).select_related('request').first() if code else None
    return render(request,'lookup.html',{'project':project,'searched':bool(code)})
def signin(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method=='POST':
        user=authenticate(request,username=request.POST.get('username',''),password=request.POST.get('password',''))
        if user and user.is_staff: login(request,user); return redirect('dashboard')
        messages.error(request,'Usuario o contraseña incorrectos.')
    return render(request,'signin.html',{'show_demo_credentials':settings.DEBUG})
def signout(request): logout(request); return redirect('home')
def dashboard(request):
    denied=staff_required(request)
    if denied: return denied
    permissions={field:has_admin_access(request.user,field) for _,group in ADMIN_PERMISSION_GROUPS for field,_ in group}
    tabs=[('solicitudes','view_requests'),('progreso','view_progress_projects'),('terminados','view_finished_projects'),('portafolio','view_portfolio'),('avisos','view_communications')]
    available=[name for name,permission in tabs if permissions[permission]]
    tab=request.GET.get('vista','')
    if tab not in available: tab=available[0] if available else ''
    requests=ServiceRequest.objects.exclude(state='rejected').filter(project__isnull=True).order_by('-created_at') if permissions['view_requests'] else ServiceRequest.objects.none()
    if tab=='progreso': projects=ClientProject.objects.filter(state='progress').select_related('request').order_by('-created_at')
    elif tab=='terminados': projects=ClientProject.objects.filter(state='finished').select_related('request').order_by('-created_at')
    else: projects=None
    return render(request,'dashboard.html',{'tab':tab,'request_count':requests.count(),'requests':requests,'projects':projects,'items':PortfolioItem.objects.order_by('-date') if permissions['view_portfolio'] else PortfolioItem.objects.none(),'notifications':Notification.objects.order_by('-created_at')[:20] if permissions['view_communications'] else Notification.objects.none(),'permissions':permissions,'is_superuser':request.user.is_superuser})
def admin_accounts(request):
    if superuser_required(request): return redirect('signin')
    User=get_user_model()
    accounts=User.objects.filter(is_staff=True,is_superuser=False).order_by('username')
    return render(request,'admin_accounts.html',{'accounts':accounts})
def admin_account_form(request,pk=None):
    if superuser_required(request): return redirect('signin')
    User=get_user_model()
    account=User.objects.filter(pk=pk,is_staff=True,is_superuser=False).first() if pk else None
    if pk and not account: raise Http404
    access=AdminAccess.objects.filter(user=account).first() if account else None
    errors=[]
    if request.method=='POST':
        data=request.POST
        username=data.get('username','').strip(); email=data.get('email','').strip()
        first_name=data.get('first_name','').strip(); last_name=data.get('last_name','').strip(); password=data.get('password','')
        if not username: errors.append('El nombre de usuario es obligatorio.')
        if User.objects.filter(username=username).exclude(pk=account.pk if account else None).exists(): errors.append('Ese nombre de usuario ya está ocupado.')
        try: validate_email(email)
        except ValidationError: errors.append('Ingresa un correo electrónico válido.')
        if not account and len(password)<12: errors.append('La contraseña inicial debe tener al menos 12 caracteres.')
        elif account and password and len(password)<12: errors.append('La nueva contraseña debe tener al menos 12 caracteres.')
        if not errors:
            if account is None:
                account=User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name,is_staff=True,is_superuser=False)
                access=AdminAccess.objects.create(user=account)
                messages.success(request,'Cuenta administradora creada. Activa los permisos necesarios antes de entregarle acceso.')
            else:
                account.username=username; account.email=email; account.first_name=first_name; account.last_name=last_name
                if password: account.set_password(password)
                account.save(update_fields=['username','email','first_name','last_name','password'])
                access,created=AdminAccess.objects.get_or_create(user=account)
                for _,group in ADMIN_PERMISSION_GROUPS:
                    for key,_label in group: setattr(access,key,request.POST.get(f'perm_{key}')=='on')
                access.save()
                messages.success(request,'Datos y permisos de la cuenta actualizados.')
            if access and request.POST.get('save_permissions')=='1':
                for _,group in ADMIN_PERMISSION_GROUPS:
                    for key,_label in group: setattr(access,key,request.POST.get(f'perm_{key}')=='on')
                access.save()
            return redirect('admin_account_edit',pk=account.pk)
        for error in errors: messages.error(request,error)
        if account is None:
            account=User(username=username,email=email,first_name=first_name,last_name=last_name)
        access=access or AdminAccess()
        for _,group in ADMIN_PERMISSION_GROUPS:
            for key,_label in group: setattr(access,key,request.POST.get(f'perm_{key}')=='on')
    permission_groups=[{'name':name,'permissions':[{'key':key,'label':label,'enabled':bool(getattr(access,key,False))} for key,label in group]} for name,group in ADMIN_PERMISSION_GROUPS]
    return render(request,'admin_account_form.html',{'account':account,'access':access,'permission_groups':permission_groups,'is_new':pk is None})
def admin_account_delete(request,pk):
    if superuser_required(request): return redirect('signin')
    User=get_user_model(); account=get_object_or_404(User,pk=pk,is_staff=True,is_superuser=False)
    if request.method=='POST' and request.POST.get('confirm')=='yes':
        username=account.username; account.delete()
        messages.success(request,f'La cuenta administradora {username} fue eliminada.')
        return redirect('admin_accounts')
    return render(request,'admin_account_delete.html',{'account':account})
def project_new(request):
    denied=staff_required(request,'create_progress_project')
    if denied: return denied
    if request.method=='POST':
        data=request.POST
        name=data.get('name','').strip(); description=data.get('description','').strip()
        contact_name=data.get('contact_name','').strip(); company=data.get('contact_company','').strip()
        channel=data.get('contact_channel','').strip(); email=data.get('contact_email','').strip(); phone=data.get('contact_phone','').strip()
        errors=[]
        if not name: errors.append('Ingresa el nombre del proyecto.')
        if not description: errors.append('Ingresa una descripción del proyecto.')
        if not contact_name: errors.append('Ingresa el nombre del contacto del cliente.')
        if channel not in ['email','phone']: errors.append('Selecciona el canal de comunicación preferido.')
        if channel=='email':
            try: validate_email(email)
            except ValidationError: errors.append('Ingresa un correo válido para el cliente.')
        elif channel=='phone' and not phone: errors.append('Ingresa el teléfono del cliente.')
        if not errors:
            project=ClientProject.objects.create(name=name,description=description,contact_name=contact_name,contact_company=company,contact_email=email,contact_phone=phone,contact_channel=channel,state='progress')
            messages.success(request,f'Proyecto creado en progreso. Código de seguimiento: {project.code}.')
            return redirect('project_detail',pk=project.pk)
        for error in errors: messages.error(request,error)
        return render(request,'project_create.html',{'data':data})
    return render(request,'project_create.html',{})
def request_detail(request,pk):
    denied=staff_required(request,'view_requests')
    if denied: return denied
    item=get_object_or_404(ServiceRequest,pk=pk)
    return render(request,'request_detail.html',{'item':item,'permissions':{key:has_admin_access(request.user,key) for key in ['edit_requests','decide_requests','delete_requests']}})
def edit_request(request,pk):
    denied=staff_required(request,'edit_requests')
    if denied: return denied
    item=get_object_or_404(ServiceRequest,pk=pk)
    if request.method=='POST': item.project_name=request.POST.get('project_name',item.project_name); item.description=request.POST.get('description',item.description); item.save(); messages.success(request,'Solicitud actualizada.'); return redirect('request_detail',pk=pk)
    return render(request,'edit_request.html',{'item':item})
def decide_request(request,pk,decision):
    denied=staff_required(request,'decide_requests')
    if denied: return denied
    if request.method!='POST' or decision not in ['aceptar','rechazar']: raise Http404
    item=get_object_or_404(ServiceRequest,pk=pk)
    destination='solicitudes'
    if decision=='aceptar' and item.state=='confirmed':
        with transaction.atomic(): project,_=ClientProject.objects.get_or_create(request=item,defaults={'name':item.project_name,'description':item.description})
        Notification.objects.create(recipient=item.email if item.channel=='email' else item.phone,message=f'Solicitud aceptada. Código: {project.code}'); messages.success(request,f'Solicitud aceptada. Código: {project.code}')
        destination='progreso'
    elif decision=='rechazar':
        item.state='rejected'; item.save(update_fields=['state']); Notification.objects.create(recipient=item.email if item.channel=='email' else item.phone,message='Solicitud rechazada.'); messages.success(request,'Solicitud rechazada y archivada.')
    return redirect(f'/interno/?vista={destination}')
def delete_request(request,pk):
    denied=staff_required(request,'delete_requests')
    if denied: return denied
    item=get_object_or_404(ServiceRequest,pk=pk)
    if item.state!='pending' or hasattr(item,'project'):
        messages.error(request,'Solo se pueden eliminar solicitudes pendientes que aún no tengan un proyecto asociado.')
        return redirect('request_detail',pk=pk)
    if request.method=='POST' and request.POST.get('confirm')=='yes':
        stored_files=[(f.file.storage,f.file.name) for f in item.files.all() if f.file and f.file.name]
        token=item.confirmation_token
        with transaction.atomic():
            Notification.objects.filter(message__contains=token).delete()
            item.delete()
            transaction.on_commit(lambda: [storage.delete(name) for storage,name in stored_files])
        messages.success(request,'La solicitud pendiente y sus archivos fueron eliminados.')
        return redirect('/interno/?vista=solicitudes')
    return render(request,'request_delete.html',{'item':item})
def project_detail(request,pk):
    project=get_object_or_404(ClientProject,pk=pk)
    permission='view_progress_projects' if project.state=='progress' else 'view_finished_projects'
    denied=staff_required(request,permission)
    if denied: return denied
    action_prefix='progress' if project.state=='progress' else 'finished'
    permissions={
        'add_update':has_admin_access(request.user,f'{action_prefix}_add_update'),
        'upload_file':has_admin_access(request.user,f'{action_prefix}_upload_file'),
        'finish_project':has_admin_access(request.user,'progress_finish_project'),
        'send_portfolio':has_admin_access(request.user,'finished_send_portfolio'),
        'reopen_project':has_admin_access(request.user,'finished_reopen_progress'),
    }
    return render(request,'project_detail.html',{'project':project,'permissions':permissions})
def add_update(request,pk):
    project=get_object_or_404(ClientProject,pk=pk)
    permission='progress_add_update' if project.state=='progress' else 'finished_add_update'
    denied=staff_required(request,permission)
    if denied: return denied
    if request.method=='POST' and request.POST.get('description','').strip(): ProgressUpdate.objects.create(project=project,description=request.POST['description'],photo=request.FILES.get('photo')); messages.success(request,'Avance guardado con fecha automática.')
    return redirect('project_detail',pk=pk)
def finish_project(request,pk):
    denied=staff_required(request,'progress_finish_project')
    if denied: return denied
    project=get_object_or_404(ClientProject,pk=pk)
    if request.method=='POST' and project.state=='progress':
        project.state='finished'; project.finished_at=timezone.now(); project.save(update_fields=['state','finished_at']); messages.success(request,'Proyecto trasladado a Terminados.')
    return redirect('/interno/?vista=terminados')
def reopen_project(request,pk):
    denied=staff_required(request,'finished_reopen_progress')
    if denied: return denied
    project=get_object_or_404(ClientProject,pk=pk)
    if request.method=='POST' and project.state=='finished':
        if PortfolioItem.objects.filter(source_project=project).exists(): messages.error(request,'Este proyecto ya está vinculado al portafolio y no puede volver a Proyectos en progreso.')
        else:
            project.state='progress'; project.finished_at=None; project.save(update_fields=['state','finished_at']); messages.success(request,'Proyecto trasladado a Proyectos en progreso.')
    return redirect('/interno/?vista=progreso' if project.state=='progress' else '/interno/?vista=terminados')
def start_portfolio(request,pk):
    denied=staff_required(request,'finished_send_portfolio')
    if denied: return denied
    project=get_object_or_404(ClientProject,pk=pk)
    if request.method!='POST' or project.state!='finished': return redirect('/interno/?vista=terminados')
    existing=PortfolioItem.objects.filter(source_project=project).first()
    if existing: return redirect('portfolio_edit',pk=existing.pk)
    return redirect(f'/interno/portafolio/nuevo/?proyecto={project.pk}')
def project_file(request,pk):
    project=get_object_or_404(ClientProject,pk=pk)
    permission='progress_upload_file' if project.state=='progress' else 'finished_upload_file'
    denied=staff_required(request,permission)
    if denied: return denied
    if request.method=='POST' and request.FILES.get('file'):
        f=request.FILES['file']; ext=f.name.rsplit('.',1)[-1].lower()
        if f.size<=10*1024*1024 and ext in ['pdf','png','jpg','jpeg','doc','docx','xls','xlsx']: ProjectFile.objects.create(project=project,file=f)
        else: messages.error(request,'Archivo no permitido: máximo 10 MB y formatos habituales de documento/imagen.')
    return redirect('project_detail',pk=pk)
def delete_project_file(request,file_id):
    f=get_object_or_404(ProjectFile,pk=file_id); pk=f.project_id
    permission='progress_upload_file' if f.project.state=='progress' else 'finished_upload_file'
    denied=staff_required(request,permission)
    if denied: return denied
    if request.method=='POST': f.file.delete(save=False); f.delete(); messages.success(request,'Archivo eliminado.')
    return redirect('project_detail',pk=pk)
def portfolio_edit(request,pk=None):
    item=get_object_or_404(PortfolioItem,pk=pk) if pk else None
    source_project=item.source_project if item else None
    if not item:
        source_id=request.POST.get('source_project') or request.GET.get('proyecto')
        if source_id:
            source_project=ClientProject.objects.filter(pk=source_id,state='finished').first()
            if not source_project: return redirect('/interno/?vista=terminados')
            existing=PortfolioItem.objects.filter(source_project=source_project).first()
            if existing: return redirect('portfolio_edit',pk=existing.pk)
    required_permission='edit_portfolio' if item else 'finished_send_portfolio' if source_project else 'add_portfolio'
    denied=staff_required(request,required_permission)
    if denied: return denied
    if request.method=='POST':
        cat=get_object_or_404(Category,pk=request.POST.get('category')); date=request.POST.get('date') or timezone.localdate()
        published=request.POST.get('published')=='1'
        if item:
            item.category=cat; item.name=request.POST.get('name',''); item.description=request.POST.get('description',''); item.date=date; item.featured=request.POST.get('featured')=='on'; item.published=published
            if request.FILES.get('photo'): item.photo=request.FILES['photo']
            elif request.POST.get('source_photo'): item.photo=selected_project_photo(source_project,request.POST.get('source_photo')) or item.photo
            item.save()
        else:
            item=PortfolioItem(category=cat,source_project=source_project,name=request.POST.get('name',''),description=request.POST.get('description',''),date=date,featured=request.POST.get('featured')=='on',published=published,photo=request.FILES.get('photo'))
            if not item.photo and request.POST.get('source_photo'): item.photo=selected_project_photo(source_project,request.POST.get('source_photo'))
            item.save()
        messages.success(request,'Portafolio actualizado.'); return redirect('/interno/?vista=portafolio')
    initial_category=Category.objects.filter(name=source_project.request.service).first() if source_project and source_project.request else None
    if source_project and not initial_category: initial_category=Category.objects.filter(name='Otros').first()
    initial_date=(source_project.finished_at.date() if source_project and source_project.finished_at else source_project.created_at.date() if source_project else timezone.localdate())
    photo_updates=source_project.updates.exclude(photo='') if source_project else []
    return render(request,'portfolio_form.html',{'item':item,'categories':Category.objects.all(),'source_project':source_project,'photo_updates':photo_updates,'initial_category':initial_category,'initial_date':initial_date})

def selected_project_photo(project,update_id):
    if not project or not str(update_id).isdigit(): return None
    update=ProgressUpdate.objects.filter(pk=int(update_id),project=project).exclude(photo='').first()
    if not update: return None
    from django.core.files import File
    from pathlib import Path
    update.photo.open('rb')
    return File(update.photo.file,name=Path(update.photo.name).name)
def portfolio_toggle(request,pk):
    denied=staff_required(request,'edit_portfolio')
    if denied: return denied
    if request.method=='POST':
        item=get_object_or_404(PortfolioItem,pk=pk); item.published=not item.published; item.save(update_fields=['published'])
    return redirect('/interno/?vista=portafolio')

def portfolio_delete(request,pk):
    denied=staff_required(request,'delete_portfolio')
    if denied: return denied
    item=get_object_or_404(PortfolioItem,pk=pk)
    error=''
    if request.method=='POST':
        if request.user.check_password(request.POST.get('password','')):
            token=secrets.token_urlsafe(32)
            request.session['portfolio_delete_confirmation']={'item_id':item.pk,'token':token,'expires':int(timezone.now().timestamp())+300}
            return redirect('portfolio_delete_confirm',pk=item.pk)
        error='La contraseña no coincide. No se realizó ningún cambio.'
    return render(request,'portfolio_delete.html',{'item':item,'error':error})

def portfolio_delete_confirm(request,pk):
    denied=staff_required(request,'delete_portfolio')
    if denied: return denied
    state=request.session.get('portfolio_delete_confirmation',{})
    valid=(state.get('item_id')==pk and state.get('expires',0)>=int(timezone.now().timestamp()))
    if not valid:
        request.session.pop('portfolio_delete_confirmation',None)
        messages.error(request,'La confirmación venció. Inicia el proceso de eliminación nuevamente.')
        return redirect('portfolio_delete',pk=pk)
    item=get_object_or_404(PortfolioItem,pk=pk)
    if request.method=='POST':
        if not secrets.compare_digest(str(request.POST.get('token','')),str(state.get('token',''))):
            request.session.pop('portfolio_delete_confirmation',None)
            messages.error(request,'No se pudo validar la segunda confirmación.')
            return redirect('portfolio_delete',pk=pk)
        source=item.source_project
        source_request=source.request if source and source.request_id else None
        stored_files=[]
        def collect(field):
            if field and field.name: stored_files.append((field.storage,field.name))
        collect(item.photo)
        if source:
            for obj in source.files.all(): collect(obj.file)
            for obj in source.updates.all(): collect(obj.photo)
            if source_request:
                for obj in source_request.files.all(): collect(obj.file)
        with transaction.atomic():
            if source:
                Notification.objects.filter(message__contains=source.code).delete()
                if source_request: Notification.objects.filter(message__contains=source_request.confirmation_token).delete()
            item.delete()
            if source:
                source.delete()
                if source_request: source_request.delete()
        for storage,name in stored_files: storage.delete(name)
        request.session.pop('portfolio_delete_confirmation',None)
        messages.success(request,'Proyecto eliminado junto con su seguimiento, solicitud asociada y ficha de portafolio.')
        return redirect('/interno/?vista=portafolio')
    return render(request,'portfolio_delete_confirm.html',{'item':item,'token':state['token'],'source_project':item.source_project})

def cancel_portfolio_delete(request):
    denied=staff_required(request,'delete_portfolio')
    if denied: return denied
    request.session.pop('portfolio_delete_confirmation',None)
    return redirect('/interno/?vista=portafolio')
