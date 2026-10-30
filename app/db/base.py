from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from app.models.clinic import Clinic
from app.models.user import User
from app.models.profile import DoctorProfile, PatientProfile
from app.models.specialization import Specialization
from app.models.schedule import DoctorSchedule