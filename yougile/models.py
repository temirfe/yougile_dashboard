from django.db import models
from django.conf import settings
    
class Project(models.Model):
    api_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Board(models.Model):
    api_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='boards')
    project_api_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Ycolumn(models.Model):
    api_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    color = models.IntegerField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    board_api_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class Task(models.Model):
    api_id = models.CharField(max_length=50)
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
    ycolumn = models.ForeignKey(Ycolumn, on_delete=models.SET_NULL, related_name='tasks')
    column_api_id =models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    title = models.TextField(blank=True,null=True)
    deleted = models.BooleanField(default=False)
    arhived = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField() #completedTimestamp
    deadline = models.DateTimeField()
    api_user_id = models.CharField(max_length=50) #createdBy
    time_plan = models.DecimalField(max_digits=10,decimal_places=2)
    time_work = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Workhour(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workhours')
    plan = models.DecimalField(max_digits=10,decimal_places=2)
    work = models.DecimalField(max_digits=10,decimal_places=2)
    workday = models.DateField(blank=True,null=True)






    


    


