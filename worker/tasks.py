from celery import Celery
app = Celery('tasks', backend = 'cache+memcached://127.0.0.1:11211/', broker='amqp://guest:guest@localhost:5672//')
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)

@app.task(ignore_result=True)
def parse_handhistory(fileName):
    print ('pretending to parse ' + fileName)
