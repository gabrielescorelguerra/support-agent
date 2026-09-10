from pydantic import BaseModel


class SupportClassification(BaseModel):
    classification: str
    message: str
    route: str