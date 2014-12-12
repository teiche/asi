import sys

from PySide import QtCore
from PySide import QtGui

import asi

class ASIMonitor(QtGui.QWidget):
    def __init__(self, runman):
        super(ASIMonitor, self).__init__()

        # RPC to the Run Manager
        self.runman = runman
        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Automated Speckle Interferometry Monitor")

        self._init_widgets()
        
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()

    def _init_widgets(self):
        self.pauseresume_btn = QtGui.QPushButton("Pause")
        self.pauseresume_btn.setStyleSheet("background-color: green")
        self.pauseresume_btn.setFixedHeight(150)
        self.pauseresume_btn.clicked.connect(self.pauseresume)
        self.layout.addWidget(self.pauseresume_btn)

        self.step_btn = QtGui.QPushButton("Step")
        self.step_btn.setStyleSheet("background-color: yellow")
        self.step_btn.clicked.connect(self.step)
        self.layout.addWidget(self.step_btn)

        hl = QtGui.QHBoxLayout()
        
        self.step_mode_btn = QtGui.QPushButton("Single Step Mode")
        self.step_mode_btn.setCheckable(True)
        self.step_mode_btn.clicked.connect(self.use_step_mode)
        hl.addWidget(self.step_mode_btn)

        self.auto_mode_btn = QtGui.QPushButton("Automatic Mode")
        self.auto_mode_btn.setCheckable(True)
        self.auto_mode_btn.setChecked(True)
        self.auto_mode_btn.clicked.connect(self.use_auto_mode)
        hl.addWidget(self.auto_mode_btn)
        
        self.layout.addLayout(hl)

        ### Current Target ###
        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        self.layout.addWidget(line)
        
        name_lbl = QtGui.QLabel("Current Target")
        name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.target_lbl = QtGui.QLabel("WDS 00066+03471")
        self.target_lbl.setStyleSheet("font: 18pt;")
        self.target_lbl.setAlignment(QtCore.Qt.AlignCenter)
        
        self.layout.addWidget(name_lbl)
        self.layout.addWidget(self.target_lbl)

        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        self.layout.addWidget(line)

        ### Current Target Status ###

        self.scheduler_lbl = QtGui.QLabel("Request New Target")
        self.scheduler_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.scheduler_lbl.setStyleSheet("color: red")
        
        self.slew_lbl = QtGui.QLabel("Slew To Target")
        self.slew_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.slew_lbl.setStyleSheet("color: red")
        
        self.slider_acq_lbl = QtGui.QLabel("Move Slider to Acquisition Camera")
        self.slider_acq_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.slider_acq_lbl.setStyleSheet("color: red")

        self.acq_lbl = QtGui.QLabel("Take Acquisition Image")
        self.acq_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.acq_lbl.setStyleSheet("color: red")
        
        self.plate_lbl = QtGui.QLabel("Plate Solve Acquisition Image")
        self.plate_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.plate_lbl.setStyleSheet("color: red")
        
        self.slew_offset_lbl = QtGui.QLabel("Slew by Offset")
        self.slew_offset_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.slew_offset_lbl.setStyleSheet("color: red")

        self.slider_sci_lbl = QtGui.QLabel("Move Slider To Science Camera")
        self.slider_sci_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.slider_sci_lbl.setStyleSheet("color: red")
        
        self.autoexpose_lbl = QtGui.QLabel("Autoexpose")
        self.autoexpose_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.autoexpose_lbl.setStyleSheet("color: red")
        
        self.takedata_lbl = QtGui.QLabel("Take FITS Cube")
        self.takedata_lbl.setAlignment(QtCore.Qt.AlignCenter)
        #self.takedata_lbl.setStyleSheet("color: red")

        self.status_labels = [self.scheduler_lbl, self.slew_lbl, self.slider_acq_lbl, self.acq_lbl, self.plate_lbl, self.slew_offset_lbl, self.slider_sci_lbl, self.autoexpose_lbl, self.takedata_lbl]
        
        self.layout.addWidget(self.scheduler_lbl)
        self.layout.addWidget(self.slew_lbl)
        self.layout.addWidget(self.acq_lbl)
        self.layout.addWidget(self.slider_acq_lbl)
        self.layout.addWidget(self.plate_lbl)
        self.layout.addWidget(self.slew_offset_lbl)
        self.layout.addWidget(self.slider_sci_lbl)
        self.layout.addWidget(self.autoexpose_lbl)
        self.layout.addWidget(self.takedata_lbl)

    def pauseresume(self):
        if self.runman.in_auto_mode():
            self.runman.singlestep_mode()
            self.pauseresume_btn.setText("Resume")
            self.pauseresume_btn.setStyleSheet("background-color: red")            

        else:
            self.runman.automatic_mode()
            self.pauseresume_btn.setText("Pause")
            self.pauseresume_btn.setStyleSheet("background-color: green")
        
    def step(self):
        self.runman.step()

    def use_step_mode(self):
        self.auto_mode_btn.setChecked(False)
        self.runman.singlestep_mode()

    def use_auto_mode(self):
        self.step_mode_btn.setChecked(False)
        self.runman.automatic_mode()
        
    def update(self):
        self.target_lbl.setText(self.runman.current_target_name())

        for lbl in self.status_labels:
            lbl.setStyleSheet('background-color: lightgray')
        
        self.step_btn.setEnabled(self.runman.ready_to_step() and (not self.auto_mode_btn.isChecked()))

        curstep = self.runman.get_current_actions()
        print 'UPDATE', curstep
        getattr(self, curstep + '_lbl').setStyleSheet('background-color: yellow')

            
if __name__ == '__main__':
    qapp = QtGui.QApplication(sys.argv)
    win = ASIMonitor(asi.client.RunManager())
    win.show()

    sys.exit(qapp.exec_())
    
        

