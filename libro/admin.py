from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.utils.html import format_html

from libro import models


@admin.register(models.Book)
class OperatorsAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title_zh", "title_ori", 'title_en', 'author', 'length', 'chapters', 'desc'
    )
    list_per_page = 500
    ordering = ("id", )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @admin.display(description="章节")
    def chapters(self, obj):
        result = ''
        for sub_chapter in obj.subchapter_set.all():
            if sub_chapter.chapter_name_en:
                result += f"{sub_chapter.chapter_name_en}-{sub_chapter.chapter_name_ori}"
            elif sub_chapter.chapter_name_zh:
                result += f"{sub_chapter.chapter_name_zh}-{sub_chapter.chapter_name_ori}"
            else:
                result +=  f"{sub_chapter.chapter_name_ori}"
            result += "<br/>"

        return format_html(result)


@admin.register(models.Publisher)
class OperatorsAdmin(admin.ModelAdmin):
    list_display = ('id', "name_ori", )
    ordering = ("id", )

@admin.register(models.BookEdition)
class OperatorsAdmin(admin.ModelAdmin):
    list_display = ('id', "book", "publisher", )
    ordering = ("id", )


admin.site.site_header = "Deduction Library"
admin.site.site_title = "DeLib"
admin.site.index_title = "Welcome back, Have a nice day 😊!"
admin.site.register(models.Author)
admin.site.register(models.Series)
admin.site.register(models.Prize)
admin.site.register(models.BookLength)
admin.site.register(models.SubChapter)
admin.site.register(models.Cover)
admin.site.register(models.Awards)
admin.site.unregister(User)
admin.site.unregister(Group)
