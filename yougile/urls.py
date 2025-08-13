from django.urls import path
from . import views

urlpatterns = [
    path('yoba/', views.yoba, name='yoba'),
    path('fetch-projects/', views.fetch_yougile_projects, name='fetch_projects'),
    path('fetch-boards/', views.fetch_yougile_boards, name='fetch_boards'),
    path('fetch-columns/', views.fetch_yougile_columns, name='fetch_columns'),
    path('fetch-users/', views.fetch_yougile_users, name='fetch_users'),
    path('fetch-tasks/', views.fetch_yougile_tasks, name='fetch_tasks'),
    path('fetch-half/', views.fetch_all_except_tasks, name='fetch_half'),
    path("taskhook/", views.TaskHookView.as_view(), name="taskhook"),
    path("projecthook/", views.ProjectHookView.as_view(), name="projecthook"),
    path("boardhook/", views.BoardHookView.as_view(), name="boardhook"),
    path("columnhook/", views.ColumnHookView.as_view(), name="columnhook"),
    #path('customer/', views.customer, name='customer'),
    #path('customer/', CustomerAPIView.as_view(), name='customer'),
]