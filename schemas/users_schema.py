from pydantic import BaseModel


class UserRequestSchema(BaseModel):
    password: str
    username: str
    balance: float


class UserResponseSchema(BaseModel):
    id: str
    username: str
    balance: float


class UserRequestLoginSchema(BaseModel):
    username: str
    password: str
