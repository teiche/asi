import sys
import time
import atexit
import xmlrpclib
import subprocess

from PySide import QtCore
from PySide import QtGui

from asi import client

class ServiceCouldNotStartError(Exception):
    pass

def spawn_cmdproc(*args):
    """
    Run args as a subprocess in the local command line environment, returning a handle
    to the child process
    Schedule the child to die when the parent does
    """
    child = subprocess.Popen(args)
    atexit.register(child.terminate)

    return child

def spawn_pyfile(fname):
    """
    Run the python file fname in a new child, and schedule the child to die when the parent
    process (the one that calls this function) dies

    Return a handle to the child process
    """
    return spawn_cmdproc('python', fname)

def spawn_ironpyfile(fname):
    """
    Run the ironpython file fname in a new child, and schedule the child to die when the parent
    process (the one that calls this function) dies

    Return a handle to the child process
    """
    return spawn_cmdproc('ipy', fname)

class Service(object):
    """
    This represents an ASI service, such as Manager, Scheduler, or Telescope Controller
    """
    def __init__(self, name, pyname, rpc_func, ironpython=False):
        """
        name is a human readable name for the service
        
        pyname is the name of a python script to run

        rpc_func is a function to call(with no arguments) to open an rpc connection to the
        service

        if ironpython is True, then pyname is executed with ironPython instead of CPython
        """
        self.name = name
        self.pyname = pyname
        self.rpc_func = rpc_func

        self.child = None
        self.rpc = None

        if ironpython:
            self.spawn = spawn_ironpyfile

        else:
            self.spawn = spawn_pyfile

        # This is added later by _create_service_control
        self.startstop_btn = None

    def alive(self):
        """
        Return true if the service is alive, false otherwise
        """
        if self.child and (self.child.poll() is None):
            return True

        return False

    def start(self):
        self.child = self.spawn(self.pyname)
        time.sleep(5)
        self.rpc = self.rpc_func()

        # Make sure it's alive
        if not self.alive():
            raise ServiceCouldNotStartError()

    def stop(self):
        try:
            self.rpc.shutdown()
        except AttributeError:
            print "No shutdown procedure for", self.name
        except xmlrpclib.Fault:
            print "No shutdown procedure for", self.name
            
        self.child.kill()
        
    def kill(self):
        self.rpc = None
        self.child.kill()
        self.child = None

    def update(self):
        if self.startstop_btn and self.alive():
            self.startstop_btn.setStyleSheet("background-color: green")
            self.startstop_btn.setText("Stop")
            return True

        else:
            self.startstop_btn.setStyleSheet("background-color: red")
            self.startstop_btn.setText("Start")
            return False

class ASIControlCenter(QtGui.QWidget):
    def __init__(self, services):
        super(ASIControlCenter, self).__init__()
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Automated Speckle Interferometry Control Center")

        self.services = services
        
        self._init_widgets()

        for service in self.services:
            self._create_service_control(service)

        self.error_message_dialog = QtGui.QErrorMessage(self)  

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()

    def _create_service_control(self, service):
        """
        Create a label and two buttons for each service
        """
        hl = QtGui.QHBoxLayout()

        lbl = QtGui.QLabel(service.name + ':')
        hl.addWidget(lbl)

        def service_startstop_btn_cb():
            if service.alive():
                service.stop()

            else:
                service.start()
        
        startstop_btn = QtGui.QPushButton("Start")
        startstop_btn.clicked.connect(service_startstop_btn_cb)
        startstop_btn.setStyleSheet("background-color: red")
        hl.addWidget(startstop_btn)

        service.startstop_btn = startstop_btn

        log_btn = QtGui.QPushButton("View Log...")
        log_btn.setEnabled(False)
        hl.addWidget(log_btn)

        self.layout.addLayout(hl)
        
    def _init_widgets(self):
        # Start/Stop all
        # Kill All
        hl = QtGui.QHBoxLayout()
        self.startstop_btn = QtGui.QPushButton("Start All")
        self.startstop_btn.setStyleSheet("background-color: red")
        self.startstop_btn.clicked.connect(self.startstop_btn_cb)
        hl.addWidget(self.startstop_btn)

        self.kill_btn = QtGui.QPushButton("Kill All")
        self.kill_btn.setStyleSheet("background-color: yellow")
        self.kill_btn.clicked.connect(self.kill_btn_cb)
        hl.addWidget(self.kill_btn)

        self.layout.addLayout(hl)

    def any_running(self):
        """
        Return true if any services are running
        """
        any_running = False

        for service in self.services:
            any_running = any_running or service.alive()

        return any_running
        
    def startstop_btn_cb(self):
        """
        Start or Stop all services
        """
        if self.any_running():
            for service in self.services:
                service.stop()

        else:
            for service in self.services:
                try:
                    service.start()
                    service.startstop_btn.setStyleSheet("background-color: green")
                    service.startstop_btn.setText("Stop")

                except:
                    self.error_message_dialog.showMessage("An error occured while starting " + service.name + ".  Check the console for more details.")
                    print sys.exc_info()
            
    def kill_btn_cb(self):
        """
        Unsafely kill all services

        Only to be used in times of emergency
        """
        for service in self.services:
            service.kill()

    def update(self):
        self.all_running = True
        
        for service in self.services:
            self.all_running = self.all_running and service.update()

        if self.all_running:
            self.startstop_btn.setStyleSheet("background-color: green")
            self.startstop_btn.setText("Stop All")

        elif self.any_running():
            self.startstop_btn.setStyleSheet("background-color: yellow")
            self.startstop_btn.setText("Stop All")

        else:
            self.startstop_btn.setStyleSheet("background-color: red")
            self.startstop_btn.setText("Start All")

if __name__ == '__main__':
    if not '-s' in sys.argv:
        slider      = Service('Slider', 'usb_stepper_slider.py', client.Slider)
        telescope   = Service('Telescope', 'ascom_telescope.py', client.Telescope)
        scicam      = Service('Science Camera', 'andor_scicam.py', client.ScienceCamera)
        platesolver = Service('PlateSolve3', 'ps3_dllwrap_standalone.py', client.PlateSolve, ironpython=True)
        scheduler   = Service('Scheduler', 'scheduler.py', client.Scheduler)
        runman      = Service('Manager', 'runman.py', client.RunManager)

    else:
        slider      = Service('Slider', 'sim_slider.py', client.Slider)
        telescope   = Service('Telescope', 'sim_telescope.py', client.Telescope)
        scicam      = Service('Science Camera', 'sim_scicam.py', client.ScienceCamera)
        platesolver = Service('PlateSolve3', 'sim_ps3.py', client.PlateSolve)
        scheduler   = Service('Scheduler', 'scheduler.py', client.Scheduler)
        runman      = Service('Manager', 'runman.py', client.RunManager)

    SERVICES = [telescope, scheduler, scicam, platesolver, slider, runman]



    qapp = QtGui.QApplication(sys.argv)
    win = ASIControlCenter(SERVICES)
    win.show()

    sys.exit(qapp.exec_())
    
        

