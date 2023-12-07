import requests, os, json, time
from dotenv import load_dotenv
from django.conf import settings


# Авторизуюсь
def get_access_token():
    load_dotenv()
    api_url = os.getenv('API_URL_SZ_AUTH')
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
    # Проверяю успешность запроса
    response.raise_for_status()    
    # Извлечение access_token из JSON-ответа
    access_token = response.json().get('access_token')         
    return access_token    
    

# Загружаю контакты в сервис скорозвон
def loading_numbers(access_token, numbers):
    load_dotenv()
    project_id = os.getenv('PROJECT_ID')
    lead_data_list = []
    for number in numbers:
        lead_data_list.append({
            "name" : f"{number['first_name']} {number['last_name']}",
            "phones": [number['number']]
        })
           
    import_data = {
        "call_project_id": project_id,
        "data": lead_data_list, 
        "duplicates" : "skip"
    }    
    response_lead = requests.post(
        f'{settings.API_URL_SZ}leads/import',
        headers={"Authorization": f"Bearer {access_token}",
                 "Content-Type": "application/json"},
        data=json.dumps(import_data)
    )   
    # Проверяю успешность запроса
    response_lead.raise_for_status()    
    import_id = response_lead.json().get('id')   
    while True:
        state = get_import_status(access_token, import_id)        
        if state == "loaded":            
            break
        elif state == "enqueued" or state == "processing" or state == "duplicates" or state == "indexing":            
            time.sleep(0.3)
        else:            
            print(f"Неизвестное состояние загрузки: {state}. Прекращаю ожидание.")
            break


# Получаю статус загрузки номеров в систему
def get_import_status(access_token, import_id):
    response_status = requests.get(
        f'{settings.API_URL_SZ}leads/import/{import_id}',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    # Проверяю успешность запроса
    response_status.raise_for_status()    
    return response_status.json().get('state')    


# Получаю статус удаления номеров в систему
def get_delete_status(access_token, import_id):
    response_status = requests.get(
        f'{settings.API_URL_SZ}bulk_deletes/{import_id}',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    # Проверяю успешность запроса
    response_status.raise_for_status()
    return response_status.json().get('state')     


# Получаю ID каждого номера в проекте
def get_leads_by_stored_file_id(access_token):    
    response_leads = requests.get(
        f'{settings.API_URL_SZ}leads',
        headers={"Authorization": f"Bearer {access_token}"}              
    )
    response_leads.raise_for_status()    
    leads_data = response_leads.json()
    # Извлекаем id из каждого элемента списка
    ids = [item['id'] for item in leads_data.get('data', [])]
    return ids


# Удаляю все номера из проекта
def bulk_delete_leads(access_token, lead_ids):
    if lead_ids is not None:     
        response = requests.post(
            f'{settings.API_URL_SZ}leads/bulk_deletes',
            headers={"Authorization": f"Bearer {access_token}",
                     "Content-Type": "application/json"}, 
            json={"ids": lead_ids}
        )
        response.raise_for_status()    
        delete_id = response.json().get('id') 

        while True:
            state = get_delete_status(access_token, delete_id)            
            if state == "finished":                
                break
            elif state == "created" or state == "processing":                
                time.sleep(0.3)                 
            else:
                print(f"Неизвестное состояние удаления: {state}. Прекращаю ожидание.")
                break    


# Запуск проекта
def start(access_token):
    load_dotenv()    
    project_id = os.getenv('PROJECT_ID')
    requests.post(
        f'{settings.API_URL_SZ}call_projects/{project_id}/start',
        headers={"Authorization": f"Bearer {access_token}"})
    