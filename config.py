import ConfigParser

config = ConfigParser.SafeConfigParser()

log = config.read(('/home/alex/speckle/asi/conf/alex_linux.conf',
'C:/Users/alex/asi/conf/alex_win7.conf', '.\conf\alex_win7.conf',
'/Users/amddude/asi/conf/james_osx.conf'))

print "Using log file: ", log


# Logging
log_path = config.get('Logging', 'log_path')

# RPC
scheduler_addr = config.get('RPC', 'scheduler_addr')
telescope_addr = config.get('RPC', 'telescope_addr')
slider_addr = config.get('RPC', 'slider_addr')
scicam_addr = config.get('RPC', 'scicam_addr')
acquiscam_addr = config.get('RPC', 'acquiscam_addr')

# Filters
# Create a dictionary of filter : filter wheel index pairs, starting a 0
filters = dict(map(lambda x: (x[1], x[0]), enumerate(filter(bool, config.get('Filters', 'filters').split(' ')))))

# Focus
science_focus_offset = int(config.get('Focus', 'science_offset'))

# Acquisition
acquiscam_itime = int(config.get('Acquisition', 'itime'))
plate_solve_tries = int(config.get('Acquisition', 'plate_solve_tries'))
scicam_x = int(config.get('Acquisition', 'scicam_x'))
scicam_y = int(config.get('Acquisition', 'scicam_y'))

    




