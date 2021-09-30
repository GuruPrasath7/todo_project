from django.contrib import admin
from todo_app.models import User, ToDo


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('id', 'username', 'first_name', 'last_name')


class ToDoAdmin(admin.ModelAdmin):
    model = ToDo
    list_display = ('id', 'user', 'task_name', 'status', 'priority', 'created_at')


admin.site.register(User, UserAdmin)
admin.site.register(ToDo, ToDoAdmin)
