import ConfigParser

config = ConfigParser.SafeConfigParser()

#log = config.read((r'C:\Users\Russ\asi\conf\alex_linux.conf'))
'''
'/home/alex/speckle/asi/conf/alex_linux.conf',
'C:/Users/alex/Desktop/asi/conf/alex_win7.conf', '.\conf\alex_win7.conf',
                   '/Users/amddude/asi/conf/james_osx.conf', 'C:\Users\Russ\asi\conf\alex_win7_.conf'))
'''
print 'conf'
log = config.read('/home/alex/speckle/asi/conf/alex_linux.conf')

print "Using log file: ", log

print "Using log file: ", log


# Logging
log_path = config.get('Logging', 'log_path')

# RPC
scheduler_addr = config.get('RPC', 'scheduler_addr')
telescope_addr = config.get('RPC', 'telescope_addr')
slider_addr = config.get('RPC', 'slider_addr')
scicam_addr = config.get('RPC', 'scicam_addr')
acquiscam_addr = config.get('RPC', 'acquiscam_addr')
platesolve_addr = config.get('RPC', 'platesolve_addr')
runman_addr = config.get('RPC', 'runman_addr')

# Filters
# Create a dictionary of filter : filter wheel index pairs, starting a 0
filters = dict(map(lambda x: (x[1], x[0]), enumerate(filter(bool, config.get('Filters', 'filters').split(' ')))))

# Focus
science_focus_offset = int(config.get('Focus', 'science_offset'))

# Acquisition
# Integration time to use when taking an image for plate solving
acquiscam_itime = int(config.get('Acquisition', 'itime'))
# The number of times a given spot in the sky is imaged and plate solved before the target is 
# skipped
plate_solve_tries = int(config.get('Acquisition', 'plate_solve_tries'))
# The location of the center of the science camera within the 
# acquisition camera, relative to the center of the acquisition camera
scicam_x = int(config.get('Acquisition', 'scicam_x'))
scicam_y = int(config.get('Acquisition', 'scicam_y'))
# The maximum distance(in degrees) that the target can be from the center of field
ra_err = float(config.get('Acquisition', 'ra_err'))
dec_err = float(config.get('Acquisition', 'dec_err'))
acquiscam_tempdir = config.get('Acquisition', 'tempdir')
acquiscam_tempfile = config.get('Acquisition', 'tempfile')
    
# Slider
slider_motor_id = int(config.get('Slider', 'motor_id'))
slider_acquis_pos = int(config.get('Slider', 'acquis_pos'))
slider_sci_pos = int(config.get('Slider', 'sci_pos'))


