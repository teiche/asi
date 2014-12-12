import os
import sys
import time
import atexit
import subprocess

from asi import client

def spawn_pyfile(fname):
    """
    Run the python file fname in a new child, and schedule the child to die when the parent
    process (the one that calls this function) dies

    Return a handle to the child process
    """
    child = subprocess.Popen(('python', fname))
    atexit.register(child.terminate)

    return child

if __name__ == '__main__':
    if '-s' in sys.argv or '--simulate' in sys.argv:    
        print "Starting PS3"    
        ps3 = spawn_pyfile('sim_ps3.py')
        
        print "Starting Slider"
        slider    = spawn_pyfile('sim_slider.py')
        print "Starting Telescope"
        telescope = spawn_pyfile('sim_telescope.py')
        print "Starting Scicam"
        scicam    = spawn_pyfile('sim_scicam.py')
        print "Starting Acquiscam"
        acqcam    = spawn_pyfile('sim_acquisition.py')

    else:

        slider = spawn_pyfile('slider.py')
        telescope = spawn_pyfile('telescope.py')
        scicam = spawn_pyfile('scicam.py')
        acqcam = spawn_pyfile('acquisition.py')

    print "Starting Scheduler"
    scheduler = spawn_pyfile('scheduler.py')


    time.sleep(10)

    print "Starting Runman"
    runman    = spawn_pyfile('runman.py')

    # Do nothing
    while True:
        time.sleep(3600)
    
    
    
