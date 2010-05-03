import thread

POOL = []

# map session to implementation and name
MAP = {}
MAPMUTEX = thread.allocate_lock()
