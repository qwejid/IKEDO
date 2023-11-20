# utils.py
import requests
from datetime import datetime, timedelta
from django.utils import timezone

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
        phone_numbers = employee_data_details.get("Contacts", [{}])

        recipients_phone_numbers.extend(phone_number.get("PhoneNumber") for phone_number in phone_numbers)
    print(f"Список номеров: {recipients_phone_numbers}") 
    return recipients_phone_numbers
