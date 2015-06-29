from celery import Celery
app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)

@app.task(ignore_result=True)
def parse_handhistory(fileName):
    print ('pretending to parse ' + fileName)
