from celery import shared_task
import requests
from .utils import (
    get_documents_id,
    get_active_employee_ids,
    get_recipients_phone_numbers,
    get_access_token,
    loading_numbers,    
    get_leads_by_stored_file_id,
    add_contacts_to_the_project,
    bulk_delete_leads,
    start,    
)

@shared_task
def process_call_task(headers, payload):

    documents_id = get_documents_id(headers, payload)    
    employee_ids = get_active_employee_ids(headers, documents_id)
    recipients_phone_numbers = get_recipients_phone_numbers(headers, employee_ids)
    access_token = get_access_token()
    contact_id = get_leads_by_stored_file_id(access_token)
    bulk_delete_leads(access_token, contact_id)
    loading_numbers(access_token, recipients_phone_numbers)
    start(access_token)
    return {"documents_id": documents_id, "recipients_phone_numbers": recipients_phone_numbers}
               
            