from libs.santizer import format_date
from prettytable import PrettyTable
import requests
import mimetypes
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from dotenv import load_dotenv

load_dotenv()
BASIC_URL = os.getenv('BASIC_URL')

# get the tree with ID token
def upload_transaction(id_token:str, t_date:str, 
                       branch:str, cashflow:int, 
                       description:str, file_path=None):

    # Get Image file indicating receipt
    if not file_path:
        print("...[INFO] No file selected")
        file = None
    else:
        print("...[INFO] File selected:", file_path)
        file = open(file_path, 'rb')

    files = {'receipt': file} if file else None
    data = {
        't_date': t_date, 
        'branch': branch, 
        'cashflow': cashflow, 
        'description': description
    }
    headers = {"Authorization": f"Bearer {id_token}"}

    # Send the transaction data to the server
    url = f"{BASIC_URL}/db/upload-transaction/"
    res = requests.post(url, headers=headers, data=data, files=files)

    # Check the response
    if res.status_code == 200:
        return {"status": True, "message": "Successfully Transaction uploaded"}
    else:
        error_message = f"[ERROR] {res.status_code}, {res.json()['detail']}"
        return {"status": False, "message": error_message}

# Get daily Transactions
def get_transaction_daily(id_token, branch="Home", begin_date='0001-01-01', end_date='9999-12-31'):
    url = f"{BASIC_URL}/db/refer-daily/"
    headers = {"Authorization": f"Bearer {id_token}"}
    body = {'branch': branch, 'begin_date': begin_date, 'end_date': end_date}
    return requests.get(url, headers=headers, json=body)

# Get Monthly Transactions
def get_transaction_monthly(id_token, branch="Home", begin_date='0001-01-01', end_date='9999-12-31'):
    url = f"{BASIC_URL}/db/refer-monthly/"
    headers = {"Authorization": f"Bearer {id_token}"}
    body = {'branch': branch, 'begin_date': begin_date, 'end_date': end_date}
    return requests.get(url, headers=headers, json=body)

# Delete the transaction info from PostgreSQL and Firebase
def delete_transaction(id_token:str, tid:int):
    url = f"{BASIC_URL}/db/delete-transaction/"
    headers = {"Authorization": f"Bearer {id_token}"}
    data = {'tid': tid}
    res = requests.delete(url, headers=headers, json=data)
    
    if res.status_code == 200:
        print("...[SUCCESS] Transaction deleted successfully")
    else:
        print("...[ERROR] Upload failed, {res.status_code}\n" + res.json()['detail'])

# Get the receipt image from the server
def get_receipt_image(id_token:str, file_path: str):
    url = f"{BASIC_URL}/db/get-receipt/"
    headers = {"Authorization": f"Bearer {id_token}"}
    data = {'file_path': file_path}
    # response = requests.get(url, data={'id_token':id_token,'file_path': file_path})
    res = requests.get(url, headers=headers, json=data)

    if res.status_code != 200:
        print("...[ERROR]", res.status_code, res.json()['detail'])
        return None

    print("...[SUCCESS]", 'Successfully loaded the image')
    return res.json()

# Modify the transaction info
def modify_transaction(id_token:str, tid:str, t_date:str, branch:str, cashflow:int, description:str, receipt=None):
    # Get Image file indicating receipt
    headers = {"Authorization": f"Bearer {id_token}"}    
    files = {'receipt': receipt} if receipt else None
    data = {
        'tid': tid, 't_date': t_date, 'branch': branch, 'cashflow': cashflow,
        'id_token': id_token, 'description': description
    }

    # Send the transaction data to the server
    url = f"{BASIC_URL}/db/modify-transaction/"
    res = requests.put(url, headers=headers, data=data, files=files)

    # Check the response
    if res.status_code == 200:
        print("...[SUCCESS] Transaction modified successfully")
    else:
        print("...[ERROR]", res.status_code, res.json()['detail'])

