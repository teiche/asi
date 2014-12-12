import sys
from math import degrees


if 'IronPython' not in sys.version:
    print("PlateSolve3 objects rely on the Microsoft CLR, and thus can only be used from within IronPython")
    sys.exit()

import clr
#clr.AddReferenceToFileAndPath(r'C:\Users\alex\Desktop\PS3DLLExample\PS3DLLExample\bin\Debug\SRSLib.dll')
clr.AddReferenceToFileAndPath(r'C:\Users\Russ\asi\PlateSolve3SRS\SRSLib.dll')

import SRSLib

def rad2sec(rad):
    return degrees(rad) * 3600.

SRSLib.MatchLib.SetCatalogLocation(r'C:\Users\Russ\Documents\PS3\PS3Cats')


if not SRSLib.MatchLib.VerifyCatalog():
    print("PlateSolve3 Catalogs did not verify correctly.")
    sys.exit()

#TODO: Nondefault parameters
SRSLib.MatchLib.SetParms(500, 10, 2, 3, 60, 6500, 2014.5, 0.0)

plate = SRSLib.MatchLib.PlateListType()

#  = SRSLib.MatchLib.PlateSolveAnyFile(fname, xsize, ysize, ra, dec, 0)
success, xsize, ysize, ra, dec, rot, plate = SRSLib.MatchLib.PlateSolveFilePlateList(r'C:\Users\Russ\Desktop\PS3Failure\test.fit', 0, 0, 100, 100, 0, plate)

print success
print plate
print dir(plate)

xpix, ypix = 0, 0
x = SRSLib.MatchLib.TransformPlateToJ2000(plate.Xform, 50, 30, xpix, ypix)

print x
print xpix
print ypix

print 'xsize', xsize
print 'ysize', ysize
print 'ra', ra
print 'dec', dec
print 'rot', rot

