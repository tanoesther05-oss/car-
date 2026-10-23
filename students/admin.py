from django.contrib import admin
from .models import StudyLevel, Program, Student, SyncLog

class ProgramInline(admin.TabularInline):
    model = Program
    extra = 0

@admin.register(StudyLevel)
class StudyLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    inlines = [ProgramInline]

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "order")
    list_filter = ("level",)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_names", "level", "program", "commune", "bus_choice", "local_override")
    list_filter = ("level", "program", "commune", "bus_choice")
    search_fields = ("last_name", "first_names", "commune")

@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("started_at", "source", "created", "updated", "ignored", "errors")
    readonly_fields = tuple(f.name for f in SyncLog._meta.fields)
