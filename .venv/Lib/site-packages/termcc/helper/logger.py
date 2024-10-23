import sys
import logbook
from logbook import (Processor, StreamHandler, SyslogHandler)
import datetime
from termcc.cc import cc
from termcc.helper.time import show
from multiprocessing import Process



def inject_basic(record):
    record.extra['time'] = show(datetime.datetime.utcnow(), 'Asia/Shanghai')

def inject_color(record):
    level_color = {
        'CRITICAL': cc(':bold::skull:  :red::black_:'),
        'ERROR': cc(':bold::cross_mark:  :red:'),
        'WARNING': cc(':bold::yellow::loudspeaker:  '),
        'NOTICE': cc(':bold::light_bulb::blue:  '),
        'INFO': cc(':bold::green::beer:  '),
        'DEBUG': cc(':bold::white::bug:  '),
        'TRACE': cc(':bold::railway_track::gray:  '),
    }
    record.extra['level-prefix'] = level_color[record.level_name]
    record.extra['level-suffix'] = cc(':reset:')

try:
    from flask import request
except ModuleNotFoundError as e:
    import uuid
    def inject_flask(record):
        inject_basic(record)
        record.extra['trace_id'] = uuid.uuid1()
        record.extra['ip'] = None
        record.extra['method'] = None
        record.extra['path'] = None
else:
    def inject_flask(record):
        inject_basic(record)
        try:
            ip = request.remote_addr or None
            tid = request.headers.get('trace-id')
            path = request.full_path
            method = request.method
        except RuntimeError:
            record.extra['ip'] = None
            record.extra['method'] = None
            record.extra['trace_id'] = None
            record.extra['path'] = None
        else:
            record.extra['ip'] = ip
            record.extra['method'] = method
            record.extra['trace_id'] = tid
            record.extra['path'] = path

def inject_default_color(record):
    inject_basic(record)
    inject_color(record)

def inject_flask_color(record):
    inject_flask(record)
    inject_color(record)

DEFAULT_LOGGERS = {
    "stream-out": StreamHandler(sys.stdout, level=logbook.TRACE, bubble=True),
    # "syslog": SyslogHandler(level=logbook.TRACE, bubble=True),
}

class Config:
    def __init__(self, loggers=None, inject=None):

        self.loggers = loggers or DEFAULT_LOGGERS        
        self.processor = Processor(inject) if inject is not None else None

    def push(self, logger_names=None):
        if logger_names:
            for name, logger in self.loggers.items():
                if name in logger_names:
                    logger.push_application()
        else:
            for logger in self.loggers.values():
                logger.push_application()
        if self.processor:
            self.processor.push_application()

    def setup_format(self, *args, logger_names=None):
        specs = []
        for arg in args:
            specs += arg
        specs.append("{record.msg}")
        specs = ' '.join(specs)

        if logger_names:
            for name, logger in self.loggers.items():
                if name in logger_names:
                    logger.format_string = specs
        else:
            for logger in self.loggers.values():
                logger.format_string = specs

    @staticmethod
    def trace_format():
        return [
            "[{record.extra[trace_id]}]",
        ]

    @staticmethod
    def process_format():
        return [
            "[{record.process_name}:{record.process}]",
            "[{record.thread_name}:{record.thread}]",
        ]

    @staticmethod
    def file_format():
        return [
            "[{record.module}:{record.filename}:{record.func_name}:{record.lineno}]",
        ]

    @staticmethod
    def time_format(color=False):
        return [
            "[{record.extra[time]}]",
        ]

    @staticmethod
    def flask_format(color=False):
        return [
            "[{record.extra[ip]}:{record.extra[method]}:{record.extra[path]}]",
        ]

    @staticmethod
    def basic_format(color=False):
        if color:
            return [
                "[{record.channel}]",
                "[{record.extra[level-prefix]}{record.level_name}{record.extra[level-suffix]}]",
            ]
        return [
            "[{record.channel}]",
            "[{record.level_name}]",
        ]

def sample_default():
    lc = Config(inject=inject_default_color)
    lc.setup_format(
        lc.basic_format(color=True),
        lc.time_format(),
        lc.process_format(),
        logger_names=['stream-out'])
    lc.push(logger_names=['stream-out'])

def sample_flask():
    lc = Config(inject=inject_flask_color)
    lc.setup_format(
        lc.basic_format(color=True),
        lc.time_format(),
        lc.process_format(),
        lc.trace_format(),
        logger_names=['stream-out'])
    lc.push(logger_names=['stream-out'])

def sample_flask_path():
    lc = Config(inject=inject_flask_color)
    lc.setup_format(
        lc.basic_format(color=True),
        lc.time_format(),
        lc.process_format(),
        lc.trace_format(),
        lc.flask_format(),
        logger_names=['stream-out'])
    lc.push(logger_names=['stream-out'])
