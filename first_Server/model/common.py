from pydantic import BaseModel


class CommReturnObj(BaseModel):
    success: bool = True
    msg: object = None
    data: object = None


class PagedReturnObj(CommReturnObj):
    total: int
