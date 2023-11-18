# utils.py
import requests

def get_documents_id(headers, payload):
    response_documents_sent = requests.get(
        'https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/docstorage/Documents/sent', 
        headers=headers,
        params=payload
    )

    response_documents_sent.raise_for_status()
    documents_sent_info = response_documents_sent.json()

    return [document_info.get("Id") for document_info in documents_sent_info]

def get_employee_ids(headers, documents_id):
    employee_ids = set()

    for document_id in documents_id:
        response_documents_id = requests.get(
            f'https://api-gw.kedo-demo.cloud.astral-dev.ru/api/v3/docstorage/Documents/{document_id}/',
            headers=headers,
        )

        response_documents_id.raise_for_status()
        documents_info = response_documents_id.json()

        document_recipients = documents_info.get("Recipients", [])
        for recipient in document_recipients:
            employee_id = recipient.get("Employee", {}).get("Id")            
            employee_ids.add(employee_id)

    employee_ids = list(employee_ids)
    
    print(f"Список id получателей: {employee_ids}")  

    return employee_ids

def get_recipients_phone_numbers(headers, employee_ids):
    recipients_phone_numbers = []

    for employee_id in employee_ids:
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
