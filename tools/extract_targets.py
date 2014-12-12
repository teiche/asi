import time

import asi.db
from asi.db.catalog import DoubleStar

#RA: 300 - 60 degrees RA

#RA_LOW = 
#RA_HIGH = 300
DEC_LOW = -10
DEC_HIGH = 50
MAX_SEC_MAG = 9.0
MIN_NUMBER_OBS = 0
LST_SEP_MIN = 5
LST_SEP_MAX = 100

DELTA_MAG_MAX = 2.0

if __name__ == '__main__':
    sess = asi.db.Session()

    doubles = sess.query(DoubleStar).filter(
    DoubleStar.ra_deg >= 300,
    DoubleStar.dec_deg <= DEC_HIGH,
    DoubleStar.secmag <= MAX_SEC_MAG,
    DoubleStar.nobs >= MIN_NUMBER_OBS,
    DoubleStar.lstsep >= LST_SEP_MIN,
    DoubleStar.lstsep <= LST_SEP_MAX,
        DoubleStar.dec_deg >= DEC_LOW).all()

    doubles2 = sess.query(DoubleStar).filter(
    DoubleStar.ra_deg <= 60,
    DoubleStar.dec_deg <= DEC_HIGH,
    DoubleStar.secmag <= MAX_SEC_MAG,
    DoubleStar.nobs >= MIN_NUMBER_OBS,
    DoubleStar.lstsep >= LST_SEP_MIN,
    DoubleStar.lstsep <= LST_SEP_MAX,
        DoubleStar.dec_deg >= DEC_LOW).all()
    
    all_doubles = doubles + doubles2

    all_doubles = filter(lambda d: abs(d.fstmag - d.secmag) <= 2.0, all_doubles)
    
    #print len(all_doubles)
    #for d in all_doubles:
    #    print d

    #time.sleep(1)
    
    for d in all_doubles:
        print d.name, ", WDS, i, 3, ATEICHE, 0, 0, 0"
       



