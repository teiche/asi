import os
import sys
import urllib

from asi import db
from asi.db import catalog

WDS_TXT_URL = 'http://ad.usno.navy.mil/wds/Webtextfiles/wdsweb_summ.txt'

"""
Reproduced from: http://ad.usno.navy.mil/wds/Webtextfiles/wdsweb_format.txt

    COLUMN     Format                     DATA
    --------   ------         ----------------------------
    1  -  10   A10             2000 Coordinates
    11 -  17   A7              Discoverer & Number
    18 -  22   A5              Components
    24 -  27   I4              Date (first)
    29 -  32   I4              Date (last)
    34 -  37   I4              Number of Observations (up to 9999)
    39 -  41   I3              Position Angle (first - XXX)
    43 -  45   I3              Position Angle (last  - XXX)
    47 -  51   F5.1            Separation (first)
    53 -  57   F5.1            Separation (last)
    59 -  63   F5.2            Magnitude of First Component
    65 -  69   F5.2            Magnitude of Second Component
    71 -  79   A9              Spectral Type (Primary/Secondary)
    81 -  84   I4              Primary Proper Motion (RA)
    85 -  88   I4              Primary Proper Motion (Dec)
    90 -  93   I4              Secondary Proper Motion (RA)
    94 -  97   I4              Secondary Proper Motion (Dec)
    99 - 106   A8              Durchmusterung Number
   108 - 111   A4              Notes
   113 - 130   A18             2000 arcsecond coordinates
"""

def nullfail(func):
    """
    Return a function that returns func(x), but if func(x) throws an exception return None
    """
    def f(x):
        try:
            return f(x)

        except:
            return None

    return f

nfloat = nullfail(float)
nint   = nullfail(int)    

def ra2deg(ra):
    hr = float(ra[0:2])
    mn = float(ra[2:4])
    sc = float(ra[4:])

    return 15.0*hr + mn/4.0 + sc/240.0

def dec2deg(dec):
    deg = float(dec[0:2])
    mn = float(dec[2:4])
    sc = float(dec[4:])

    return deg + mn/60.0 + sc/3600.0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: build_wds_catalog.py --fetch'
        print '       build_wds_catalog.py [path_to_wds.txt_on_disk]'
    
    if '--fetch' in sys.argv:
        print "Fetching WDS TXT File from the USNO..."
        print "This may take several minutes."
        wds = urllib.urlopen(WDS_TXT_URL)

    else:
        print "Opening WDS TXT file from disk..."
        wds = open(sys.argv[1], 'r')
        
    wds_lines = wds.readlines()


    total = float(len(wds_lines))
    skipped = 0
    added = 0.0

    perc = 0

    print "Adding WDS stars to MySQL Database..."

    sess = db.Session()
    
    for line in wds_lines:
        coord = line[0:10].strip()
        disc = line[10:17].strip()
        comp = line[17:22].strip()
        fstdate = int(line[23:27])
        lstdate = int(line[28:32])
        nobs = int(line[33:37])
        fstpa = int(line[38:41])
        lstpa = int(line[42:45])
        fstsep = nfloat(line[46:51])
        lstsep = nfloat(line[52:57])
        fstmag = nfloat(line[58:63])
        secmag = nfloat(line[64:69])
        stype = line[70:79].strip()
        pm1ra = nint(line[80:84])
        pm1dc = nint(line[84:88])
        pm2ra = nint(line[89:93])        
        pm2dc = nint(line[93:97])
        dnum = line[98:106].strip()
        notes = line[107:111].strip()
        acoord = line[112:130].strip()
        
        # Calculate decimal equivalents of RA and Dec
        # Easier to query
        try:
            ra = acoord[0:9]
            ra_deg = ra2deg(ra)
                
            dec = acoord[9:]
            dec_deg = dec2deg(dec)

        except ValueError:
            print "\rWDS{crd} is missing precise coordinates(WDS field acoord).  Skipping...   ".format(crd=coord)

            skipped += 1
            perc = 0 # guarantee a redraw of the status bar
            continue
        
        wds = catalog.DoubleStar(catalog='WDS',
                  name=coord + '-' + disc + '-' + comp,
                  coord=coord,
                  disc=disc,
                  comp=comp,
                  fstdate=fstdate,
                  lstdate=lstdate,
                  nobs=nobs,
                  fstpa=fstpa,
                  lstpa=lstpa,
                  fstsep=fstsep,
                  lstsep=lstsep,
                  fstmag=fstmag,
                  secmag=secmag,
                  stype=stype,
                  pm1ra=pm1ra,
                  pm1dc=pm1dc,
                  pm2ra=pm2ra,
                  pm2dc=pm2dc,
                  dnum=dnum,
                  notes=notes,
                  acoord=acoord,
                  ra_deg=ra_deg,
                  dec_deg=dec_deg)

        sess.add(wds)
        sess.commit()
        
        added += 1.0

        progdec = (added + skipped) / total
        operc = perc
        perc = round(100 * progdec, 1)
        
        if (perc != operc):
            status = '=' * int(.7 * perc) + '>'
            status += ' '*(70 - len(status))
            sys.stdout.write("\r |{status}| {perc}%".format(status=status, perc=perc))
            sys.stdout.flush()

    print "{added} WDS stars were added to the MySQL database.".format(added=added)
    print "{skipped} were incomplete and were skipped.".format(skipped=skipped)
