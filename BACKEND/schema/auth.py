from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(str_strip_whitespace=True)
    #Its purpose is to automatically remove leading and trailing whitespace from string fields in a Pydantic model.
    #model_config is a special class attribute used to define configuration settings for a Pydantic model.


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class CsrfResponse(BaseModel):
    csrf_token: str