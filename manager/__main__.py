'''
import xmlrpclib

from runman import RunManager

scheduler = xmlrpclib.ServerProxy("http://localhost:7273", allow_none=True)
telescope = xmlrpclib.ServerProxy("http://localhost:7272", allow_none=True)

rm = RunManager(telescope)

telescope.slew_rel(10, 10)
print "Waiting while busy"
rm._idle_while_busy(telescope)
print "Done!"
'''
