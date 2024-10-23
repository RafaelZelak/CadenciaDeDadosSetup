import logging
from copy import copy

from logcc.util.table import trace_table as tt
from loader.function import load

from worker.exception import WorkerException
from worker.util import grouper_it


def work(data, info):
    log = logging.getLogger(info.get('log', 'worker'))
    results = []
    chunk_size = info.get('chunk_size', 20)
    # max_workers = info.get('max_workers', 4)
    try:
        func_str = info.get('worker')
        func = load(func_str)
    except Exception as exc:
        log.error('dynamic worker func invalid! %s' % exc)
        return results
    backup_info = copy(info)
    for index, data_chunked in enumerate(grouper_it(data, chunk_size)):
        log.debug('simple worker chunk %d processing.' % (index))
        info = copy(backup_info)
        info['index'] = index
        try:
            result = func(data_chunked, info)
        except Exception as exc:
            tt(exc)
            log.critical('exception catched! %s %r' % (type(exc), exc))
            result = WorkerException('%s -- %r' % (type(exc), exc))
        results.append(result)
    return results
