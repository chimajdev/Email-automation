from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from .models import (EmailCampaign, EmailConfiguration, EmailTemplate, 
                    EmailTemplateAttachment, EmailCampaignTemplate)


class AttachmentInline(admin.StackedInline):

    model = EmailTemplateAttachment
    extra = 0


@admin.register(EmailConfiguration)
class EmailServerAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'host']
    search_fields = ['user']
    autocomplete_fields = ['user']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):

    search_fields = ['id', 'user', 'public']
    list_display = ['id', 'user', 'body', 'datetime']
    list_filter = ['public']

    inlines = [AttachmentInline]
    autocomplete_fields = ['user']


@admin.register(EmailTemplateAttachment)
class EmailTemplateAttachmentAdmin(admin.ModelAdmin):

    list_display = ['id', 'template', 'attachment']
    autocomplete_fields = ['template']
    

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):

    search_fields = ['name', 'user']

    list_display = ['id', 'name', 'scheduled']
    list_filter = ['created_datetime', 'scheduled']

    autocomplete_fields = ['user']


@admin.register(EmailCampaignTemplate)
class EmailCampaignTemplatedmin(admin.ModelAdmin):

    list_display = ['id', 'campaign', 'template']

    autocomplete_fields = ['template', 'campaign', 'email']


