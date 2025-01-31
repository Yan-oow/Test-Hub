from pydantic import BaseModel


class UserInfo(BaseModel):
    userNT: str
    customerList: list[str]


class LoginUser(BaseModel):
    nt: str
    email: str
    full_name: str
    full_name_with_department: str
    disabled: bool = False
    department: str
    role: str = 'user'
    permission_list: list = []
