import sys
import math

from asi import db
from asi.db import catalog


HIP_ASCII_FNAME = 'hip_ascii'

def hms_to_deg(hms):
    hours, minutes, seconds = hms.split(':')

    return float(int(hours)*15) + (float(minutes)/4.0) + (float(seconds)/240.0)

def dms_to_deg(dms):
    degrees, minutes, seconds = dms.split(':')

    print degrees, minutes, seconds
    
    return math.copysign(abs(int(degrees)) + (int(minutes)/60.0) + (float(seconds)/3600.0), int(degrees))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: build_hip_catalog.py [path-to-hip_ascii]'
        sys.exit(-1)

    print "Removing all existing reference stars..."
    connection = db.engine.connect()
    connection.execute('TRUNCATE TABLE refstars;')
           
    #print "Extracting HIP stars from binary file..."
    #os.system('scat {path} -d 0-118218 > {hip_ascii}'.format(path=sys.argv[1], 
    #                                                      hip_ascii=HIP_ASCII_FNAME))

    print "Opening ASCII HIP File..."
    stars = open(HIP_ASCII_FNAME, 'r').readlines()

    
    count = 0
    total = float(len(stars))
    
    perc = 0

    sess = db.Session()
    
    for line in stars:        
        count += 1.0
        
        name = 'HIP' + line[0:6]
        ra_deg = float(line[7:19].strip())
        dec_deg = float(line[19:32].strip())
        magv = float(line[33:40].strip())
        magb = float(line[40:46].strip())
        stype = line[61:63].strip()

        hip = catalog.ReferenceStar(
            name=name,
            ra_deg=ra_deg,
            dec_deg=dec_deg,
            magv=magv,
            magb=magb,
            stype=stype)

        sess.add(hip)
        sess.commit()
        
        del hip

        progdeg = count / total
        operc = perc
        perc = round(100*progdeg, 1)

        if (perc != operc):
            status = '=' * int(.7 * perc) + '>'
            status += ' '*(70 - len(status))
            sys.stdout.write("\r |{status}| {perc}%".format(status=status, perc=perc))

    print
    print "Total Stars: ", count
