from django.db import models
from django.conf import settings
from django.utils import timezone
    
class Project(models.Model):
    api_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=50, blank=True, null=True)
    trackable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Board(models.Model):
    api_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='boards')
    project_api_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Ycolumn(models.Model):
    api_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    color = models.IntegerField(blank=True, null=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    board_api_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class Task(models.Model):
    api_id = models.CharField(max_length=50, unique=True, db_index=True)
    parent = models.ForeignKey(
        'self',  # This refers to the Task model itself
        on_delete=models.CASCADE, # Or models.SET_NULL, models.PROTECT, etc., depending on your desired behavior
        blank=True,
        null=True,
        related_name='subtasks' 
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tasks',
        blank=True
    )
    ycolumn = models.ForeignKey(Ycolumn, on_delete=models.SET_NULL, related_name='tasks', null=True)
    column_api_id =models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True,default='')
    deleted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True) #completedTimestamp
    deadline = models.DateTimeField(null=True)
    api_user_id = models.CharField(max_length=50) #createdBy
    time_plan = models.DecimalField(max_digits=10,decimal_places=2, null=True)
    time_work = models.DecimalField(max_digits=10,decimal_places=2, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Workhour(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workhours')
    plan = models.DecimalField(max_digits=10,decimal_places=2)
    work = models.DecimalField(max_digits=10,decimal_places=2)
    workday = models.DateField(blank=True,null=True)






    


    


