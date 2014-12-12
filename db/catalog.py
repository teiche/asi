from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship, backref

from base import Base

class DoubleStar(Base):
    __tablename__ = 'doublestars'

    id = Column(Integer, primary_key=True)
    
    # A human identifier for the catalog this came from(e.g. WDS)
    catalog = Column(String(200))
    # A unique name for the double star
    # In the case of a WDS star, this is {coord}-{disc}-{comp}, the only unique identifier
    name = Column(String(200))

    # The rest of the fields are optional other than ra_deg, dec_deg
    # They mirror the WDS fields, but should cover the range of all things relevant to a double star
    # Doubles from different(non-WDS) sources will simply ignore unused fields
    coord = Column(String(10))
    disc = Column(String(10))
    comp = Column(String(7))
    fstdate = Column(Integer)
    lstdate = Column(Integer)
    nobs = Column(Integer)
    fstpa = Column(Integer)
    lstpa = Column(Integer)
    fstsep = Column(Integer)
    lstsep = Column(Integer)
    fstmag = Column(Integer)
    secmag = Column(Integer)
    stype = Column(String(9))
    pm1ra = Column(Integer)
    pm1dc = Column(Integer)
    pm2ra = Column(Integer)
    pm2dc = Column(Integer)
    dnum = Column(String(8))
    notes = Column(String(4))
    acoord = Column(String(18))
    ra_deg = Column(Float)
    dec_deg = Column(Float)

    # Target one-to-many mapping
    # At load-time this is enforced to be one-to-one or one-to-zero
    #targets = relationship("Target", backref="DoubleStar")
    
    def __repr__(self):
        return '<({obj}) WDS'.format(obj=self.__class__.__name__) + self.name + '>'

class ReferenceStar(Base):
    __tablename__ = 'refstars'

    # Unique ID to the ASI database
    id = Column(Integer, primary_key=True)

    # Unique star ID from catalog(HIP Number, etc)
    name = Column(String(200))

    # RA in degrees
    ra_deg = Column(Float)

    # Dec in degrees
    dec_deg = Column(Float)

    # B-band magnitude
    magb = Column(Float)

    # B-band magnitude
    magv = Column(Float)

    # Spectral type
    stype = Column(String(2))

    def __repr__(self):
        return '<({obj}) {name}>'.format(obj=self.__class__.__name__, name=self.name)
