from django.contrib import admin

from crypt_my_cloud.models import File


class FileAdmin(admin.ModelAdmin):
    search_fields = ['file_name']
    readonly_fields = ('updated_at',)


admin.site.register(File, FileAdmin)