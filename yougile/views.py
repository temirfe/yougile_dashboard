from django.shortcuts import render
from yougile.models import Project, Board, Ycolumn
from yougile.services.project_service import fetch_and_save_all_companies_projects,fetch_and_save_projects
from yougile.services.board_service import fetch_and_save_all_companies_boards,fetch_and_save_boards
from yougile.services.column_service import fetch_and_save_all_companies_columns,fetch_and_save_columns
from yougile.services.user_service import fetch_and_save_all_companies_users, fetch_and_save_users
from yougile.services.task_service import fetch_and_save_all_companies_tasks, fetch_and_save_by_active_columns, save_tasks, calc_hours
from django.http import HttpResponse

def fetch_yougile_projects(request):
    #context = fetch_and_save('prosoft')
    context = fetch_and_save_all_companies_projects()

    return HttpResponse(f'nahoi {context}')

def fetch_yougile_boards(request):
    #context = fetch_and_save_boards('product')
    context = fetch_and_save_all_companies_boards()

    return HttpResponse(f'fetch_yougile_boards {context}')

def fetch_yougile_columns(request):
    #context = fetch_and_save_columns('product', 'b41008ff-a281-4000-abf3-310a6ee48c19')
    #context = fetch_and_save_columns('prosoft')
    context = fetch_and_save_all_companies_columns()

    return HttpResponse(f'fetch_yougile_columns {context}')

def fetch_yougile_users(request):
    context = fetch_and_save_all_companies_users()
    return HttpResponse(f'fetch users {context}')

def fetch_yougile_tasks(request):
    #context = fetch_and_save_tasks('dartlab','787c50f1-f630-4f70-9a10-f5d9d72a5dd6')
    #context = fetch_and_save_all_companies_tasks()
    context = fetch_and_save_by_active_columns()
    return HttpResponse(f'fetch_yougile_tasks {context}')

def fetch_all_except_tasks(request):
    company = 'no'
    if 'company' in request.GET:
        company = request.GET['company']
        fetch_and_save_projects(company)
        fetch_and_save_boards(company)
        fetch_and_save_columns(company)
        fetch_and_save_users(company)

    return HttpResponse(f'test {company}')



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

class TaskHookView(APIView):
    authentication_classes = []  # No auth by default (external service)
    permission_classes = []      # No permission checks by default

    def post(self, request, *args, **kwargs):
        event = request.data.get("event")
        payload = request.data.get("payload", {})

        if not event:
            return Response({"error": "Missing event"}, status=status.HTTP_400_BAD_REQUEST)

        if event == "task-created":
            # Do not create task if it has parents
            if not payload.get("parents"):
                save_tasks([payload])

        elif event == "task-updated":
            save_tasks([payload])
            if payload.get("timeTracking") and payload.get("completedTimestamp"):
                calc_hours(today=True)

        return Response({"status": "ok"})
    
class ProjectHookView(APIView):
    authentication_classes = []  # No auth by default (external service)
    permission_classes = []      # No permission checks by default

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        event = request.data.get("event")
        payload = request.data.get("payload", {})

        if not event or not payload.get("id"):
            return Response({"error": "Missing event or payload id"}, status=status.HTTP_400_BAD_REQUEST)
        
        company = request.query_params.get("company") 

        model = None
        if event == "project-created":
            model = Project()
        else:
            model = Project.objects.filter(api_id=payload["id"]).first()

        if model:
            model.api_id = payload["id"]
            model.title = payload.get("title", "")
            if event == "project-deleted":
                model.trackable=False
            if company and not model.company:
                model.company = company

            try:
                model.save()
            except Exception as e:
                return Response(
                    {
                        "error": "Failed to save project",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"status": "ok"})
    
class BoardHookView(APIView):
    authentication_classes = []  # No auth by default (external service)
    permission_classes = []      # No permission checks by default

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        event = request.data.get("event")
        payload = request.data.get("payload", {})

        if not event or not payload.get("id"):
            return Response({"error": "Missing event or payload id"}, status=status.HTTP_400_BAD_REQUEST)

        model = None
        if event == "board-created":
            model = Board()
        elif event != "board-deleted":
            model = Board.objects.filter(api_id=payload["id"]).first()

        if model:
            model.api_id = payload["id"]
            model.title = payload.get("title", "")
            #print(f'projectId: {payload['projectId']}')
            if not model.project_id:
                model.project = Project.objects.get(api_id=payload['projectId'])
                model.project_api_id = payload['projectId']

            try:
                model.save()
            except Exception as e:
                return Response(
                    {
                        "error": "Failed to save board",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"status": "ok"})
    
class ColumnHookView(APIView):
    authentication_classes = []  # No auth by default (external service)
    permission_classes = []      # No permission checks by default

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        event = request.data.get("event")
        payload = request.data.get("payload", {})

        if not event or not payload.get("id"):
            return Response({"error": "Missing event or payload id"}, status=status.HTTP_400_BAD_REQUEST)

        model = None
        if event == "column-created":
            model = Ycolumn()
        elif event != "column-deleted":
            model = Ycolumn.objects.filter(api_id=payload["id"]).first()

        if model:
            model.api_id = payload["id"]
            model.title = payload.get("title", "")
            model.color = payload.get("color")
            #print(f'boardId: {payload['boardId']}')
            if not model.board_id:
                model.board = Board.objects.get(api_id=payload['boardId'])
                model.board_api_id = payload['boardId']

            try:
                model.save()
            except Exception as e:
                return Response(
                    {
                        "error": "Failed to save ycolumn",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"status": "ok"})

def yoba(request):
    return HttpResponse(f'wassap ')