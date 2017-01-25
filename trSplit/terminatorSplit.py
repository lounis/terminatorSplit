#!/usr/bin/python

"""terminator-split

Wrapper script for splitting Terminator terminal emulator
https://github.com/AlekseyChudov/terminator-split
"""

import argparse
import logging
import os
import resource
import tempfile

import configobj

__author__ = 'Aleksey Chudov <aleksey.chudov@gmail.com>'
__date__ = '24 Dec 2016'
__version__ = '1.0.1'


class TerminatorSplit(object):

    DEFAULT = {
        'config': os.path.expanduser('~/.config/terminator/config'),
        'command': "ssh -i ~/.ssh/test-generic-ec2.pem {}; bash",
        'terminator': '/usr/bin/terminator'
    }

    def __init__(self):
        self._args, self._unknown_args = self._parse_args()
        self._logging()
        self._child = 0
        self._layout = None
        self._config = self._write_config()
        self._launch_terminator()

    def _parse_args(self):
        usage = """terminator-split [-h] [-d]
                        [-e COMMAND] [-g CONFIG] [-t TERMINATOR]
                        [TERMINATOR_OPTIONS]
                        hostname [hostname ...]
        """
        parser = argparse.ArgumentParser(usage=usage)
        parser.add_argument('-d', '--debug', action='store_const', dest='level',
                            const='DEBUG', default='INFO')
        parser.add_argument('-e', '--command')
        parser.add_argument('-g', '--config')
        parser.add_argument('-t', '--terminator')
        parser.add_argument('hostname', nargs='+')
        namespace = argparse.Namespace(**self.DEFAULT)
        return parser.parse_known_args(namespace=namespace)

    def _is_debug(self):
        return self._args.level == 'DEBUG'

    def _logging(self):
        logging.basicConfig(format='%(message)s', level=self._args.level)
        logging.debug('args:{}'.format(self._args))
        logging.debug('unknown_args:{}'.format(self._unknown_args))

    def _write_config(self):
        config = configobj.ConfigObj(self._args.config)
        self._update_layout(config)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            config.filename = tmp.name
            config.write()
        logging.debug("config:{}:'{}'".format(config.filename, config))
        return config.filename

    def _update_layout(self, config):
        parent = self._next_child()
        self._layout = {parent: {'parent': '', 'type': 'Window'}}
        self._split_layout(parent, self._args.hostname)
        config['layouts']['default'] = self._layout

    def _next_child(self):
        child = 'child{}'.format(self._child)
        self._child += 1
        return child

    @staticmethod
    def _split_index(iterable):
        return (len(iterable) + 1) // 2

    def _split_layout(self, parent, hosts):
        if len(hosts) == 1:
            self._add_terminals(parent, hosts)
            return

        new_parent = self._split_horizontal(parent)
        split_index = self._split_index(hosts)

        if len(hosts) == 2:
            self._add_terminals(new_parent, hosts)

        elif len(hosts) == 3:
            left_parent = self._split_vertical(new_parent)
            self._add_terminals(left_parent, hosts[:split_index])
            self._add_terminals(new_parent, hosts[split_index:])

        elif len(hosts) == 4:
            left_parent = self._split_vertical(new_parent)
            right_parent = self._split_vertical(new_parent)
            self._add_terminals(left_parent, hosts[:split_index])
            self._add_terminals(right_parent, hosts[split_index:])
        else:
            self._split_layout(new_parent, hosts[:split_index])
            self._split_layout(new_parent, hosts[split_index:])

    def _add_terminals(self, parent, hosts):
        for host in hosts:
            self._layout[self._next_child()] = {
                'command': self._args.command.format(host),
                'parent': parent,
                'type': 'Terminal'
            }

    def _split_horizontal(self, parent):
        child = self._next_child()
        self._layout[child] = {
            'parent': parent,
            'type': 'HPaned'
        }
        return child

    def _split_vertical(self, parent):
        child = self._next_child()
        self._layout[child] = {
            'parent': parent,
            'type': 'VPaned'
        }
        return child

    def _launch_terminator(self):
        self._demonize()
        os.execl(self._args.terminator, self._args.terminator,
                 '-g', self._config, *self._unknown_args)

    def _demonize(self, chdir='/', max_fd=1024, umask=0):
        """
        http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
        """
        if os.fork():
            os._exit(0)

        os.setsid()
        os.chdir(chdir)
        os.umask(umask)

        if os.fork():
            os._exit(0)

        start_fd = 0
        stop_fd = max(max_fd, resource.getrlimit(resource.RLIMIT_NOFILE)[0])

        if self._is_debug():
            start_fd = 4

        for fd in range(start_fd, stop_fd):
            try:
                os.close(fd)
            except OSError:
                pass

        if not self._is_debug():
            os.open(os.devnull, os.O_RDWR)
            os.dup2(0, 1)
            os.dup2(0, 2)


def main():
    TerminatorSplit()

if __name__ == '__main__':
    main()
