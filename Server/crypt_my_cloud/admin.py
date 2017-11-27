from django.contrib import admin

from crypt_my_cloud.models import Key, File


class KeyAdmin(admin.ModelAdmin):
    readonly_fields = ('updated_at',)


class FileAdmin(admin.ModelAdmin):
    search_fields = ['file_name']
    readonly_fields = ('updated_at',)


admin.site.register(Key, KeyAdmin)
admin.site.register(File, FileAdmin)
