from django.db import models
from eth_utils import ValidationError


# Create your models here.

class MilitaryScenario(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "MilitaryScenario"
        verbose_name = 'MilitaryScenario'
        verbose_name_plural = 'MilitaryScenario'

        def __str__(self):
            return self.Id


class MilitaryOrganizationPowerType(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=30)
    commander = models.ForeignKey("MilitaryOrganizationPowerType", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "MilitaryOrganizationPowerType"
        verbose_name = 'MilitaryOrganizationPowerType'
        verbose_name_plural = 'MilitaryOrganizationPowerTypes'

        def __str__(self):
            return self.Id


# MILITARYORGANIZATION
class MilitaryOrganization(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    type = models.ForeignKey("MilitaryOrganizationPowerType", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=30)
    commander = models.ForeignKey("MilitaryOrganization", on_delete=models.CASCADE, blank=True, null=True)
    scenario = models.ForeignKey(MilitaryScenario, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "MilitaryOrganization"
        verbose_name = 'MilitaryOrganization'
        verbose_name_plural = 'MilitaryOrganization'

        def __str__(self):
            return self.Id


class Carrier(models.Model):
    Id = models.AutoField(primary_key=True, unique=True)
    VisibilityRange = models.FloatField(max_length=30, blank=True, null=True)
    v_min = models.FloatField(max_length=30, blank=True, null=True)
    v_max = models.FloatField(max_length=30, blank=True, null=True)
    scenario = models.ForeignKey("MilitaryScenario", on_delete=models.CASCADE, blank=True, null=True)

class Platform(Carrier):
    ARMORED_CATEGORY = 'armored'
    CATEGORY_CHOICES = (
        (ARMORED_CATEGORY, 'Armored'),
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=ARMORED_CATEGORY)
    Military_Organization = models.ForeignKey(MilitaryOrganization, on_delete=models.CASCADE)

class Guarani(Platform):
    name = models.CharField(max_length=30)


#CRIAR OPERATIONAL ELEMENT E INSTITUTIONAL ELEMENT?


class MilitaryPerson(models.Model):
    Identifier = models.CharField(max_length=30)  # 01,02,03...
    Military_Organization = models.ForeignKey(MilitaryOrganization, on_delete=models.CASCADE)
    CommDevice_Carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='commdevicecarrier', blank=True, null=True)
    scenario = models.ForeignKey("MilitaryScenario", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "MilitaryPerson"
        verbose_name = 'MilitaryPerson'
        verbose_name_plural = 'MilitaryPerson'

        def __str__(self):
            return self.Identifier


