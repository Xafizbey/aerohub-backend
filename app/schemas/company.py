from datetime import datetime

from pydantic import BaseModel


class CompanySettingsOut(BaseModel):
    id: int
    airline_name: str
    logo_path: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanySettingsUpdate(BaseModel):
    airline_name: str | None = None
