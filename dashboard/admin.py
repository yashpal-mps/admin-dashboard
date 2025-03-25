from django.contrib import admin
from .models import Conversation
from .models.Leads import Lead
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class LeadResource(resources.ModelResource):
    class Meta:
        model = Lead
        fields = ('id', 'name', 'company_name', 'phone_no', 'email', 'linkedln', 
                 'facebook_id', 'twitter', 'city', 'state', 'country', 'type', 
                 'created_at', 'updated_at')
        export_order = fields
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin):
    resource_class = LeadResource
    list_display = ('id', 'name', 'company_name', 'email', 'phone_no', 'linkedln', 
                   'twitter', 'facebook_id', 'state', 'country', 'type', 'created_at')
    list_filter = ('type', 'country', 'state', 'created_at')
    search_fields = ('name', 'company_name', 'email', 'phone_no')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'leads', 'message', 'created_at', 'updated_at')
    list_filter = ('created_at', 'leads')
    search_fields = ('message', 'leads__company_name')
    readonly_fields = ('created_at', 'updated_at')
