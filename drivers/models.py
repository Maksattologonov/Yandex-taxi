from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd


class DriverProfile(BaseModel):
    first_name: str
    id: str
    last_name: str
    park_id: str
    work_rule_id: str
    work_status: str


class Account(BaseModel):
    balance: float
    id: str


class Car(BaseModel):
    callsign: Optional[str] = None
    id: Optional[str] = None
    vin: Optional[str] = None


class CurrentStatus(BaseModel):
    status: str


class DriverProfiles(BaseModel):
    updated_at: datetime
    accounts: List[Account]
    car: Optional[Car] = None
    driver_profile: DriverProfile
    current_status: CurrentStatus
