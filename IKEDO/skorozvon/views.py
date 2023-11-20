from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import requests
from django.contrib import messages
from django.http import HttpResponse
from .utils import get_documents_id, get_active_employee_ids, get_recipients_phone_numbers

# api_skorozvon = 'https://skorozvon.ru/features/golosovoy-robot'


def index(request):
    if request.method == 'POST':
        # Получаем значение токена из request.POST
        token = request.POST.get('token')
        if request.user.is_authenticated:
            # Сохраняем токен в поле 'token' модели пользователя
            request.user.token = token
            request.user.save()        
        return redirect('index')
    return render(request, "index.html")


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
        if not request.user.token:
            return redirect('index')
 
        headers = {
            "Authorization": f"Bearer {request.user.token}",
            "kedo-gateway-token-type": "IntegrationApi"
        }
        payload = {"DocumentStatuses": "SignatureRequired"}
        
        try:
            documents_id = get_documents_id(headers, payload)
                        
            if not documents_id:
                return render(request, 'index.html', context= {"text": "Нет документов для обработки"})
            
            employee_ids = get_active_employee_ids(headers, documents_id)
            recipients_phone_numbers = get_recipients_phone_numbers(headers, employee_ids)          
            
            text = f'''Номера сотрудников успешно загружены. 

                       Id документов в которых требуется оповестить подписателей 
                       {documents_id}

                       Id сотрудников от которых требуется подпись 
                       {employee_ids}
            
                       Обзваниваю: {recipients_phone_numbers}'''
            
        except requests.exceptions.HTTPError as err:
            # Пример русификации сообщений об ошибках
            if err.response.status_code == 404:
                text = 'Запрашиваемая страница не найдена.'
            elif err.response.status_code == 403:
                text = 'Доступ запрещен. У вас нет прав на выполнение данного действия.'
            elif err.response.status_code == 401:
                text = 'Не верный токен. Пожалуйста обновите и попробуйте снова.'
            else:
                context['text'] = f'Произошла ошибка запроса: {err}'
           

        context = {"text": text}
    else:
            return HttpResponse("Метод не поддерживается")

    return render(request, 'index.html', context=context)



