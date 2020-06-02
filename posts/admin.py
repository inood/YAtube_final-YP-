from django.contrib import admin

from .models import Comment, Follow, Group, Post


class BaseModelAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'

    def get_author(self, obj):
        return f'{obj.author.first_name} {obj.author.last_name}'
    get_author.short_description = 'Автор'


class PostAdmin(BaseModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    list_display_links = ('pk', 'text')
    search_fields = ('text',)
    list_filter = ('pub_date',)


class GroupAdmin(BaseModelAdmin):
    list_display = ('pk', 'title', 'slug')
    list_display_links = ('pk', 'title', 'slug')
    list_filter = ('title',)


class CommentAdmin(BaseModelAdmin):
    list_display = ('pk', 'text', 'created', 'get_author', 'post')
    list_filter = ('post', 'author')
    search_fields = ('text',)


class FollowAdmin(BaseModelAdmin):
    list_display = ('get_user', 'get_author')
    list_filter = ('user', 'author')

    def get_user(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    get_user.short_description = 'Пользователь'

    def get_author(self, obj):
        return f'{obj.author.first_name} {obj.author.last_name}'
    get_author.short_description = 'Подписан на автора'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
