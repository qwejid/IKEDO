import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings


# Получаю все имеющиеся поздразделения
def get_subdivision(headers):
    response_subdivisions = requests.get(
        f'{settings.API_URL}administrative/Subdivisions', 
        headers=headers,
    )
    response_subdivisions.raise_for_status()
    subdivisions = response_subdivisions.json()    
    names = {item["Id"]: item["Name"] for item in subdivisions}    
    return names


# Получаю id документов которые в состоянии подписания
def get_documents_id(headers, payload):
    response_documents_sent = requests.get(
        f'{settings.API_URL}docstorage/Documents/sent', 
        headers=headers,
        params=payload
    )
    response_documents_sent.raise_for_status()
    documents_sent_info = response_documents_sent.json()
    return [document_info.get("Id") for document_info in documents_sent_info]


# Получаю ID сотрудников которые должны подписать документ
def get_active_employee_ids(headers, documents_id):    
    employee_usage_count = {}
    current_datetime = timezone.now()  
    for document_id in documents_id:        
        response_documents_id = requests.get(
            f'{settings.API_URL}docstorage/Documents/{document_id}/route-stages',
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
                        employee_workplace = route_member.get("EmployeeWorkplace", {})
                        employee_id = employee_workplace.get("Employee", {}).get("Id")                    
                        employee_usage_count[employee_id] = employee_usage_count.get(employee_id, 0) + 1       
    return employee_usage_count


# Получаю номера телефонов сотрудников, которые еще работают и находяться в выбранном подразделении
def get_recipients_phone_numbers(headers, employee_usage_count, selected_subdivision):
    recipients_phone_numbers = []
    current_datetime = timezone.now() 
      
    for employee_id in employee_usage_count:        
        subdivision_list = []
        response_employee_details = requests.get(
            f"{settings.API_URL}staff/Employees/{employee_id}/",
            headers=headers,)        
        response_employee_details.raise_for_status()
        employee_data_details = response_employee_details.json()        
        employee_workplaces = employee_data_details.get("EmployeeWorkplaces", [{}])
        
        for workplace in employee_workplaces:                                
            work_ended = workplace.get("WorkEnded")                             
            if work_ended is not None:
                work_ended = (datetime.strptime(work_ended, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc))            
            if work_ended is None or work_ended > current_datetime:                
                subdivision_id = workplace.get("Subdivision", {}).get("Id")            
                subdivision_list.append(subdivision_id)              
            
        if selected_subdivision in subdivision_list or selected_subdivision == 'all':            
            first_name = employee_data_details.get("FirstName")
            last_name = employee_data_details.get("LastName")
            phone_numbers = employee_data_details.get("Contacts", [{}])
            for phone_number in phone_numbers:
                number = phone_number.get("PhoneNumber")
                recipients_phone_numbers.append({"number": number, "first_name": first_name, "last_name": last_name})    
    return recipients_phone_numbers
