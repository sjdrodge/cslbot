# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import re
from random import choice
from config import NICK

args = ['channels', 'target', 'connection', 'nick', 'do_log']


def cmd(send, msg, args):
    users = (args['channels'][args['target']].users() if args['target'] != 'private' else ['you'])
    target = args['target'] if args['target'] != 'private' else args['nick']
    if "at" in msg:
        match = re.match('(.*) at (.*)', msg)
        if match:
            msg = 'throws %s at %s' % (match.group(1), match.group(2))
            args['connection'].action(target, msg)
        else:
            return
    elif msg:
        msg = 'throws %s at %s' % (msg, choice(users))
        args['connection'].action(target, msg)
    else:
        return
    args['do_log'](NICK, msg, 'action')