import logging
import random
import asyncio
from copy import copy
from datetime import datetime

from aiohttp import ClientSession
from loader.function import load

from logcc.util.table import trace_table as tt

from worker.exception import WorkerException
from worker.util import grouper_it
import time


async def test(data, info):
    # await asyncio.sleep(1)
    print(info)
    print(data)
    # print(data.get('index'))
    return 'hello'


async def test2(data, info):
    # await asyncio.sleep(5)
    print(info.get('index'))
    print(data.get('index'))
    raise Exception('test2 e')
    return 'hello2'


async def test3(data, info):
    asyncio.sleep(random.randint(1, 3))
    print(info.get('index'))
    print(data.get('index'))
    print(data)
    print(info)
    return 'hello3'


async def bound_process(func, data, info):
    response = None
    log = logging.getLogger(info.get('log', 'worker'))
    # log = logging.getLogger('worker')
    try:
        start_time = time.time()
        async with info.get('semaphore'):
            response = await func(data, info)
    except Exception as exc:
        tt(exc)
        log.critical('exception catched! %s -- %r' % (exc, data))
        response = WorkerException('%s -- %r' % (type(exc), exc))
    finally:
        end_time = time.time()
        log.debug("time elapsed: {}".format(end_time-start_time))
        return response


async def _work(data, info):
    log = logging.getLogger('worker')
    chunk_size = info.get('chunk_size', 20)
    # max_workers = info.get('max_workers', 4)
    max_sem = info.get('max_semaphore', len(data))
    try:
        func_str = info.get('worker')
        func = load(func_str)

    except Exception as exc:
        log.error('dynamic worker func invalid! %s' % exc)
        return None
    tasks = []
    semaphore = asyncio.Semaphore(max_sem)

    async with ClientSession() as session:
        backup_info = copy(info)
        response = None
        for index, data_chunked in enumerate(grouper_it(data, chunk_size)):
            info = copy(backup_info)
            info['index'] = index
            info['session'] = session
            info['semaphore'] = semaphore
            log.debug('coroutine worker chunk %d processing.' % (index))
            task = asyncio.ensure_future(bound_process(func, data_chunked, info))
            tasks.append(task)
        try:
            gathers = asyncio.gather(*tasks, return_exceptions=False)
        except Exception as exc:
            tt(exc)
            log.critical('exception catched! %s -- %r' % (exc, data))
            # response = WorkerException('%s -- %r' % (type(exc), exc))
        else:
            response = await gathers
        finally:
            return response


def work(data, info):
    log = logging.getLogger('worker')
    begin_time = datetime.now()

    response = None

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = asyncio.ensure_future(_work(data, info))
    # signal(SIGINT, lambda s, f: loop.stop())
    try:
        response = loop.run_until_complete(tasks)
    except KeyboardInterrupt as exc:
        log.warning('keyboard exited! %s -- %r' % (exc, data))
        for task in asyncio.Task.all_tasks():
            task.cancel()
    except Exception as exc:
        loop.stop()
        tt(exc)
        log.critical('exception catched when loop run until compete! %s -- %r' % (exc, data))
    finally:
        end_time = datetime.now()
        log.debug('coro done. time elapsed: {}'.format(end_time - begin_time))
        return response


if __name__ == '__main__':
    data = [
               {'hello': 'world'}
           ] * 90
    info = {
        'worker': 'test.pycurl.multicurl_simple',
    }
    resp = work(data, info)
    print(resp)
    # loop = asyncio.get_event_loop()
    # tasks = asyncio.ensure_future(coro([
    #                                        {'func': 'worker.coroutine.test'},
    #                                        {'func': 'worker.coroutine.test2'},
    #                                        {'func': 'worker.coroutine.test3'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                    ] * 200))
    # resp = loop.run_until_complete(tasks)
    # print(resp)
