from copy import deepcopy

from worker.celery import work
from worker.celery_app import app
from worker.worker import Worker


@app.task(bind=True)
def test(self, data, info):
    print(data, '1111')
    print(info, '1111')
    sub_info = deepcopy(info)
    sub_info['chunk_size'] = info['sub_chunk_size']
    sub_info['worker'] = info['sub_worker']

    worker = Worker(mode='thread')
    resp = worker.work(data, sub_info)


def worker_do_sth(data, info):
    print(data, '2222')
    print(info, '2222')


if __name__ == '__main__':
    work(data=['a', 'b', 'c', 'd',
               1, 2, 3, 4, 5, 6, 7, 8],
         info={
             'worker': 'worker.celery_demo_tasks.test',
             'sub_worker': 'worker.celery_demo_tasks.worker_do_sth',
             'max_workers': 2,
             'chunk_size': 2,
             'sub_chunk_size': 1,
         })
