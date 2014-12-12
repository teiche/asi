import os.path
import logging

import config

def init_logging(log_name):
    """
    Initialize the global logging settings for this process, writing log out to logfile

    This results in one log being generated for each module.  These may in the future be combined by having the Python logger send the log events over HTTP POST/GET reponses, or (more likely/stable) a tool will be written to merge the logs based on timestamps.
    """
    log_fmt = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(name)s: %(message)s")
    log_root = logging.getLogger()
    log_root.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(os.path.join(config.log_path, log_name))
    file_handler.setFormatter(log_fmt)
    log_root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_fmt)
    log_root.addHandler(console_handler)   

def sanitize_fault(fs):
    """
    Given a fault string, sanitize it so it can be emitted by a logger
    """
    return ':'.join(fs.replace('{', '(').replace('}', ')').split(':')[1:])
