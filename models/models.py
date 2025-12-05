from sqlalchemy import Column, Integer, String, BigInteger

from database.database import Base


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    population = Column(BigInteger)
    region = Column(String)
