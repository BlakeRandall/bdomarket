from typing import List
from threading import main_thread, Thread
from market import web_app
from gevent.pywsgi import WSGIServer

count = 0
terminate = False

def web(*args, **kwargs):
    while main_thread().is_alive() and not terminate:
        wsgi_server = WSGIServer(
            listener=':8080',
            application=web_app
        )
        wsgi_server.serve_forever()

threads: List[Thread] = []

web_thread = Thread(
    name='web',
    target=web,
    daemon=True
)

threads.extend([web_thread])

for thread in threads:
    thread.start()

while main_thread().is_alive() and count <= 3:
    terminate = any(not thread.is_alive() for thread in threads)

    if terminate:
        count += 1

    for thread in threads:
        if thread.is_alive():
            thread.join(60)