from django.shortcuts import render
from yougile.services.project_service import fetch_and_save_all_companies,fetch_and_save
from yougile.services.board_service import fetch_and_save_all_companies_boards,fetch_and_save_boards
from yougile.services.column_service import fetch_and_save_all_companies_columns,fetch_and_save_columns
from django.http import HttpResponse

def fetch_yougile_projects(request):
    #context = fetch_and_save('prosoft')
    context = fetch_and_save_all_companies()

    return HttpResponse(f'nahoi {context}')

def fetch_yougile_boards(request):
    #context = fetch_and_save_boards('product')
    context = fetch_and_save_all_companies_boards()

    return HttpResponse(f'fetch_and_save_boards {context}')

def fetch_yougile_columns(request):
    #context = fetch_and_save_columns('product', 'b41008ff-a281-4000-abf3-310a6ee48c19')
    #context = fetch_and_save_columns('prosoft')
    context = fetch_and_save_all_companies_columns()

    return HttpResponse(f'fetch_and_save_columns {context}')

def yoba(request):
    return HttpResponse('wassap')