from celery import Celery

app = Celery('worker', include=[
    'worker.celery_demo_tasks',
    'test.functional.test_celery',
])
app.config_from_object('worker.celeryconfig')

if __name__ == '__main__':
    app.start()
