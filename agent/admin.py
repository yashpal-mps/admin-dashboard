from django.contrib import admin
from agent.models.Agent import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'status',
                    'company', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)
