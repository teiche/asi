import sys

from asi import db
from asi.db.catalog import DoubleStar
from asi.db.targetlist import Target
from asi import config


def fetch_double(session, name, cat=None):
    if cat:
        return session.query(DoubleStar).filter(DoubleStar.name.contains(name), DoubleStar.catalog == cat).all()

    else:
        return session.query(DoubleStar).filter(DoubleStar.name.contains(name)).all()
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: load_targets.py [path-to-targets.csv]'
        sys.exit()

    # Get a database connection
    session = db.Session()

    '''
    # Try to connect to the filter wheel to get a list of supported filters
    try:
        fw = lebenswelt.client.FilterWheel()
        supported_filters = fw.get_filters()

    except:
        supported_filters = []
    '''
        
    lines = open(sys.argv[1], 'r').readlines()

    # The number of targets added
    added = 0

    for i, line in enumerate(lines):
        # In case the user left off the end fields completely, pad it with empty values
        line = line.replace('\n', '') + ',,,,,,,'

        # Convert '' to None so it gets entered as a NULL in the database
        name, cat, band, priority, requester, mpo, maxdt, mindt = [x if x != '' else None for x in line.split(',')[0:8]]

        if not band in config.filters:
            print "ERROR({l}): In double {dbl}, the filter band {filt} is not supported.  Target skipped...".format(l=i, dbl=name, filt=band)
            
        dbl = fetch_double(session, name, cat)
        if len(dbl) > 1:
            print "ERROR({l}): More than one double matches {dbl}".format(l=i, dbl=name)
            print "    ", line
            print "     The following doubles all match:"
            for d in dbl:
                print "        ", d

        elif len(dbl) == 0:
            print "WARNING({l}): No doubles found matching {dbl}".format(l=i, dbl=name)

        else:
            # 1 double was found, so add it!
            dbl = dbl[0]            

            # Check to see if a target already exists for this double
            # If so, we delete it and replace it with the new one after issuing a warning
            existing = session.query(Target).filter_by(star=dbl, band=band).all()
            if len(existing) == 1:
                print "WARNING({l}): {dbl} is already in the target list.  Its properties have been updated.".format(l=i, dbl=dbl)

                session.delete(existing[0])

            elif len(existing) > 1:
                print "SERIOUS ERROR({1}): {dbl} exists in the target list more than once.  This is a serious error, and should be reported to Alex Teiche."
                print "    All instances of this star in the target list have been deleted, and replaced with the newest entry."
                for d in existing:
                    session.delete(d)

            # Commit the delete, if applicable
            session.commit()
                              
            # Add the new target
            target_kwargs = {
                'star' : dbl,
                'band' : band,
                'priority' : priority,
                'requester' : requester,
                'mpo' : mpo,
                'maxdt' : maxdt,
                'mindt' : mindt}
            
            # Filter out None fields so the Django defaults are used instead
            target_kwargs = dict(filter(lambda di: di[1] is not None, target_kwargs.items()))                        
            target = Target(**target_kwargs)
            session.add(target)
            session.commit()

            added += 1
        
    print "{0} targets added.".format(added)
