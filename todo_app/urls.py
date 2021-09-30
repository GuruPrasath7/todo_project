from django.urls import path, include
from todo_app import views


urlpatterns = [
    path('swagger/', include('swagger_ui.urls')),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('todo/', views.TodoListView.as_view(), name='todo-list-view'),
    path('todo/<int:todo_id>/', views.ToDoDetailView.as_view(), name='todo-detail-view'),
]
