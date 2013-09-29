# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import subprocess
from helpers.command import Command


def get_scores(cursor):
    rows = cursor.execute('SELECT nick,score FROM scores').fetchall()
    return {row['nick']: row['score'] for row in rows}


@Command(['bc', 'math'], ['db'])
def cmd(send, msg, args):
    """Evaluates mathmatical expressions.
    Syntax: !bc <expression>
    """
    if not msg:
        send("Calculate what?")
        return
    scores = get_scores(args['db'])
    for word in msg.split():
        if word in scores:
            msg = msg.replace(word, str(scores[word]))
    msg += '\n'
    proc = subprocess.Popen(['bc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.communicate(msg.encode())[0].decode()
    for line in output.splitlines():
        send(line)
