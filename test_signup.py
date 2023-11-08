import requests
 
def signup(email: str, password: str, username: str, full_name: str):
   body = {
       "email": email,
       "password": password,
       "username": username,
       "full_name": full_name
   }
   response = requests.post(url="http://127.0.0.1:8000/signup", json=body)
   return response.text
 
print(signup("abcd@gmail.com", "123456", "username", "full_name"))