from pydantic import BaseModel, Field
class obdresult(BaseModel):
    data_required_choice: list = []
    selected_data: list = []
    Data:list = []



