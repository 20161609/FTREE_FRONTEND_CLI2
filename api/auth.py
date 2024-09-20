import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASIC_URL = os.getenv('BASIC_URL')

# Check user's exist
def api_possible_signup(email: str):
    try:
        url = f"{BASIC_URL}/user/check-user-exist/"
        res = requests.get(url, json={"email": email})
        if res.status_code == 200:
            return {"status":True, "message": "Email is possible to sign up"}
        else:
            return {"status":False, "message": "Email is already exist"}
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}
    except Exception as e:
        return {"status": False, "message": str(e)}

# Register a new user to Firebase and PostgreSQL
def api_signup(email:str, password: str, username: str, code:str):
    # Request to the server to create a new user
    url = f"{BASIC_URL}/user/signup/"
    response = requests.post(url, json={
        "email": email, "password": password,
        "username": username, "code": code
    })
    
    # Check the response status and return the user data
    try:
        if response.status_code == 200:
            return {"status": True, "message": "successfully signed up"}
        else:
            error_message = f"status code: {response.status_code},\n{response.json()}"
            return {"status": False, "message": error_message}
    except Exception as e:
        return {"status": False, "message": str(e)}

# Sign in the user and return the user data
def api_signin(email: str, password: str):
    try:
        url = f"{BASIC_URL}/user/signin/"
        res = requests.post(url, json={"email": email, "password": password})
        if res.status_code == 200:
            return {"status": True, "message": res.json()["message"]}
        else:
            erroer_message = f"{res.status_code}, {res.json()['detail']}"
            return {"status": False, "message": erroer_message}
    except requests.exceptions.RequestException as e:
        error_message = f"Request, {str(e)}"
        return {"status": False, "message": error_message}
    except Exception as e:
        error_message = f"Unexpected, {str(e)}"
        return {"status": False, "message": error_message}

# send the verification email
def api_send_verify_email(email: str):
    url = f"{BASIC_URL}/user/verify-email/"
    try:
        res = requests.post(url, json={"email": email})
        if res.status_code == 200:
            return {"status": True, "message": "Email sent"}
        else:
            return {"status": False, "message": res.json().get("detail", "Unknown error occurred")}
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}
    except Exception as e:
        return {"status": False, "message": str(e)}

# Change Password
def api_change_password(email: str, new_pw: str, code: str, id_token: str):
    url = f"{BASIC_URL}/user/modify-password/"
    try: 
        headers = {"Authorization": f"Bearer {id_token}"}
        body = {
            'email': email,
            'new_password': new_pw,
            'code': code
        }
        res = requests.post(url, json=body, headers=headers)
        if res.status_code != 200:
            error_message = f"{res.status_code}, {res.json()['detail']}"
            return {"status": False, "message": error_message}
    except requests.exceptions.RequestException as e:
        error_message = f"Request, {str(e)}"
        return {"status": False, "message": error_message}
    except Exception as e:
        error_message = f"Unexpected, {str(e)}"
        return {"status": False, "message": error_message}