from fastapi import HTTPException,Response,Request,status

from pymongo.errors import DuplicateKeyError

from core.config import ACCESS_TOKEN_MINUTES, COOKIE_SECURE
from core.csrf import set_csrf_cookie,verify_csrf
from core.security import create_access_token,verify_password,decode_access_token,hash_password
from models.user import create_user_document,serialize_user

async def set_auth_cokkies(response:Response,user_id:str):
      token=create_access_token(user_id)

      response.set_cookie(
              key="access_token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_MINUTES * 60,

      )

      
  

async def get_csrf_token(response:Response):
      token =set_csrf_cookie(response)
      print({"csrf token is":token})
      return {"csrf_token": token}

async def register_user(data,response:Response,request:Request):
      await verify_csrf(request)

      db=request.app.state.db
      email=str(data.email).lower()

      document=create_user_document(
            name=data.name.strip(),
            email=email,
            hashed_password=hash_password(data.password)
      )
      try: 

            result= await db["user"].insert_one(document)


      except DuplicateKeyError:
            raise HTTPException(
                  status_code=status.HTTP_409_CONFLICT,
                  detail="An account this emial already be there" ,
            )
      user_id=str(result.inserted_id)
      await set_auth_cokkies(response,user_id)

      return {
        "id": user_id,
        "name": document["name"],
        "email": document["email"],
    }


async def login_user(data,response:Response,request:Request):
      await verify_csrf(request)

      db=request.state.app.db
      email=str(data.email).lower()
      user=db["user"].find_one({"email":email})

      if not user or not verify_password(data.password,db["hash_password"]):
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                               detail="Invalid email or password",)
       
      await set_auth_cokkies(response,str(user["_id"]))
      return serialize_user(user)


async def get_me(user: dict):
    return serialize_user(user)



async def logout_user(request:Request,response:Response):
       await verify_csrf(request)

       response.delete_cookie(
        key="access_token",
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )

       response.delete_cookie(
        key="csrf_token",
        path="/",
        secure=COOKIE_SECURE,
        httponly=False,
        samesite="lax",
    )

       return {"message": "Logged out successfully"}














