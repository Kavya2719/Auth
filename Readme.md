# Auth
## Project Explanation
Video Link: https://drive.google.com/file/d/1Psv_krtQQVhdbh2AAsFgTZim-7prweiF/view?usp=sharing

## Setting up Directions
for setting up the project in your local environment, you will be first needing the service_keys.json and firebase_config.json of the firebase.
After getting the firebase credentials, the application is ready to go.

Download the required dependencies for running the application, by the following command
```
pip install firebase_admin pyrebase4 fastapi slowapi 
```

Add the key databaseURL for the value as an empty string in the firebase_config.json, in case databaseURL is not present there. Otherwise, main.py will give error.
```
"databaseURL": ""
```

for starting the server, run the following command:
```
uvicorn main:app --reload
```

For running the python test files in order, run the following commands one by one:
```
python test_signup.py
```
```
python test_login.py
```
```
python test_rate_limiting.py
```
