from django.contrib import admin
from django.utils.html import format_html
from campaign.models.Campaign import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    
    
    list_display = ('id', 'name', 'agent', 'started_at',
                    'ended_at', 'created_at', 'updated_at', 'send_email_button')
    list_filter = ('agent', 'started_at', 'ended_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    
    def send_email_button(self, obj):
        # Return a button for sending the email, along with a form for email input only.
        return format_html(
            '''
            <button type="button" class="send-email-btn" data-id="{}">Send Email</button>
            <div class="email-form-container" id="form-{}" style="display:none; margin-top: 5px;">
                <input type="email" class="email-input" placeholder="Enter email address" />
                <button type="button" class="email-send-btn" data-id="{}">Send</button>
                <button type="button" class="email-cancel-btn">Cancel</button>
            </div>
            ''',
            obj.pk, obj.pk, obj.pk
        )

    send_email_button.short_description = 'Send Email'
    
    class Media:
        js = ('campaign/admin_send_email.js',)
