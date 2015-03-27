# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, Reed Koser, and James Forcier
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

import collections
from threading import Lock
from sqlalchemy import or_
from helpers.hook import Hook
from helpers.orm import Log, Babble, Babble_metadata

babble_lock = Lock()


def get_messages(cursor, cmdchar, ctrlchan, last):
    # Ignore all commands, messages addressed to people, and messages addressed to the ctrlchan
    return cursor.query(Log).filter(Log.id > last.last, or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar),
                                    Log.target != ctrlchan).order_by(Log.id).all()

Node = collections.namedtuple('Node', ['freq', 'source', 'target'])


def get_markov(cursor, prev, row):
    node = Node(collections.defaultdict(int), row.source, row.target)
    old = cursor.query(Babble).filter(Babble.key == prev, Babble.source == row.source, Babble.target == row.target).all()
    node.freq.update({x.word: x.freq for x in old})
    return node


def build_markov(cursor, cmdchar, ctrlchan):
    """ Builds a markov dictionary."""
    # Keep synchronized with scripts/gen_babble.py
    markov = {}
    last = cursor.query(Babble_metadata).first()
    messages = get_messages(cursor, cmdchar, ctrlchan, last)
    if not messages:
        return
    curr = messages[-1].id
    for row in messages:
        msg = row.msg.split()
        for i in range(2, len(msg)):
            prev = "%s %s" % (msg[i-2], msg[i-1])
            if prev not in markov:
                markov[prev] = get_markov(cursor, prev, row)
            markov[prev].freq[msg[i]] += 1
    for key, node in markov.items():
        for word, freq in node.freq.items():
            row = cursor.query(Babble).filter(Babble.key == key, Babble.source == node.source, Babble.target == node.target).first()
            if row:
                row.word = word
                row.freq = freq
            else:
                cursor.add(Babble(source=node.source, target=node.target, key=key, word=word, freq=freq))
    last.last = curr
    cursor.commit()


def update_markov(handler, config):
    with babble_lock:
        with handler.db.session_scope() as cursor:
            cmdchar = config['core']['cmdchar']
            ctrlchan = config['core']['ctrlchan']
            build_markov(cursor, cmdchar, ctrlchan)


@Hook('babble', ['pubmsg', 'privmsg'], ['db', 'handler', 'config'])
def hook(send, msg, args):
    # No babble cache, nothing to update
    if not args['db'].query(Babble).count():
        return
    # FIXME: is this the best way to do this?
    args['handler'].workers.defer(0, False, update_markov, args['handler'], args['config'])
