from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import requests
from django.contrib import messages
from django.http import HttpResponse

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
    if request.method == 'POST':

        if not request.user.token:
            return redirect('index')

        headers = {"Authorization": f"Bearer {request.user.token}",
                   "kedo-gateway-token-type" : "IntegrationApi" }
        
        payload = {"DocumentStatuses" : "SignatureRequired"}                   
                   
                   
        documentsId = [] 
        employee_ids = []
        recipients_phone_numbers = []


        try:    
            # Запрос к sent для получения id всех документов кому был отправлен документ на подписание
            response_documents_sent = requests.get(
            'https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/docstorage/Documents/sent', 
            headers=headers,
            params=payload) 

            response_documents_sent.raise_for_status()
            documents_sent_info = response_documents_sent.json()
            

            for document_info in documents_sent_info:
                    document_info_id = document_info.get("Id")                
                    documentsId.append(document_info_id)            

            print(f"Список id документов: {documentsId}")

            # по полученым id документов просматриваю экземпляры документов
            for documentId in documentsId:
                response_documents_id = requests.get(
                f'https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/docstorage/Documents/{documentId}/', 
                headers=headers,
                )

                response_documents_id.raise_for_status()
                documents_info = response_documents_id.json()

                document_recipients = documents_info.get("Recipients", [])
                for recipient in document_recipients:
                    employee_id = recipient.get("Employee", {}).get("Id")
                    if employee_id:
                        employee_ids.append(employee_id)

            print(f"Список id получателей: {employee_ids}")

            # Запрос к Employees/{employee_id} для получения мобильных номеров
            for employee_id in employee_ids:
                
                response_employee_details = requests.get(
                    f"https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/staff/Employees/{employee_id}/", 
                    headers=headers,
                    )

                response_employee_details.raise_for_status()
                employee_data_details = response_employee_details.json()
                phone_numbers = employee_data_details.get("Contacts", [{}])

                for phone_number in phone_numbers:
                    recipient_number = phone_number.get("PhoneNumber")                
                    recipients_phone_numbers.append(recipient_number)
                
            print(f"Номера телефонов получателей: {recipients_phone_numbers}")
                
            messages.success(request, f'Номера сотрудников успешно загружены. \nОбзваниваю: {recipients_phone_numbers} ')

        except requests.exceptions.HTTPError as err:
            print(f"Ошибка запроса: {err}")
            messages.error(request, f"Ошибка запроса: {err}")
        
    else:
        return HttpResponse("Метод не поддерживается")
    
    return render(request, 'index.html')

