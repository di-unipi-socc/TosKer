import json
import logging

from six import print_


class Logger:
    main_level = logging.DEBUG
    _ch = None

    @staticmethod
    def _get_console_hadler():
        if Logger._ch is None:
            Logger._ch = logging.StreamHandler()
            Logger._ch.setLevel(Logger.main_level)

            # create formatter and add it to the handlers
            LOG_FORMAT = ('%(levelname) -3s %(asctime)s %(name)'
                          '-3s %(funcName)'
                          '-1s %(lineno) -0s: %(message)s')
            formatter = logging.Formatter(LOG_FORMAT)
            # fh.setFormatter(formatter)

            Logger._ch.setFormatter(formatter)
        return Logger._ch

    @staticmethod
    def get(name_class, level=logging.DEBUG):
        # print ('class:', name_class, '- level:', Logger.main_level)
        logger = logging.getLogger(name_class)
        logger.setLevel(level)
        logger.addHandler(Logger._get_console_hadler())
        assert isinstance(logger, logging.Logger)
        return logger


def get_attributes(args, nodes):
    get = nodes
    for a in args:
        get = get[a]
    return get


def print_TOSCA(tosca, indent=2):
    space = ' ' * indent

    def _rec_print(item, tab, res):
        if type(item) is dict:
            for key, value in item.items():
                if type(value) is str or (type(value) is dict and 'get_input' in value):
                    return res + tab + str(key) + ': ' + str(value)
                else:
                    res += tab + str(key) + ':\n'
                    return _rec_print(value, tab + space, res)
        elif type(item) is list:
            for value in item:
                if type(value) is str:
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


def print_json(stream):
    for line in stream:
        print_('\t' + json.dumps(json.loads(line.decode("utf-8")), indent=2), end='')
    # print()


def print_byte(stream):
    for line in stream:
        print_('\t' + line.decode("utf-8"), end='')
    # print()
