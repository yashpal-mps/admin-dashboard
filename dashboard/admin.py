from django.contrib import admin
from .models import Leads, Conversation
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class LeadsResource(resources.ModelResource):
    class Meta:
        model = Leads
        fields = ('id', 'name', 'company_name', 'phone_no', 'email', 'linkedln', 
                 'facebook_id', 'twitter', 'city', 'state', 'country', 'type', 
                 'created_at', 'updated_at')
        export_order = fields
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

class LeadsAdmin(ImportExportModelAdmin):
    resource_class = LeadsResource
    list_display = ('id', 'name', 'company_name', 'email', 'phone_no', 'linkedln', 
                   'twitter', 'facebook_id', 'state', 'country', 'type', 'created_at')
    # list_filter = ('type', 'country', 'state', 'created_at')
    # search_fields = ('name', 'company_name', 'email', 'phone_no')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

admin.site.register(Leads, LeadsAdmin)
admin.site.register(Conversation)
