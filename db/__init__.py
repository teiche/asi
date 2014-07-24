### The following handles creating one engine and Session instance for the app ###
import logging
logger = logging.getLogger(__name__)

import sqlalchemy
from sqlalchemy.orm import sessionmaker

DB_ADDR_STRING = 'mysql+mysqlconnector://speckle_user:lebenswelt@localhost:3306/speckle'

logger.info("Connecting to database at " + DB_ADDR_STRING)

engine = sqlalchemy.create_engine(DB_ADDR_STRING)

Session = sessionmaker(bind=engine)

### Begin some normal __init__ stuff ###
import catalog
import targetlist
import runlog
