from django.db import models
from django.contrib.auth.models import AbstractUser


class ModelConstants:
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    HOLD = "HOLD"
    COMPLETED = "COMPLETED"

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"

    todo_status = ((NOT_STARTED, NOT_STARTED), (IN_PROGRESS, IN_PROGRESS), (HOLD, HOLD), (COMPLETED, COMPLETED))
    todo_priority = ((LOW, LOW), (MEDIUM, MEDIUM), (HIGH, HIGH), (SEVERE, SEVERE))


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    username = models.CharField(max_length=256, unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class ToDo(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=256)
    task_description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=ModelConstants.todo_status)
    priority = models.CharField(max_length=25, choices=ModelConstants.todo_priority)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user.username) + ' - ' + str(self.task_name)
