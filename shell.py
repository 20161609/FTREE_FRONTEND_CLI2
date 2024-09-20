from libs.santizer import format_cost
from prettytable import PrettyTable
import getpass
import tkinter as tk
from api.auth import api_change_password, api_signin, api_signup
from api.auth import api_send_verify_email
from api.auth import api_possible_signup
from api.branch import api_mkdir, api_rmdir
from api.branch import api_get_tree

from api.transaction import get_transaction_daily, get_transaction_monthly
from windows.delete_window import DeleteWindow
from windows.modify_window import ModifyWindow
from windows.upload_window import UploadWindow


class Shell:
    def __init__(self):
        print("\"Welcome to F-tree\"")
        self.id_token = None
        self.email = None
        self.username = None
        self.branch = None
        self.mode = 'Viewer'
        self.tree = None
        self.branch_dict = {}
        self.prompt = f"\n[{self.mode}] ~ #{self.branch}\n{self.email}:~$ "
        self.renew_prompt()

    def renew_prompt(self):
        if self.email == None:
            email = 'Guest'
        else:
            email = self.email

        if self.branch != None:
            branch = self.branch[::]
        else:
            branch = 'None'
        self.prompt = f'\n[{self.mode}] ~ {email} #{branch}/\n$ '

    def fetch(self, command):
        try:
            list_cmd = command.strip().split()
            if len(list_cmd) == 1: # 1 words command
                if list_cmd[0] in ['signup', 'join', 'register']: # User: Sign up
                    self.signup()
                elif list_cmd[0] in ['signin', 'login']: # User: Sign in
                    self.signin()
                elif list_cmd[0] == 'mode': # Change Mode (Viewer <-> Editor)
                    self.modify_mode()
                elif list_cmd[0] in ['list', 'ls']: # Branch: List Children
                    self.list_branch()
                elif list_cmd[0] in ['insert', 'in']: # DB: Insert
                    self.insert()
                elif list_cmd[0] in ['remove', 'rm']: # DB: Remove
                    self.remove()
                elif list_cmd[0] == 'modify':
                    self.modify()
            elif len(list_cmd) == 2:
                if list_cmd[0] == 'mkdir': # Branch: Create New Child Branch
                    self.mkdir(list_cmd[1])
                elif list_cmd[0] in ['cd', 'chdir']: # Change Branch
                    self.chdir(list_cmd[1])
                elif list_cmd[0] in ['refer', 'rf']:
                    if list_cmd[1] in ['-d', '-daily']:
                        self.refer_daily()
                    elif list_cmd[1] in ['-m', '-monthly']:
                        self.refer_monthly()
                elif list_cmd[0] == 'rmdir':
                    self.rmdir(list_cmd[1])
                elif list_cmd[0] in ['change', 'ch']:
                    if list_cmd[1] in ['password','pw']:
                        self.change_password()
        except Exception as e:
            error_message = f'on fetch, \n{e}'
            print('...[ERROR]:', error_message)

        self.renew_prompt()

    # Auth
    def signup(self):
        if self.id_token == None:
            # Get Input for Sign up
            print("...[INFO] Please enter the following information to sign up.")
            print("...[INFO] If you want to cancel, please input 'q!'.")
            email = input("...[INPUT] Email: ")
            if email == 'q!':
                return
            else:
                # Check if the email is possible to sign up
                try:
                    res_possible = api_possible_signup(email)
                    if res_possible['status'] == False:
                        print('...[ERROR]', res_possible['message'])
                        return
                except Exception as e:
                    print('...[ERROR]', e)
                    return

            name = input("...[INPUT] Name: ")
            if name == 'q!':
                return
            password = getpass.getpass("...[INPUT] Password: ")

            # Verify Email and Sign up
            try:
                res_sendemail = api_send_verify_email(email)
                if res_sendemail['status'] == False:
                    print("...[ERROR]", res_sendemail['message'])
                    return
                code = input("...[INPUT] Enter the verification code sent to your email: ")
                res = api_signup(email, password, name, code)
                if res['status'] == False:
                    print("...[ERROR]", res['message'])
            except Exception as e:
                print('...[ERROR]', e)
                return

            # If verification is successful, sign in
            print('...[SUCCESS]', res['message'])
            res = api_signin(email, password)
            if res['status'] == False:
                print("...[ERROR]", res['message'])
                return
            
            # Get User Info
            user_info = res['message']
            self.id_token = user_info['id_token']
            self.email = user_info['email']
            self.name = user_info['name']
            self.branch, self.mode = 'Home', "Viewer"

            # Get Tree
            res_tree = api_get_tree(self.id_token)
            self.branch_dict = res_tree['message']['branch_dict']
            self.tree = res_tree['message']['tree']
        else:
            print("...[ERROR] You are already logged in.")
        
    def signin(self):
        # Check if already logged in
        if self.id_token != None:
            print("...[ERROR] You are already logged in.")
            return

        # Get Input for Sign in
        email = input("...[INPUT] Email: ")
        password = getpass.getpass("...[INPUT] Password: ")
        res = api_signin(email, password)
        if res['status'] == False:
            print("...[ERROR]", res['message'])
            return
        
        # Get User Info
        user_info = res['message']
        print(user_info)
        print('Successfully signed in')
        return
        self.id_token = user_info['id_token']
        self.email = user_info['email']
        self.name = user_info['name']
        self.branch, self.mode = 'Home', "Viewer"

        # Get Tree
        res_tree = api_get_tree(self.id_token)
        self.branch_dict = res_tree['message']['branch_dict']
        self.tree = res_tree['message']['tree']

    def modify_mode(self):
        if self.mode == 'Viewer':
            self.mode = 'Editor'
        else:
            self.mode = 'Viewer'

    def change_password(self):
        # Check Token
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
        
        # Get New Password
        new_pw = input('...[INPUT] Enter the new password: ')
        
        # Send Verification Email
        res_sendemail = api_send_verify_email(self.email)
        if res_sendemail['status'] == False:
            print("...[ERROR]", res_sendemail['message'])
            return
        print("...[INFO] Verification code has been sent to your email.")
        code = input('...[INPUT] Enter the verification code: ')

        # Change Password
        res_change = api_change_password(self.email, new_pw, code, self.id_token)
        if res_change['status'] == False:
            print("...[ERROR]", res_change['message'])
            return
        print("...[SUCCESS]", res_change['message'])

    # Branch
    def list_branch(self):
        # Token Check
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
    
        # Print Children
        for i, child in enumerate(self.get_path_list()):
            print(f"{i+1}. {child}")

    def mkdir(self, child_name):
        # Chcek Login
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
        
        # Check mode
        if self.mode == 'Viewer':
            print("...[ERROR] You are in Viewer mode. You need to change to Editor mode.")
            print("...[INFO] To change the mode, input 'mode'")
            return

        # Check Already Exist
        child_path = self.branch + '/' + child_name        
        if child_path in self.branch_dict:
            print(f"...[ERROR] Branch already exists. [{child_path}]")
            return
        
        # Execute Mkdir
        res = api_mkdir(self.id_token, self.branch, child_name)
        if res['status'] == False:
            print(f"...[ERROR] {res['message']}")
            return

        # Get Tree
        res_tree = api_get_tree(self.id_token)
        self.branch_dict = res_tree['message']['branch_dict']
        self.tree = res_tree['message']['tree']
        print(f"...[SUCCESS] {res['message']}")

    def chdir(self, branch_path: str):
        # Check login status
        if self.id_token == None:
            print("...[ERROR] You are not logged in.")
            return

        # make path
        branch_depth = len(self.branch.split('/'))
        back_motion_count = 0
        for node in branch_path.split('/'):
            if node == '..':
                back_motion_count += 1
            else:
                break
        base_path_depth = max(branch_depth - back_motion_count, 1)
        base_path = '/'.join(self.branch.split('/')[:base_path_depth:])
        base_path += ''.join([f'/{node}' for node in branch_path.split('/')[back_motion_count:]])
        base_path = base_path[:-1] if base_path[-1] == '/' else base_path

        # Check if the path exists
        node = self.tree["Home"]
        nxt_path = "Home"
        for node_name in base_path.split('/')[1::]:
            # When Index's given 
            if node_name.isdigit():
                children = self.get_path_list(nxt_path)

                index = int(node_name) - 1
                if not (0 <= index < len(children)):
                    print(f"...[ERROR] Index out of range. [{nxt_path}/{node_name}]")
                    return
                node_name = children[index]

            # Shift to next node
            if not node_name in node:
                print(f"...[ERROR] No such Branch {nxt_path}/{node_name}")
                return
            nxt_path += f'/{node_name}'
            node = node[node_name]
        
        # Change Branch
        self.branch = nxt_path

    def rmdir(self, branch_path: str):
        # Check login status
        if self.id_token == None:
            print("...[ERROR] You are not logged in.")
            return
        
        # Check mode (Editor)
        if self.mode == 'Viewer':
            print("...[ERROR] You are in Viewer mode. You need to change to Editor mode.")
            print("...[INFO] To change the mode, input 'mode'")
            return
        
        # Check if the path exists
        if branch_path.isdigit():
            children = self.get_path_list()
            index = int(branch_path) - 1
            if not (0 <= index < len(children)):
                print(f"...[ERROR] Index out of range. [{self.branch}/{branch_path}]")
                return
            branch_path = children[index]
        
        if not branch_path in self.get_path_list():
            print(f"...[ERROR] No such Branch {self.branch}/{branch_path}")
            return
      
        res = api_rmdir(id_token=self.id_token, branch=self.branch + '/' + branch_path)
        if res['status'] == False:
            print(f"...[ERROR] {res['message']}")
            return
        else:
            print(f"...[SUCCESS] {res['message']}")
            return

    # Transaction CRUD
    def insert(self):
        if not self.id_token:
            print("...[ERROR] You are not logged in.")
            return
        if self.mode == "Viewer":
            print("...[ERROR] You are not in the Editor mode.")
            return
        
        UploadWindow(
            branch_options=list(self.branch_dict.keys()), 
            branch_path=self.branch, 
            id_token=self.id_token,
            tree=self.tree
        )

    def remove(self, begin_date='0001-01-01', end_date='9999-12-31'):
        if self.id_token == None:
            print("...[ERROR] You are not sign in.")
            print("...[INFO] If you want to sign in, please input 'signin'.")
            return
        
        if self.mode == "Viewer":
            print("...[ERROR] You are not in the Editor mode.")
            print("...[INFO] If you want to delete the transaction, please input 'mode'.")
            return

        DeleteWindow({
            'branch': self.branch,
            'id_token': self.id_token,
            'begin_date': begin_date,
            'end_date': end_date
        })


        pass

    def modify(self):
        # Check Token
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
        
        # Check Mode (Editor)
        if self.mode == 'Viewer':
            print("...[ERROR] You are in Viewer mode. You need to change to Editor mode.")
            print("...[INFO] To change the mode, input 'mode'")
            return

        ModifyWindow(
            id_token=self.id_token,
            branch=self.branch,
            branch_options=list(self.branch_dict.keys()), 
        )

        pass
    
    def refer_daily(self, begin_date='0001-01-01', end_date='9999-12-31'):
        # Check Token
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
        
        res = get_transaction_daily(id_token=self.id_token, branch=self.branch)
        if res.status_code != 200:
            print(f"...[ERROR] {res.status_code}, {res.json()['detail']}")
            return
        
        history = res.json()
        if len(history) == 0:
            print("...[INFO] No Transaction data")
            return
        
        table = PrettyTable()
        table.field_names = ['T-id', 'When', 'Branch', 'Income', 'Expenditure', 'Balance','Description', 'Receipt', 'Date-created']
        total_in, total_out, balance = 0, 0, 0

        # Iterate the history and print table row
        for record in history:
            tid = record['tid']
            when = record['t_date']
            branch = record['branch']
            income = record['cashflow'] if record['cashflow'] > 0 else 0
            expenditure = -record['cashflow'] if record['cashflow'] < 0 else 0

            total_in += record['cashflow'] if record['cashflow'] > 0 else 0
            total_out += -record['cashflow'] if record['cashflow'] < 0 else 0
            balance += record['cashflow']
            description = record['description']
            receipt = 'Yes' if record['receipt'] else 'No'
            c_date = record['c_date']

            row = [tid, when, branch, 
                    format_cost(income), 
                    format_cost(expenditure), 
                    format_cost(balance), 
                    description, receipt, c_date]
            
            table.add_row(row)
            continue

        # Print the summary
        print(table)
        print("\n*** Summary ***")
        print("- Branch: {}".format(branch))
        print("- Period: {} ~ {}".format(begin_date, end_date))
        print("- Count: {}".format(len(history)))
        print("- Total In: {}".format(format_cost(total_in)))
        print("- Total Out: {}".format(format_cost(total_out)))
        print("- Balance: {}".format(format_cost(balance)))
        print()
            
    def refer_monthly(self, begin_date='0001-01-01', end_date='9999-12-31'):
        # Check Token
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
        
        res = get_transaction_monthly(id_token=self.id_token, branch=self.branch)
        if res.status_code != 200:
            print(f"...[ERROR] {res.status_code}, {res.json()['detail']}")
            return
        
        history = res.json()
        if len(history) == 0:
            print("...[INFO] No Transaction data")
            return

        table = PrettyTable()
        table.field_names = ['Monthly', 'Income', 'Expenditure', 'Balance']
        total_in, total_out, balance = 0, 0, 0
        for record in history:
            monthly = (record['monthly'])
            income = record['income']
            expenditure = record['expenditure']
            
            total_in += record['income']
            total_out += record['expenditure']
            balance += income - expenditure

            row = [monthly,
                    format_cost(income), 
                    format_cost(expenditure), 
                    format_cost(balance)
                    ]
            
            table.add_row(row)
            continue

        # Print the summary
        print(table)
        print("\n*** Summary ***")
        print("- Branch: {}".format(self.branch))
        print("- Period: {} ~ {}".format(begin_date, end_date))
        print("- Total In: {}".format(format_cost(total_in)))
        print("- Total Out: {}".format(format_cost(total_out)))
        print("- Balance: {}".format(format_cost(balance)))
        print()

    # Library Functions
    def get_path_list(self, branch: str = None):
        # Token Check
        if self.id_token == None:
            print("...[ERROR] You need to log in first.")
            return
        
        # Get Children
        if branch == None:
            branch = self.branch
        node = self.tree
        for branch_name in branch.split('/'):
            node = node[branch_name]
        children = list(node.keys())

        # Sort Children by tid refering to branch_dict
        children.sort(key=lambda x: self.branch_dict[branch + '/' + x])
        return children        

