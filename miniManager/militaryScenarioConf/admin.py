from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(MilitaryOrganization)

admin.site.register(MilitaryOrganizationPowerType)

admin.site.register(CommDevice_Carrier)

admin.site.register(Military_Platform)

admin.site.register(MilitaryPerson)

admin.site.register(MilitaryScenario)