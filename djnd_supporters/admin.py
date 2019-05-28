from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin
from djnd_supporters import models

class MilestonesInline(SortableInlineAdminMixin, admin.TabularInline):
    model = models.Milestone

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = (MilestonesInline,)

admin.site.register(models.Gift)
admin.site.register(models.Supporter)