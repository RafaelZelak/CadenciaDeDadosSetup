from terminaltables import AsciiTable
from logbook import Logger
import traceback
from textwrap import wrap

def trace_exception(exception, log=None):
    if log is None:
        log = Logger('termcc')

    table_data = [['info', 'func', 'lino', 'file']]
    tb = traceback.extract_tb(exception.__traceback__, limit=None)
    for t in tb:
        wrapped_string = '\n'.join(wrap(t.filename.rstrip('\n'), 80))
        table_data.append([t.line.rstrip('\n'), t.name, t.lineno, wrapped_string])
    table = AsciiTable(table_data)
    table.outer_border = True
    table.inner_heading_row_border = True
    table.inner_column_border = True
    table.inner_row_border = True

    log.error('TABLE>\n'+table.table)
    log.error('ERROR type: {}, detail: {}'.format(type(exception), str(exception)))