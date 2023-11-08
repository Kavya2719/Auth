import requests
import json

# Test for login
def login(email: str, password: str):
   body = {
       "email": email,
       "password": password
   }
   response = requests.post(url="http://127.0.0.1:8000/login", json=body)
   return json.loads(response.text)["token"]

print('Testing for login:')
print('jwt: ' + login("abcd@gmail.com", "123456") + '\n')


# Test for Ping
token = login("abcd@gmail.com", "123456")

def ping(token: str):
   headers = {
       'authorization': token
   }
   response = requests.post(url="http://127.0.0.1:8000/ping", headers=headers)
   return response.text

print('Testing for ping:')
print('uid: ' + ping(token) + '\n')


# Test for update
def updateUser(email:str, username:str, full_name:str):
   headers = {
       'authorization': token
   }
   body = {
        "email": email,
        "username": username,
        "full_name": full_name
   }
   response = requests.post(url='http://127.0.0.1:8000/updateUser/', headers=headers, json=body)
   return response.text

print('Testing updateUser:')
print(updateUser("abcd@gmail.com", "updated_username", "updated_full_name") + "\n")
# it can also change the email. Changing email will effect authorization too, for data consistency.


# Test for password reset
def generate_reset_password_link():
    headers = {
        'authorization': token
    }
    response = requests.post(url='http://127.0.0.1:8000/resetPassword/', headers=headers)
    return response.text

print('Testing generate reset password link:')
print(generate_reset_password_link() + '\n')


# Test for delete
def deleteUser(token: str):
   headers = {
       'authorization': token
   }
   response = requests.delete(url='http://127.0.0.1:8000/deleteUser/', headers=headers)
   return response.text

print('Testing for deleteUser:')
print(deleteUser(token))