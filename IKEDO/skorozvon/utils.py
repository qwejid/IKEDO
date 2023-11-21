# utils.py
import requests, os, json, time
from datetime import datetime, timedelta
from django.utils import timezone
from dotenv import load_dotenv

def get_documents_id(headers, payload):
    response_documents_sent = requests.get(
        'https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/docstorage/Documents/sent', 
        headers=headers,
        params=payload
    )

    response_documents_sent.raise_for_status()
    documents_sent_info = response_documents_sent.json()

    return [document_info.get("Id") for document_info in documents_sent_info]

def get_active_employee_ids(headers, documents_id):    
    employee_usage_count = {}
    current_datetime = timezone.now()    

    for document_id in documents_id:
        print(f'-------------------------{document_id}---------------------')
        response_documents_id = requests.get(
            f'https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/docstorage/Documents/{document_id}/route-stages',
            headers=headers,
        )

        response_documents_id.raise_for_status()
        documents_route_info_list = response_documents_id.json()

        for documents_route_info in documents_route_info_list:
            current_status = documents_route_info.get("CurrentStatus")
            if current_status == "Completed":
                route_members = documents_route_info.get("RouteMembers", [])
                for route_member in route_members:                    
                    signed_date_str = route_member.get('SignedDate')
                signed_date = datetime.strptime(signed_date_str, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)                
                
            
            if current_status == "Active":           
                route_members = documents_route_info.get("RouteMembers", [])
                for route_member in route_members:                       
                    if signed_date + timedelta(hours=1) < current_datetime:   
                        print(f'{signed_date} < {current_datetime}')                
                        employee_workplace = route_member.get("EmployeeWorkplace", {})
                        employee_id = employee_workplace.get("Employee", {}).get("Id")                    
                        employee_usage_count[employee_id] = employee_usage_count.get(employee_id, 0) + 1
        
        print(employee_usage_count)

    return employee_usage_count

def get_recipients_phone_numbers(headers, employee_usage_count):
    recipients_phone_numbers = []

    for employee_id in employee_usage_count:
        response_employee_details = requests.get(
            f"https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/staff/Employees/{employee_id}/",
            headers=headers,
        )

        response_employee_details.raise_for_status()
        employee_data_details = response_employee_details.json()
        first_name = employee_data_details.get("FirstName")
        last_name = employee_data_details.get("LastName")
        phone_numbers = employee_data_details.get("Contacts", [{}])

        for phone_number in phone_numbers:
            number = phone_number.get("PhoneNumber")
            recipients_phone_numbers.append({"number": number, "first_name": first_name, "last_name": last_name})

    print(f"Список данных получателей: {recipients_phone_numbers}") 
    return recipients_phone_numbers


def get_access_token():
    load_dotenv()

    api_url = 'https://app.skorozvon.ru/oauth/token'
    grant_type = os.getenv('GRANT_TYPE')
    username = os.getenv('USERNAME')
    api_key = os.getenv('API_KEY')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    data = {
        'grant_type': grant_type,
        'username': username,
        'api_key': api_key,
        'client_id': client_id,
        'client_secret': client_secret
    }

    # Отправка запроса на получение ключа авторизации
    response = requests.post(api_url, data=data)
    response.raise_for_status()

    # Проверка успешности запроса
    if response.status_code == 200:
        # Извлечение access_token из JSON-ответа
        access_token = response.json().get('access_token')       
        # print(f"Access Token: {access_token}")       
        return access_token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    

def loading_numbers(access_token, numbers):

    lead_data_list = []
    for number in numbers:
        lead_data_list.append({
            "name" : f"{number['first_name']} {number['last_name']}",
            "phones": [number['number']]
        })
           
    import_data = {
        "call_project_id": 20000083371,
        "data": lead_data_list, 
        "duplicates" : "skip"
    }

    
    response_lead = requests.post('https://app.skorozvon.ru/api/v2/leads/import',
                                 headers={"Authorization": f"Bearer {access_token}",
                                          "Content-Type": "application/json"},
                                 data=json.dumps(import_data))    

    # Проверяю успешность запроса
    if response_lead.status_code == 200:
        print("Контакты добавлены успешно!")      
    else:
        print(f"Error: {response_lead.status_code}, {response_lead.text}")
        return None
    
    import_id = response_lead.json().get('id')
    
    while True:
        state = get_import_status(access_token, import_id)
        
        if state == "loaded":
            print("Загрузка завершена.")
            break
        elif state == "enqueued" or state == "processing" or state == "duplicates" or state == "indexing":
            print(f"Загрузка находится в состоянии: {state}. Ожидаем...")
            time.sleep(5) 
        else:
            print(f"Неизвестное состояние загрузки: {state}. Прекращаю ожидание.")
            break

    return state, import_id   



def get_import_status(access_token, import_id):
    response_status = requests.get(
        f'https://app.skorozvon.ru/api/v2/leads/import/{import_id}',
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response_status.status_code == 200:
        return response_status.json().get('state')
    else:
        print(f"Ошибка получения статуса: {response_status.status_code}, {response_status.text}")
        return None

def get_leads_by_stored_file_id(access_token, stored_file_id):
    response_leads = requests.get(
        f'https://app.skorozvon.ru/api/v2/leads',
        headers={"Authorization": f"Bearer {access_token}"},
        params={"stored_file_id": stored_file_id}
    )

    if response_leads.status_code == 200:
        leads_data = response_leads.json()
        # Извлекаем id из каждого элемента списка
        ids = [item['id'] for item in leads_data.get('data', [])]
        return ids
    else:
        print(f"Ошибка получения потенциальных клиентов по сохраненному идентификатору файла.: {response_leads.status_code}, {response_leads.text}")
        return None
    
    
def add_contacts_to_the_project(access_token, lead_ids):
    load_dotenv()
    
    project_id = os.getenv('PROJECT_ID')
    data = {"lead_ids": lead_ids}

    response_assign_leads = requests.post(f'https://app.skorozvon.ru/api/v2/call_projects/{project_id}/assign_leads',
                                 headers={"Authorization": f"Bearer {access_token}",
                                          "Content-Type": "application/json"},
                                          json=data
                                 )
    if response_assign_leads.status_code == 200:
        message = "Контакты успешно добавлены в проект!"
        print(message)
    else:
        print(f"Error: {response_assign_leads.status_code}, {response_assign_leads.text}")


def bulk_delete_leads(access_token, lead_ids):
    url = 'https://app.skorozvon.ru/api/v2/leads/bulk_deletes'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "ids": lead_ids
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()
            bulk_delete_id = result.get('id')
            return bulk_delete_id
        else:
            print(f"Error bulk deleting leads: {response.status_code}, {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def start(access_token):
    load_dotenv()
    
    project_id = os.getenv('PROJECT_ID')
    response_call_projects_start = requests.post(f'https://app.skorozvon.ru/api/v2/call_projects/{project_id}/start',
                                 headers={"Authorization": f"Bearer {access_token}",
                                          "Content-Type": "application/json"},
                                 )
    if response_call_projects_start.status_code == 200:
        print("Робот начал обзванивать контакты!")        
    else:
        print(f"Error: {response_call_projects_start.status_code}, {response_call_projects_start.text}")
        







# def refresh_access_token():
#     api_url = 'https://app.skorozvon.ru/oauth/token'
#     refresh_token = os.getenv('ACCESS_TOKEN')
#     client_id = os.getenv('CLIENT_ID')
#     client_secret = os.getenv('CLIENT_SECRET')

#     data = {
#         'grant_type': 'refresh_token',
#         'refresh_token': refresh_token,
#         'client_id': client_id,
#         'client_secret': client_secret
#     }

#     response = requests.post(api_url, data=data)    

#     if response.status_code == 200:
#         access_token = response.json().get('access_token')
#         print(f"New Access Token: {access_token}")
#         return access_token
#     else:
#         print(f"Error: {response.status_code}, {response.text}")
#         return None