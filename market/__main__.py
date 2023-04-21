from typing import List
from threading import main_thread, Thread
from time import sleep
from market import web_app, worker_app
from gevent.pywsgi import WSGIServer
from schedule import run_pending, idle_seconds, next_run, every

count = 0
terminate = False

def web(*args, **kwargs):
    while main_thread().is_alive() and not terminate:
        wsgi_server = WSGIServer(
            listener=':8080',
            application=web_app
        )
        wsgi_server.serve_forever()

def worker(*args, **kwargs):
    every(1).minute.at(':00').do(worker_app)
    while main_thread().is_alive() and not terminate:
        sleep(idle_seconds() or 1)
        run_pending()

threads: List[Thread] = []

web_thread = Thread(
    name='web',
    target=web,
    daemon=True
)

worker_thread = Thread(
    name='worker',
    target=worker,
    daemon=True
)

threads.extend([web_thread, worker_thread])

for thread in threads:
    thread.start()

while main_thread().is_alive() and count <= 3:
    terminate = any(not thread.is_alive() for thread in threads)

    if terminate:
        count += 1

    for thread in threads:
        if thread.is_alive():
            thread.join(60)