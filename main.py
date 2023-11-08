import firebase_admin
import json
import pyrebase

from datetime import datetime
from firebase_admin import credentials, auth, firestore
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


# Setup Firebase
cred = credentials.Certificate('Auth_service_account_keys.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebase_config.json')))

# Setup Firestore
db = firestore.client()
users_ref = db.collection("users")

# Setup Fastapi
app = FastAPI()
allow_all = ['*']
app.add_middleware(
   CORSMiddleware,
   allow_origins=allow_all,
   allow_credentials=True,
   allow_methods=allow_all,
   allow_headers=allow_all
)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# home endpoint
@app.get("/")
@limiter.limit("5/minute")
async def read_root(request: Request):
    return {"message": "Hello, World!"}

# Note that the home endPoint have 5 api calls/minutes rate limit for testing purposes


# signup endpoint
@app.post("/signup")
@limiter.limit("50/minute")
async def signup(request: Request):
   req = await request.json()
   email = req['email']
   password = req['password']
   username = req['username']
   full_name = req['full_name']
   
   if email is None or password is None or full_name is None or username is None:
       return HTTPException(detail={'message': 'Error! Missing username or full_name or email or password'}, status_code=400)
   
   try:
        user = auth.create_user(
            email=email,
            password=password
        )
        user = auth.update_user(
            user.uid,
            display_name = username,
        )

        data = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "uid": user.uid,
            "created_at": datetime.now()
        }
        users_ref.document(user.uid).set(data)
        
        return JSONResponse(content={'message': f'Successfully created user: {user.uid}', 'uid': user.uid}, status_code=200)
   except Exception as e:
       return HTTPException(detail={'message': 'Error Creating User: ' + str(e)}, status_code=400)


# login endpoint
@app.post("/login")
@limiter.limit("50/minute")
async def login(request: Request):
   req_json = await request.json()
   email = req_json['email']
   password = req_json['password']
   try:
       user = pb.auth().sign_in_with_email_and_password(email, password)
       jwt = user['idToken']
       return JSONResponse(content={'token': jwt}, status_code=200)
   except Exception as e:
       return HTTPException(detail={'message': 'Error while Logging In: Invalid Credentials'}, status_code=400)


# ping endpoint
@app.post("/ping")
@limiter.limit("50/minute")
async def validate(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')
    try:
        user = auth.verify_id_token(jwt)
        return user["uid"]
    except Exception as e:
        return HTTPException(detail="Invalid JWT", status_code=400)


# updateUser endPoint
@app.post("/updateUser")
@limiter.limit("50/minute")
async def updateUser(request: Request):
    req = await request.json()
    username = req["username"]
    full_name = req["full_name"]
    email = req["email"]

    if username is None or full_name is None or email is None:
        return HTTPException(detail={'message': 'Error! Missing email or full_name or username'}, status_code=400)

    try:
        uid = await validate(request)
        if(type(uid) != str):
            return HTTPException(detail="Invalid JWT", status_code=400)

        doc = users_ref.document(uid).get()
        if not doc.exists:
            return HTTPException(details={"message": "No document present in users database for uid: " + uid}, status_code=400)
        
        cur_data = doc.to_dict()
        new_data = {
            **cur_data,
            "username": username,
            "full_name": full_name,
            "email": email,
        }

        # If the email is changed, also update the authorization table
        if(email != cur_data['email']):
            user = auth.get_user(uid)
            user = auth.update_user(
                user.uid,
                email=email,
                display_name=username,
            )

        users_ref.document(uid).set(new_data)

        return JSONResponse(content={"message": "Successfully Updated: " + str(new_data)}, status_code=200)
    except Exception as e:
        return HTTPException(detail={'message': 'Error while updating user: ' + str(e)}, status_code=400)


# deleteUser endpoint
@app.delete("/deleteUser")
@limiter.limit("50/minute")
async def deleteUser(request: Request):
    try:
        uid = await validate(request)
        if(type(uid) != str):
            return HTTPException(detail="Invalid JWT", status_code=400)
        
        users_ref.document(uid).delete()
        auth.delete_user(uid)
        return JSONResponse(content={"message": f'Successfully Deleted User: {uid}'}, status_code=200)
    except Exception as e:
        return HTTPException(detail="Deletion of User failed: " + str(e), status_code=400)


# password reset request endPoint
@app.post("/resetPassword")
@limiter.limit("50/minute")
async def resetPassword(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')
    try:
        user = auth.verify_id_token(jwt)
        email = user['email']

        auth.generate_password_reset_link(email)
        return JSONResponse(content={"message": "Password reset link sent to your email address"}, status_code=200) 
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to send password reset link: " + str(e))