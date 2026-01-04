from django.db import models
from django.contrib.auth.models import User
from Home.models import Exam


class ExamAuditLog(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=50)
    target = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


