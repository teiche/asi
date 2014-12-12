import time

import asi

x = asi.client.Scheduler()

while 1:
    time.sleep(1)
    print x.get_next_target()[0]
    print x.target_success()
