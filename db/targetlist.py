from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from base import Base

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    
    # star and bands are required fields, the rest are optional(they have default values)
    
    # Reference to the star to be observed
    #star_id = Column(Integer, ForeignKey('doublestars.id'), nullable=False)
    star = relationship("DoubleStar")
    star_id = Column(Integer, ForeignKey('doublestars.id'))

    # The filter band(only one) to observe the target in
    band = Column(String(2), nullable=False)
    
    # Priority
    # 0 is "Will not be observed"
    # 5 is "Only other stars with priority 5 may be observed before this one"
    # 3 is normal, and 2 and 4 are relatively levels of priority
    # 2, 3, 4 do not enforce a strict order, they just provide a means to choose when all other
    # things are relatively equal

    NEVER = 1
    LOW = 2
    NORMAL = 3
    HIGH = 4
    NOW = 5
    
    PRIORITY_CHOICES = (
        (NEVER, 'Never'),
        (LOW, 'Low'),
        (NORMAL, 'Normal'),
        (HIGH, 'High'),
        (NOW, 'Now'))
    
    priority = Column(Integer, nullable=True, default=3)
    
    # The astronomer that requested this star be observed
    requester = Column(String(200), nullable=True)
    
    # Measurements Per Observation
    # This is the number of FITS cubes to collect each time the scheduler selects this target
    # to be observed
    # It is used, for instance, to observe a well known binary 10+ times in a row for calibration
    mpo = Column(Integer, default=1)

    # Maximum delta-t (hours)
    # The maximum number of hours permissible between two observations of this object
    maxdt = Column(Integer, default=1)

    # Minimum delta-t (hours)
    # The minimum number of hours permissible between two observations of this object
    mindt = Column(Integer, default=12)

    def __unicode__(str):
        return unicode(self.star)
