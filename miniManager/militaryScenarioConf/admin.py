from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(MilitaryOrganization)

admin.site.register(MilitaryOrganizationPowerType)

admin.site.register(Carrier)

admin.site.register(Platform)

admin.site.register(Guarani)

admin.site.register(MilitaryPerson)

admin.site.register(MilitaryScenario)
