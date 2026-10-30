from app.db.base import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Specialization(Base):
    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True,)
    description: Mapped[str | None] = mapped_column(Text, nullable=True,)

    doctors = relationship("DoctorProfile", back_populates="specialization",)