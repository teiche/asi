import asi.db

from asi.db.catalog import DoubleStar
from asi.db.targetlist import Target


sess = asi.db.Session()
ds = sess.query(DoubleStar).filter_by(id=133).first()
print ds

t = Target(star_id=ds.id, bands='B v i')
print t

sess.add(t)
sess.commit()

#t.star
q = t.star
print '---'
print q
print t.bands









