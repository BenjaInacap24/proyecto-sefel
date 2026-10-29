from django.contrib import admin
from .models import AdminAccess, Category, ServiceRequest, RequestFile, ClientProject, ProjectFile, ProgressUpdate, PortfolioItem, Notification
admin.site.register([AdminAccess, Category, ServiceRequest, RequestFile, ClientProject, ProjectFile, ProgressUpdate, PortfolioItem, Notification])
