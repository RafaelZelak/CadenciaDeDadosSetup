import logging
import traceback
from copy import copy
from time import sleep

from celery import group, chain, Celery, chord
from celery.bin.control import inspect
from loader.function import load
from logcc.util.table import trace_table

from worker.util import grouper_it
from worker.thread import work as thread_work
from worker.coroutine import work as coroutine_work


def celery_coroutine_worker(self, data, info):
    sub_info = copy(info)
    resp = coroutine_work(data, sub_info)
    return resp


def celery_thread_worker(self, data, info):
    sub_info = copy(info)
    resp = thread_work(data, sub_info)
    return resp


celery_worker = celery_thread_worker


def parallel_chunked(data, info):
    func_str = info.get('celery_worker')
    queue = info.get('queue', 'celery')
    func = load(func_str)
    tasks = []

    callback = info.get('each_callback')
    if callback:
        callback = load(callback)
    for i, d in enumerate(data):
        for index, chunked_data in enumerate(grouper_it(d, info.get('chunk_size', 20))):
            if callback:
                # the result to callback will be returned as [result]
                sig = func.si(chunked_data, info).set(queue=queue) | callback.s().set(queue=queue)
            else:
                sig = func.si(chunked_data, info).set(queue=queue)
            tasks.append(sig)
    # removed for return group results
    # callback = info.get('group_callback')
    # if callback:
    #     callback = load(callback)
    #     return group(tasks) | callback.s()
    g = group(tasks)
    return g


def wait_for_group(results, celery_sleep=None, sync=None):
    if sync:
        rs = results.results
        while 1:
            success = 0
            for r in rs:
                if r.successful():
                    success += 1
                else:
                    break
            if len(rs) == success:
                break
            if celery_sleep:
                sleep(celery_sleep)
    else:
        if celery_sleep:
            sleep(celery_sleep)


def final_results(results_list):
    final_results = []
    for results in results_list:
        rs = results.results
        for r in rs:
            final_results.append(r.result)
    return final_results


def work(data, info):
    celery_chunk_size = info.get('celery_chunk_size', 80)
    celery_max_workers = info.get('celery_max_workers', 4)
    celery_sleep = info.get('celery_sleep')
    queue = info.get('queue', 'celery')
    sync_callback = info.get('sync_callback')
    final_callback = info.get('final_callback')
    dummy = info.get('dummy')
    dummy = load(dummy)
    splitted_data = []

    for index, data_chunked in enumerate(grouper_it(data, celery_chunk_size)):
        splitted_data.append(data_chunked)

    results_list = []
    if sync_callback:
        for index, splitted_chunked in enumerate(grouper_it(splitted_data, celery_max_workers)):
            tasks = parallel_chunked(splitted_chunked, info)
            results = tasks.apply_async()
            wait_for_group(results, celery_sleep, sync_callback)
            results_list.append(results)

        results = final_results(results_list)
        sync_callback = load(sync_callback)
        return sync_callback(results)
    else:
        tasks_list = []
        for index, splitted_chunked in enumerate(grouper_it(splitted_data, celery_max_workers)):
            tasks = parallel_chunked(splitted_chunked, info)
            if len(tasks) == 1:
                # chord([A], B) can be optimized as A | B
                # - Issue #3323
                tasks_list.append(tasks | dummy.si().set(queue=queue))
            else:
                tasks_list.append(chord(tasks, dummy.si().set(queue=queue)))

        if final_callback:
            final_callback = load(final_callback)
            task_to_run = chain(tasks_list) | final_callback.si(data, info).set(queue=queue)
        else:
            task_to_run = chain(tasks_list)

        results = task_to_run.apply_async()

        results_list.append(results)
        return results_list
