from django.contrib import admin
from .models import Agent, BuiltInAgent
# Register your models here.
admin.site.register(Agent)
admin.site.register(BuiltInAgent)
