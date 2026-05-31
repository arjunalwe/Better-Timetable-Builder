import requests
from __future__ import annotations
from redis import Redis
from rq import Queue

q = Queue(connection=Redis())
