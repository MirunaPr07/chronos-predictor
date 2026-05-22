from celery import shared_task
from collectors.thread_manager import ThreadManager

# we keep a single thread manager at module level,
# so that we don't create new threads on every task call
_manager = None

def get_manager() -> ThreadManager:
    # we initialize the manager only once and reuse it
    global _manager
    if _manager is None:
        _manager = ThreadManager()
    return _manager

@shared_task
def collect_all_sources():
    # this task gets called by celery beat every 30 seconds
    manager = get_manager()
    if not any(c.is_running for c in manager.collectors):
        # threads aren't running yet, so we start them all
        manager.start_all()
        return "collectors started"
    # threads are running, so we return the queue size
    status = manager.status()
    return f"collectors running - queue size: {status['queue_size']}"

@shared_task
def stop_all_sources():
    # we use this to cleanly shut down all threads 
    manager = get_manager()
    manager.stop_all()
    return "all collectors stopped"

@shared_task
def get_collector_status():
    # returns a snapshot of all running threads: useful for monitoring
    manager = get_manager()
    return manager.status()