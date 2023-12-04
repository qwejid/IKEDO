from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import requests, os
from django.contrib import messages
from django.http import HttpResponse
import logging
from celery import shared_task
from .tasks import process_call_task
from .utils import (
    get_documents_id,
    get_active_employee_ids,
    get_recipients_phone_numbers,
    get_access_token,
    loading_numbers,    
    get_leads_by_stored_file_id,    
    bulk_delete_leads,
    start    ,
    get_subdivision
)
@login_required(login_url='login')
def index(request):
    if request.method == 'POST':
        # Получаем значение токена из request.POST
        token = request.POST.get('token')
        if request.user.is_authenticated:
            # Сохраняем токен в поле 'token' модели пользователя
            request.user.token = token
            request.user.save()        
        return redirect('index')
    headers = {
            "Authorization": f"Bearer {request.user.token}",
            "kedo-gateway-token-type": "IntegrationApi"
        }
    sub_but = get_subdivision(headers)
    
    
    return render(request, "index2.html", context={"sub_but" : sub_but})


@login_required(login_url='login')
def update_token(request):
    if request.method == 'POST':
        # Получаем значение токена из request.POST
        token = request.POST.get('token')           
        request.user.token = token
        request.user.save()        
        return redirect('index')

    return render(request, "update_token.html")



@login_required(login_url='login')
def call(request):
    if request.method == 'POST' and 'obzvon_button' in request.POST:
        headers = {
            "Authorization": f"Bearer {request.user.token}",
            "kedo-gateway-token-type": "IntegrationApi"
        }
        payload = {"DocumentStatuses": "SignatureRequired"}
        
        subdivision = request.POST.get('selected_subdivision')
        sub_but = get_subdivision(headers)
        subdivision_name = sub_but.get(subdivision)
        
        
        user_token = request.user.token        
        if not user_token:
            return redirect('index')
        
 
        
        
        try:

            
            # task_result = process_call_task.apply_async(args=[headers, payload], countdown=5)
            # result = task_result.get(timeout=120)  
            # documents_id, recipients_phone_numbers = result["documents_id"], result["recipients_phone_numbers"]           

            
            documents_id = get_documents_id(headers, payload)
                        
            
            
            employee_ids = get_active_employee_ids(headers, documents_id)
            recipients_phone_numbers = get_recipients_phone_numbers(headers, employee_ids, subdivision)
            
            if not recipients_phone_numbers:
                return render(request, 'index2.html', context= {"text": "Нет документов для обработки"})   
                                           
            access_token = get_access_token() 
            contact_id = get_leads_by_stored_file_id(access_token)    
            bulk_delete_leads(access_token, contact_id)     
            loading_numbers(access_token, recipients_phone_numbers)          
            start(access_token)            
            
           
            context = {
                "documents_id" : documents_id,
                "recipients_phone_numbers" : recipients_phone_numbers,
                "subdivision" : subdivision_name
                }   
            
            return render(request, "call_info.html", context=context)
            
        except requests.exceptions.HTTPError as http_err:
            text = f"Произошла ошибка HTTP: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            text = f"Произошла ошибка соединения: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            text = (f"Произошла ошибка таймаута: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            text = f"Произошла общая ошибка запроса: {req_err}"
        except Exception as e:
            text = f"Произошла общая ошибка: {e}"         

        context = {"text": text}
    else:
            return HttpResponse("Метод не поддерживается")

    return render(request, 'index2.html', context=context)



