from typing import List, Optional
from pydantic import BaseModel


class Account(BaseModel):
    id: Optional[str] = None
    balance: Optional[float] = None


class Car(BaseModel):
    id: Optional[str] = None
    callsign: Optional[str] = None
    vin: Optional[str] = None


class CurrentStatus(BaseModel):
    status: Optional[str] = None


class DriverProfile(BaseModel):
    id: Optional[str] = None
    park_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    work_rule_id: Optional[str] = None
    work_status: Optional[str] = None


class Driver(BaseModel):
    account: Optional[Account] = None
    car: Optional[Car] = None
    current_status: Optional[CurrentStatus] = None
    driver_profile: Optional[DriverProfile] = None