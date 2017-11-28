'''
Helper module
'''
import json
import logging
import sys

from six import StringIO, print_
from termcolor import colored


class Logger:
    ch = logging.NullHandler()
    quiet = False

    @staticmethod
    def set(ch, quiet):
        Logger.ch = ch
        Logger.quiet = quiet
        if Logger.quiet:
            sys.stdout = StringIO()

    @staticmethod
    def get(name_class, level=logging.DEBUG):
        # print_('get logger - class:', name_class, Logger.ch)
        logger = logging.getLogger(name_class)
        logger.setLevel(level)
        logger.addHandler(Logger.ch)
        assert isinstance(logger, logging.Logger)
        return logger

    @staticmethod
    def print_(*args):
        if not Logger.quiet:
            print_(*args, end='', flush=True)

    @staticmethod
    def print_error(*args):
        if not Logger.quiet:
            print_(colored('ERROR: ' + ' '.join(args), 'red'))

    @staticmethod
    def println(*args):
        if not Logger.quiet:
            print_(*args)


def get_consol_handler():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter((
        '%(levelname) -3s %(asctime)s %(name)'
        '-3s %(funcName)'
        '-1s %(lineno) -0s: %(message)s'
    ))
    ch.setFormatter(formatter)
    return ch


def get_attributes(args, nodes):
    get = nodes
    for a in args:
        get = get[a]
    return get


def print_TOSCA(tosca, indent=2):
    space = ' ' * indent

    def _rec_print(item, tab, res):
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str) or \
                   (isinstance(value, dict) and 'get_input' in value):
                    return res + tab + str(key) + ': ' + str(value)
                else:
                    res += tab + str(key) + ':\n'
                    return _rec_print(value, tab + space, res)
        elif isinstance(item, list):
            for value in item:
                if isinstance(value, str):
                    return res + tab + '- ' + value + '\n'
                else:
                    key, value = list(value.items())[0]
                    res += res + tab + '- ' + key + ':\n'
                    return _rec_print(value, tab + space + '  ', res)
    res = ''
    if hasattr(tosca, 'nodetemplates'):
        if tosca.inputs:
            res += "\ninputs:\n"
            for input in tosca.inputs:
                res += space + input.name

        nodetemplates = tosca.nodetemplates
        if nodetemplates:
            res += "\nnodetemplates:\n"
            for node in nodetemplates:
                res += space + node.name + '\n'
                res += _rec_print(node.entity_tpl, space + space, '')
                res += '\n'
    return res


def print_json(stream, fprint):
    for line in stream:
        fprint('\t' + json.dumps(json.loads(line.decode("utf-8")), indent=2))


def print_byte(stream, fprint):
    for line in stream:
        fprint('\t' + line.decode("utf-8").strip())
