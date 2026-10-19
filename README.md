# SEFEL Ingeniería & Construcción — prototipo Django

Este proyecto es un **prototipo funcional de sitio web y gestión interna**, creado para demostrar cómo podría funcionar la presencia digital de SEFEL y el flujo básico de una solicitud de servicio hasta su seguimiento y publicación en el portafolio. Está hecho con Django 5.2. Usa SQLite por defecto en desarrollo local y puede usar PostgreSQL administrado (por ejemplo, Supabase) mediante `DATABASE_URL`.

Un prototipo sirve para revisar pantallas, navegación, textos y reglas de negocio con usuarios antes de invertir en el desarrollo y operación definitivos. Aunque varias funciones operan de verdad dentro del equipo local, esta entrega no está preparada para recibir información real ni para publicarse en Internet: usa servicios locales, credenciales de demostración y no cuenta con la infraestructura, seguridad operativa ni integraciones necesarias para producción.

## Cómo iniciarlo en Windows

1. Instala Python 3.10 o posterior.
2. Ejecuta `run.bat`. El script prepara el entorno, instala dependencias, inicializa la base local y arranca Django.
3. Abre http://127.0.0.1:8000.
4. Para entrar a Gestión interna usa la cuenta de demostración `admin` y la contraseña `sefel-demo`.

La cuenta y contraseña son públicas dentro de esta entrega y **solo sirven para probar localmente**. Nunca deben reutilizarse en un servidor real.

## Idea y recorrido principal

El sitio presenta los servicios de SEFEL y sus proyectos, y permite que un cliente envíe una solicitud. El equipo interno puede revisarla, aceptarla y convertirla en proyecto; registrar avances; finalizarlo; y, si corresponde, preparar una ficha para el portafolio. De esta manera el prototipo ilustra el recorrido comercial y operativo en un solo lugar.

Categorías disponibles incluyen estructuras metálicas, construcción y obras civiles, mantenimiento mecánico y eléctrico, fabricación especial, apoyo industrial y **Otros**, para trabajos que no encajen en las categorías principales.

## Vistas públicas

- **Inicio (`/`)**: presentación de SEFEL, enlaces a servicios y solicitudes y carrusel de proyectos destacados. Cada página del carrusel muestra hasta dos proyectos apilados, con imagen a la izquierda y descripción a la derecha; el cambio incluye una transición visual.
- **Nosotros (`/nosotros/`)**: presentación de la empresa y su enfoque.
- **Servicios (`/servicios/`)**: lista de áreas de servicio, incluida la categoría Otros.
- **Proyectos realizados (`/proyectos/`)**: portafolio publicado, filtros por categoría y proyectos recientes. Cada ficha admite recorte cuadrado de imagen junto al texto; en pantallas estrechas se adapta a una columna. Los cambios de categoría conservan la posición de lectura.
- **Contáctanos / Solicitar (`/solicitar/`)**: primero pregunta si la solicitud es para Empresa o Persona mediante dos tarjetas con iconos. Luego abre el formulario correspondiente; el de empresa solicita razón social. Permite seleccionar hasta cinco archivos, muestra individualmente el nombre y peso de cada archivo, permite agregarlos en varias selecciones y quitarlos antes de enviar, e indica el contador de hasta cinco adjuntos. Valida datos básicos, formatos permitidos y 10 MB por archivo.
- **Solicitud enviada**: muestra la solicitud recibida y un enlace de confirmación local. Ese enlace permite demostrar el paso de confirmación sin configurar correo o SMS.
- **Mi proyecto (`/mi-proyecto/`)**: consulta de solo lectura usando el código que se genera al aceptar una solicitud.

## Gestión interna

El acceso está en `/interno/ingresar/`. Las vistas se seleccionan en una barra horizontal ubicada en la parte superior del panel. Bajo el saludo se indica cuántas solicitudes están pendientes o que no hay ninguna.

- **Solicitudes**: lista solicitudes que todavía no se han convertido en proyectos y no fueron rechazadas. Permite revisar datos, descargar adjuntos, modificar nombre y descripción, y aceptar o rechazar una solicitud confirmada.
- **Detalle de solicitud**: presenta los antecedentes y archivos del cliente. Al aceptar una solicitud confirmada se crea un proyecto en progreso y un código de consulta; rechazarla la archiva como rechazada.
- **Proyectos en progreso**: permite abrir la gestión del proyecto y marcarlo como terminado.
- **Proyectos terminados**: permite gestionar el proyecto, devolverlo a progreso si aún no se asoció al portafolio o iniciar la creación de una ficha de portafolio.
- **Gestionar proyecto**: reúne datos y canales de contacto del cliente, archivos, historial de avances, carga de nuevos avances y fotografías, y gestión de archivos del proyecto.
- **Portafolio**: permite crear una ficha independiente o editar/publicar/retirar fichas existentes. Al crearla desde un proyecto terminado, se precargan el nombre, la descripción, categoría y fecha de término, y se puede elegir una foto del seguimiento o cargar otra. El proyecto terminado se conserva asociado. La publicación se confirma al guardar.
- **Eliminar ficha de portafolio**: exige una confirmación, la contraseña del usuario interno y una segunda confirmación. Si la ficha está ligada a un proyecto terminado, el flujo elimina también su solicitud, seguimiento y archivos asociados; la acción es irreversible en esta demo.
- **Comunicaciones**: historial de eventos generados por el sistema. Es una bitácora, no una bandeja de entrada. Indica qué notificación se habría enviado y a quién.
- **Cerrar sesión**: termina la sesión interna.

Los cambios de vista en el panel también conservan la posición de desplazamiento. La aplicación utiliza autenticación de Django para restringir las pantallas internas, pero aún requiere endurecimiento de seguridad antes de un despliegue público.

## Qué funciona y qué se simula

**Funciona en el entorno local:** navegación pública e interna, persistencia en SQLite, inicio de sesión, formularios y validaciones básicas, carga local de archivos, confirmación mediante enlace visible, flujo solicitud → proyecto → seguimiento → terminado → portafolio, filtros, carrusel, consulta mediante código, y registro de eventos.

**Se simula o requiere conexión externa:** entrega de correos y SMS, llamadas, WhatsApp automatizado, notificación a SEFEL y cualquier integración con sistemas externos. Las comunicaciones se guardan en la bitácora local; el prototipo no las envía. Los enlaces de contacto que abre una aplicación del usuario dependen de sus dispositivos y no equivalen a una integración de mensajería.

## Por qué sigue siendo un prototipo

La meta de esta entrega es hacer revisable el flujo y la interfaz, no resolver todavía las decisiones de operación del sistema real. SQLite y los archivos locales solo son apropiados para una demostración pequeña; el despliegue real necesita infraestructura, configuración por ambiente, protección de datos y una persona responsable de operar y mantener el servicio. Los datos semilla, credenciales y contenidos de muestra son demostrativos. Las fotografías y documentos deben ser reemplazados o cargados por SEFEL con autorización y contenido definitivo.

El alcance disponible tampoco incorpora cotización o presupuesto, análisis de precios unitarios (APU), costos y gastos, rentabilidad, facturación, pagos, planificación detallada, roles internos diferenciados, auditoría completa ni sincronización con un ERP/CRM.

## Trabajo necesario antes de convertirlo en el proyecto real

1. **Validar requisitos con SEFEL**: aprobar textos, identidad visual, servicios y categorías, campos requeridos, estados del proceso, permisos, datos que puede ver el cliente y qué información debe incluir cada notificación.
2. **Cerrar reglas de negocio**: definir quién recibe y asigna solicitudes, cómo se identifican clientes y proyectos, qué transiciones de estado se permiten, retención y eliminación de datos, y el alcance final de presupuestos, APU, costos, gastos, rentabilidad y facturación.
3. **Diseñar seguridad y privacidad**: definir aviso de privacidad y consentimiento, base legal y retención de datos; política de contraseñas, MFA, roles y permisos; protección de descargas; validación segura del contenido de archivos; límites y controles contra abuso; auditoría y procedimiento de incidentes. Revisar además las obligaciones legales aplicables con asesoría competente.
4. **Preparar la aplicación para producción**: generar una clave secreta nueva, desactivar `DEBUG`, restringir `ALLOWED_HOSTS`, configurar `CSRF_TRUSTED_ORIGINS`, HTTPS y cookies seguras, dominio, servidor WSGI/ASGI y variables por ambiente. `.env.example` solo contiene nombres y valores de muestra; nunca publicar credenciales reales.
5. **Elegir infraestructura**: el proyecto Supabase `sefel-portal` está creado en la organización `MoralesCompany` (región `sa-east-1`), pero todavía no se han aplicado migraciones ni cargado datos. Configurar `DATABASE_URL` con credenciales seguras en el entorno de despliegue; para Vercel, preferir el pooler de transacciones de Supabase (puerto 6543). Los archivos cargados aún se guardan localmente: producción requiere almacenamiento privado persistente con permisos y copias de seguridad. Definir alojamiento, DNS, correo saliente, monitoreo, registros, restauración y continuidad.
6. **Conectar servicios reales**: elegir proveedor y plantillas de correo/SMS/WhatsApp, configurar credenciales y consentimiento, gestionar rebotes/errores y reintentos, y comprobar entregas. Si se usará n8n u otro sistema, acordar endpoints, autenticación y manejo de fallos.
7. **Completar la experiencia del cliente y del equipo**: decidir si habrá acceso autenticado de clientes, actualización del estado en tiempo real, búsqueda y filtros internos, asignación de responsables, exportaciones y notificaciones configurables.
8. **Añadir módulos de negocio aprobados**: diseñar presupuestos, APU, costos, gastos, márgenes, aprobación comercial, documentos y facturación solo después de acordar reglas, fórmulas e integraciones contables.
9. **Asegurar calidad y operación**: crear pruebas automatizadas de reglas críticas y permisos, revisión de accesibilidad y compatibilidad móvil, pruebas de carga y seguridad, entorno de staging, proceso de migraciones, despliegues repetibles, alertas y documentación para administración.
10. **Preparar contenido y lanzamiento**: revisar la visibilidad pública del repositorio `proyecto-sefel`, terminar la configuración de base de datos y almacenamiento, cargar fotografías y fichas autorizadas, revisar textos con SEFEL, capacitar a los usuarios internos, migrar datos si corresponde y hacer una salida controlada con soporte y mantenimiento definidos.

El orden y alcance de estos puntos debe acordarse con SEFEL: son trabajo pendiente identificado para pasar de una demostración local a un servicio que pueda operar con clientes y datos reales.

## Preparación de GitHub, Vercel y Supabase

El código está publicado en `BenjaInacap24/proyecto-sefel` (actualmente público). Se creó el proyecto Vercel `proyecto-sefel`, pero GitHub aún no está enlazado: la conexión de Vercel rechazó el acceso al ámbito `morales-company` (403). Aún no hay despliegue porque también falta configurar `DATABASE_URL`. El proyecto Supabase `sefel-portal` está aprovisionado en `MoralesCompany`, región `sa-east-1`; Vercel detecta Django por `manage.py`, usa `sefel.wsgi.application` y publica `STATIC_ROOT` mediante su CDN. `.python-version` fija Python 3.13 y `vercel.json` establece un máximo de 60 segundos para la función Django.

La base usa migraciones de Django versionadas. En la migración de perfiles se agrega `ClientProfile` enlazado al usuario Django y la referencia opcional desde una solicitud. La autenticación y los administradores usan el sistema de Django (`auth_user`, grupos y permisos); no se creó una segunda tabla de usuarios ni se conectó Supabase Auth. `seed_demo` está bloqueado con `DEBUG=False` para evitar crear la cuenta de muestra en producción.

El proyecto Vercel ya tiene `DJANGO_DEBUG=false` y una `DJANGO_SECRET_KEY` generada y guardada como variable sensible para desarrollo, preview y producción. Falta configurar `DATABASE_URL` directamente en el panel de Vercel; no la compartas en el repositorio ni en el chat. Cópiala desde Supabase usando SSL y el pooler de transacciones (puerto 6543). `ALLOWED_HOSTS` y CSRF se derivan automáticamente del dominio `VERCEL_URL`; para dominios propios se deben definir `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_TRUSTED_ORIGINS`. Después verifica las variables, aplica las migraciones y crea el usuario administrador con una contraseña propia. El despliegue está pendiente hasta completar ese requisito. No se debe usar la cuenta local `admin / sefel-demo` en un servidor.

Los adjuntos y fotografías siguen configurados con el almacenamiento local de Django. El sistema de archivos de una función Vercel no es almacenamiento persistente, así que antes de aceptar archivos de clientes en producción se debe integrar almacenamiento externo privado (por ejemplo, Supabase Storage) y definir políticas de acceso/retención. Por esto la preparación del despliegue no equivale a estar listo para producción.

## Comandos manuales

Si prefieres preparar el entorno paso a paso en PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

`seed_demo` crea datos de demostración y la categoría Otros si aún no existe. No ejecutes este comando con datos reales sin revisar primero su comportamiento.
