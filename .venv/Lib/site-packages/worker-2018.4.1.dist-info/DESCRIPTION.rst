=============================
worker
=============================

simple worker

**Note**: this package is still in alpha. Use with caution !


Quickstart
----------

Install worker::

    pip install worker


Use worker:

.. code-block:: python

    data = [
               {'hello': 'world'},
           ] * 40
    info = {
        'worker': 'xxx.yyy.worker_do_sth'
    }
    worker = Worker(mode='thread')
    resp = worker.work(data, info)
    print(resp)


.. code-block:: python

    def worker_do_sth(data, info):
        print(data)
        return data

    def callback(results):
        print('final')
        print(results)


    def test_celery():
        data = [
                   'u11', 'u22', 'u33', 'u44',
                   'u21', 'u22', 'u23', 'u24',
                   'u31', 'u32', 'u33', 'u34',
                   'u41', 'u42', 'u43', 'u44',
                   'u51', 'u52', 'u53', 'u54',
               ]*8
        info={
            'celery_worker': 'test.functional.test_celery.simple',
            'worker': 'test.functional.test_celery.worker_do_sth',
            'celery_max_workers': 4,
            'celery_chunk_size': 80,
            'chunk_size': 20,
            'final_callback': 'test.functional.test_celery.callback',
            'queue': '123'
        }

        worker = Worker(mode='celery')
        resp = worker.work(data, info)
        return resp


