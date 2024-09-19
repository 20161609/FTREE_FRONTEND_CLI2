import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASIC_URL = os.getenv('BASIC_URL')

# Get Tree structure
def api_get_tree(id_token: str):
    try:
        url = f"{BASIC_URL}/db/get-tree/"
        headers = {"Authorization": f"Bearer {id_token}"}
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            branch_list = res.json()
            tree = {"Home": {}}
            branch_dict = {}

            for branch in branch_list:
                bid, path = branch['bid'], branch['path']
                branch_dict[path] = bid
                node = tree
                for branch_name in path.split('/'):
                    if branch_name not in node:
                        node[branch_name] = {}
                    node = node[branch_name]

            return {"status": True, "message": {"tree": tree, "branch_dict": branch_dict}}
        else:
            error_message = f"{res.status_code}, {res.json()['detail']}"
            return {"status": False, "message": error_message}
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}
    except Exception as e:
        return {"status": False, "message": str(e)}
    
# Add a new branch
def api_mkdir(id_token: str, branch: str, child_name: str):
    try:
        url = f"{BASIC_URL}/db/create-branch/"
        headers = {"Authorization": f"Bearer {id_token}"}
        body = {"branch": branch, "child_name": child_name}
        res = requests.post(url, headers=headers, json=body)
        
        if res.status_code == 200:
            return {"status":True, "message": "Successfully branch's created"}
        else:
            error_message = f"{res.status_code}, {res.json()['detail']}"
            return {"status":False, "message": error_message}

    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}
    
# Delete branch and its children 
def api_rmdir(id_token: str, branch: str):
    try:
        url = f"{BASIC_URL}/db/delete-branch/"
        headers = {"Authorization": f"Bearer {id_token}"}
        body = {"branch": branch}
        res = requests.delete(url, headers=headers, json=body)
        if res.status_code != 200:
            error_message = f"{res.status_code}, {res.json()['detail']}"
            return {"status":False, "message": error_message}

        return {"status":True, "message": "Successfully branch's deleted"}
    except requests.exceptions.RequestException as e:
        error_message = f"Request, {str(e)}"
        return {"status": False, "message": error_message}
    except Exception as e:
        error_message = f"Exception, {str(e)}"
        return {"status": False, "message": error_message}
