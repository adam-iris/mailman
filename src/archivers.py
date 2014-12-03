from mailman.interfaces.mailinglist import IListArchiverSet

def archivers(mlist):
  archiver_set = IListArchiverSet(mlist)
  print ', '.join(("{0.name} {0.is_enabled}".format(a) for a in archiver_set.archivers))

