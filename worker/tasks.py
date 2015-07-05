from celery import Celery
import os
from parsing.fileparser import FileParser

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)


@app.task(ignore_result=True)
def parse_hand_history(file_name):
    # dev hack
    path = os.path.abspath('../webserver/uploads/')
    fp = FileParser(path, file_name)
    fp.parse()
