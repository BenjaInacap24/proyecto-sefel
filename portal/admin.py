from django.contrib import admin
from .models import Category, ServiceRequest, RequestFile, ClientProject, ProjectFile, ProgressUpdate, PortfolioItem, Notification
admin.site.register([Category, ServiceRequest, RequestFile, ClientProject, ProjectFile, ProgressUpdate, PortfolioItem, Notification])
