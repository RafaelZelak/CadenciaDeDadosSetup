import random

from worker import caoe
from worker.loop import work as loop_work
from worker.coroutine import work as coroutine_work
from worker.thread import work as thread_work
from worker.process import work as process_work
from worker.celery import work as celery_work

worker_map = {
    'loop': loop_work,
    'coroutine': coroutine_work,
    'thread': thread_work,
    'process': process_work,
    'celery': celery_work
}

# caoe.install()


class Worker:
    def __init__(self, mode='thread'):
        self.mode = mode
        self.worker_func = worker_map.get(self.mode, thread_work)

    def work(self, data, info):
        return self.worker_func(data, info)


# async def worker_do_sth(data, info):
def worker_do_sth(data, info):
    i = random.randint(1, 10)
    print(data, '???/')
    # if i % 2 == 0:
    # test()
    return 'haha'


def test():
    raise Exception('test')


if __name__ == '__main__':
    data = [
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
        'u1', 'u2', 'u3', 'u4',
    ]
    info = {
        'worker': 'worker.worker.worker_do_sth',
        'chunk_size': 2

    }
    # worker = Worker(mode='coroutine')
    # worker = Worker(mode='loop')
    worker = Worker(mode='thread')
    # worker = Worker(mode='process')
    resp = worker.work(data, info)
    print(resp)
