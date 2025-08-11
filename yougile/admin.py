from django.contrib import admin
from .models import Project, Board, Ycolumn, Task, Workhour

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title','company','trackable','created_at']
    list_filter = ['company','trackable']
    search_fields = ['title']

class ProjectByCompanyFilter(admin.SimpleListFilter):
    title = 'Project'
    parameter_name = 'project'

    def lookups(self, request, model_admin):
        # Get the currently selected company from the URL query params
        company = request.GET.get('project__company')
        qs = Project.objects.all()
        if company:
            qs = qs.filter(company=company)
        return [(p.id, p.title) for p in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__id=self.value())
        return queryset
    
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['title','project','company_name','created_at']
    list_filter = ['project__company',ProjectByCompanyFilter]
    search_fields = ['title']

    def company_name(self, obj):
        return obj.project.company  # Access related model's field
    company_name.admin_order_field = 'project__company'  # Enable sorting
    company_name.short_description = 'Company'  # Column header

@admin.register(Ycolumn)
class YcolumnAdmin(admin.ModelAdmin):
    list_display = ['title','board','created_at']
    list_filter = ['board']
    search_fields = ['title']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title','completed','created_at']
    list_filter = ['completed']
    search_fields = ['title']
    ordering = ['-created_at','-completed_at']

@admin.register(Workhour)
class WorkhourAdmin(admin.ModelAdmin):
    list_display = ['user','plan','work', 'workday']
    list_filter = ['user','workday']