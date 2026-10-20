"""Create idempotent SEFEL prototype content and a demo administrator."""

import os
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from portal.models import Category, ClientProject, PortfolioItem, ProgressUpdate, ServiceRequest


class Command(BaseCommand):
    help = "Create sample SEFEL content for the prototype. Safe to re-run."

    def handle(self, *args, **kwargs):
        production_seed_enabled = os.getenv("SEFEL_DEMO_SEED_ENABLED", "").lower() == "true"
        if not settings.DEBUG and not production_seed_enabled:
            raise CommandError(
                "Demo seeding is disabled outside development. Set SEFEL_DEMO_SEED_ENABLED=true "
                "only for the SEFEL demonstration environment."
            )

        username = os.getenv("SEFEL_DEMO_ADMIN_USERNAME", "admin")
        password = os.getenv("SEFEL_DEMO_ADMIN_PASSWORD", "")
        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": "demo@sefel.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            if not password:
                if not settings.DEBUG:
                    raise CommandError(
                        "Set SEFEL_DEMO_ADMIN_PASSWORD as a secret before creating the demo administrator."
                    )
                password = "sefel-demo"
            admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save(update_fields=["password", "is_staff", "is_superuser"])

        category_names = [
            "Estructuras metálicas",
            "Construcción y obras civiles",
            "Mantenimiento mecánico",
            "Mantenimiento eléctrico",
            "Fabricación especial",
            "Apoyo industrial",
            "Otros",
        ]
        categories = {
            name: Category.objects.get_or_create(name=name)[0] for name in category_names
        }

        portfolio_examples = [
            ("Pasarela metálica", category_names[0], "Referencia de estructura metálica y montaje.", True, 0),
            ("Galpón industrial", category_names[1], "Obras de edificación e infraestructura.", True, 1),
            ("Intervención mecánica y piping", category_names[2], "Mantenimiento y modificaciones mecánicas.", False, 2),
            ("Carro de arrastre", category_names[4], "Fabricación especial a requerimiento.", True, 3),
            ("Obra de edificación", category_names[1], "Ejecución y mejoramiento de infraestructura.", False, 4),
            ("Servicio industrial", category_names[5], "Apoyo a la continuidad operativa.", False, 5),
        ]
        for title, category_name, description, featured, days_ago in portfolio_examples:
            PortfolioItem.objects.get_or_create(
                name=title,
                defaults={
                    "category": categories[category_name],
                    "description": description,
                    "date": date.today() - timedelta(days=days_ago * 90),
                    "featured": featured,
                    "published": True,
                },
            )

        request, _ = ServiceRequest.objects.get_or_create(
            rut="76.123.456-7",
            project_name="Montaje de estructura metálica",
            defaults={
                "applicant_type": "company",
                "company_name": "Constructora Ejemplo SpA",
                "contact_name": "Ana Pérez",
                "email": "ana@ejemplo.cl",
                "phone": "+56 9 1234 5678",
                "channel": "email",
                "service": category_names[0],
                "description": "Proyecto de ejemplo para mostrar el recorrido completo de seguimiento.",
                "location": "Coelemu, Región de Ñuble",
                "state": "confirmed",
            },
        )
        project, _ = ClientProject.objects.get_or_create(
            request=request,
            defaults={
                "name": request.project_name,
                "description": request.description,
                "code": "SFL9K4M2R8TZ",
            },
        )
        if not project.updates.exists():
            ProgressUpdate.objects.create(
                project=project,
                description="Montaje de estructura principal: primer tramo completado.",
                created_at=timezone.now() - timedelta(days=2),
            )
            ProgressUpdate.objects.create(
                project=project,
                description="Preparación del área de trabajo finalizada.",
                created_at=timezone.now() - timedelta(days=5),
            )

        if settings.DEBUG:
            self.stdout.write(self.style.SUCCESS("Datos demo listos. Admin: admin / sefel-demo."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Datos demo listos. Usuario administrador creado o actualizado: {username}."
                )
            )
        self.stdout.write("Código de proyecto de ejemplo: SFL9K4M2R8TZ")

