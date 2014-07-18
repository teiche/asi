import logging
logger = logging.getLogger(__name__)

from asi.db import base, engine

if __name__ == '__main__':    
    logger.info("Creating tables...")
    base.Base.metadata.create_all(engine)
