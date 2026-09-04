from pydantic import BaseModel
from typing import Any
class IngestSchema(BaseModel):
    entity:str
    event:str
    payload:Any
