from sqlalchemy import Column, String, Integer, Float

from app.database import Base


class ParsingSource(Base):
    __tablename__ = 'parsing_sources'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    xpath = Column(String, nullable=False)
    avg_price = Column(Float, nullable=True)