from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from base import Base

class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, primary_key=True)

    filename = Column(String(255))
    star_id = Column(Integer, ForeignKey('doublestars.id'))
    star = relationship("DoubleStar", backref='observations')

    ref_filename = Column(String(255))
    ref_id = Column(Integer, ForeignKey('refstars.id'))
    ref_star = relationship("ReferenceStar", backref='observations')

    datetime = Column(DateTime)

    emgain = Column(Integer) #ANDOR camera EM gain
    itime = Column(Float)    #ANDOR camera integration time
    roi_width = Column(Integer)     #Frame width in pixels
    roi_height = Column(Integer)    #Frame height in pixels
    
    requester = Column(String(200), nullable=True)

    band = Column(String(2))
    ra_deg = Column(Float)
    dec_deg = Column(Float)

