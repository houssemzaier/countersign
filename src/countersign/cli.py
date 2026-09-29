"""countersign: a file protocol for a maker-checker loop between two AI coding agents.

The maker builds and signs its work (a report). The checker verifies it on evidence and
countersigns (a review with a verdict). The owner, a human, holds the gates.

A session is a folder:
  <session>/messages/   append-only messages, one file each, written atomically
  <session>/state.json  turn, sequence, rounds per ticket, heartbeats, settings
  <session>/STOP        present once the owner has stopped the session
  <session>/tmp/        atomic writes and the state lock

Each agent listens with `wait` and writes with `send`. Nothing else is shared.
"""
import argparse
import datetime
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from . import __version__

ROLES = ('maker', 'checker', 'owner')
TYPES = ('ready', 'report', 'review', 'note', 'approval')
VERDICTS = ('accepted', 'changes', 'blocked')
EXIT_MESSAGE, EXIT_USAGE, EXIT_STOP, EXIT_TIMEOUT = 0, 2, 3, 4
DATA = Path(__file__).resolve().parent / 'data'


def now():
    return datetime.datetime.now().isoformat(timespec='seconds')


def fail(msg):
    print(f'countersign: {msg}', file=sys.stderr)
    sys.exit(EXIT_USAGE)


def session_path(arg):
    value = arg or os.environ.get('COUNTERSIGN_SESSION')
    if not value:
        fail('no session folder: pass it as an argument or set COUNTERSIGN_SESSION')
    return Path(value).expanduser()


class Lock:
    """A lock file created with O_EXCL. A lock older than 30 s is left by a killed process."""

    def __init__(self, ws):
        self.path = ws / 'tmp' / '.lock'

    def __enter__(self):
        started = time.time()
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > 30:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.time() - started > 15:
                    fail('the session state is locked by another process')
                time.sleep(0.1)

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def load_state(ws):
    try:
        return json.loads((ws / 'state.json').read_text())
    except FileNotFoundError:
        fail(f'{ws} is not a countersign session (run: countersign new {ws})')


def save_state(ws, state):
    tmp = ws / 'tmp' / 'state.json.tmp'
    tmp.write_text(json.dumps(state, indent=1))
    os.replace(tmp, ws / 'state.json')


def notify(state, text):
    """Runs the session's notify command with the text on stdin and in COUNTERSIGN_MESSAGE.
    COUNTERSIGN_NOTIFY overrides the session setting; 'off' disables it. A failure never blocks."""
    command = os.environ.get('COUNTERSIGN_NOTIFY', state.get('notify') or '')
    if not command or command == 'off':
        return
    try:
        subprocess.run(command, shell=True, input=text, text=True, capture_output=True, timeout=60,
                       env=dict(os.environ, COUNTERSIGN_MESSAGE=text))
    except Exception:
        pass


def parse_front(text):
    meta = {}
    if text.startswith('---\n'):
        end = text.find('\n---', 4)
        for line in text[4:end].splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                meta[key.strip()] = value.strip()
    return meta


def messages(ws):
    out = []
    for path in sorted((ws / 'messages').glob('*.md')):
        meta = parse_front(path.read_text())
        meta['path'] = str(path)
        out.append(meta)
    return out


def cmd_new(args):
    ws = session_path(args.session)
    if (ws / 'state.json').exists():
        fail(f'{ws} already exists')
    for sub in ('messages', 'tmp'):
        (ws / sub).mkdir(parents=True, exist_ok=True)
    state = {'protocol': 1, 'status': 'running', 'turn': 'any', 'seq': 0, 'maxRounds': args.max_rounds,
             'notify': args.notify or '', 'rounds': {}, 'ready': {'maker': False, 'checker': False},
             'lastRead': {r: 0 for r in ROLES}, 'lastSeen': {r: None for r in ROLES}, 'created': now()}
    save_state(ws, state)
    print(f'countersign session ready: {ws}')


def cmd_send(args):
    ws = session_path(args.session)
    body = Path(args.file).read_text() if args.file else sys.stdin.read()
    if args.type == 'review' and args.verdict not in VERDICTS:
        fail('a review needs --verdict accepted|changes|blocked')
    if args.type == 'report' and not args.ticket:
        fail('a report needs --ticket ID')
    if args.as_ == 'maker' and args.to != 'checker':
        fail('the maker writes only to the checker; to ask the owner, send to the checker with --owner')
    pings = []
    with Lock(ws):
        state = load_state(ws)
        if (ws / 'STOP').exists():
            fail('STOP is set: the session is over')
        seq = state['seq'] + 1
        owner = args.owner or args.verdict == 'blocked'
        rnd = ''
        if args.ticket:
            key = str(args.ticket)
            if args.type == 'report':
                state['rounds'][key] = state['rounds'].get(key, 0) + 1
                if state['rounds'][key] > state['maxRounds']:
                    owner = True
                    pings.append(f'countersign: ticket {key} reached report {state["rounds"][key]} '
                                 f'(max {state["maxRounds"]}); the owner decides')
            rnd = state['rounds'].get(key, 0)
        front = ['---', 'protocol: 1', f'seq: {seq}', f'from: {args.as_}', f'to: {args.to}', f'type: {args.type}',
                 f'ticket: {args.ticket or ""}', f'round: {rnd}', f'created: {now()}',
                 f'requires_owner: {"true" if owner else "false"}', f'verdict: {args.verdict or ""}', '---', '']
        tmp = ws / 'tmp' / f'{seq:04d}.md'
        tmp.write_text('\n'.join(front) + body.rstrip() + '\n')
        os.replace(tmp, ws / 'messages' / f'{seq:04d}-{args.as_}-{args.type}.md')
        state['seq'] = seq
        state['turn'] = 'owner' if owner else args.to
        state['status'] = 'waiting_owner' if owner else 'running'
        if args.type == 'ready' and args.as_ in state['ready']:
            state['ready'][args.as_] = True
            if all(state['ready'].values()):
                pings.append('countersign: maker and checker are both ready; the loop is running')
        if args.type == 'review' and args.verdict == 'accepted':
            pings.append(f'countersign: ticket {args.ticket} countersigned (accepted by the checker)')
        if owner and args.type != 'report':
            pings.append(f'countersign: owner decision needed (message {seq}, {args.as_} to {args.to})')
        save_state(ws, state)
    for text in pings:
        notify(state, text)
    print(f'sent {seq:04d}-{args.as_}-{args.type} to {args.to}' + (' (owner gate)' if owner else ''))


def cmd_wait(args):
    ws = session_path(args.session)
    started = time.time()
    while True:
        if (ws / 'STOP').exists():
            print(f"STOP: {(ws / 'STOP').read_text().strip() or 'the owner stopped the session'}")
            sys.exit(EXIT_STOP)
        with Lock(ws):
            state = load_state(ws)
            state['lastSeen'][args.as_] = now()
            mine = [m for m in messages(ws)
                    if m.get('to') == args.as_ and int(m.get('seq', 0)) > state['lastRead'].get(args.as_, 0)]
            if mine:
                state['lastRead'][args.as_] = int(mine[0]['seq'])
            save_state(ws, state)
        if mine:
            m = mine[0]
            detail = (f", ticket {m['ticket']}" if m.get('ticket') else '') + \
                     (f", verdict {m['verdict']}" if m.get('verdict') else '')
            print(f"# message {m['seq']} from {m['from']} ({m['type']}{detail})  {m['path']}\n")
            print(Path(m['path']).read_text())
            sys.exit(EXIT_MESSAGE)
        if args.timeout and time.time() - started > args.timeout:
            print(f'timeout: no message for the {args.as_} yet; run wait again')
            sys.exit(EXIT_TIMEOUT)
        time.sleep(args.poll)


def cmd_status(args):
    ws = session_path(args.session)
    state = load_state(ws)
    print(f"status {state['status']} | turn {state['turn']} | seq {state['seq']} | rounds {state['rounds']} | "
          f"ready {state['ready']} | STOP {'yes' if (ws / 'STOP').exists() else 'no'}")
    print(f"last seen: {state['lastSeen']}")
    for m in messages(ws)[-args.last:]:
        print(f"  {m.get('seq', '?'):>4} {m.get('from')} -> {m.get('to')} {m.get('type')}"
              f"{' #' + m['ticket'] if m.get('ticket') else ''}{' r' + m['round'] if m.get('round') else ''}"
              f"{' ' + m['verdict'] if m.get('verdict') else ''}{' OWNER' if m.get('requires_owner') == 'true' else ''}")


def cmd_approve(args):
    args.as_, args.type, args.ticket, args.verdict, args.owner, args.file = 'owner', 'approval', None, None, False, None
    sys.stdin = io.StringIO(args.note or 'approved')
    cmd_send(args)


def cmd_stop(args):
    ws = session_path(args.session)
    (ws / 'STOP').write_text((args.note or 'stopped by the owner') + f' ({now()})\n')
    with Lock(ws):
        state = load_state(ws)
        state['status'] = 'stopped'
        save_state(ws, state)
    notify(state, f'countersign: session stopped ({args.note or "owner"})')
    print('STOP set')


def cmd_prompt(args):
    """Prints a role card, to hand to the agent that plays the role."""
    print((DATA / 'roles' / f'{args.role}.md').read_text(), end='')


def cmd_template(args):
    """Prints a project template: the AGENTS.md rules, the frozen acceptance list, a ticket."""
    print((DATA / 'templates' / f'{args.name}.md').read_text(), end='')


def build_parser():
    p = argparse.ArgumentParser(prog='countersign', description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--version', action='version', version=f'countersign {__version__}')
    sub = p.add_subparsers(dest='cmd', required=True)

    def session(sp):
        sp.add_argument('session', nargs='?', help='session folder (default: $COUNTERSIGN_SESSION)')

    n = sub.add_parser('new', help='create a session')
    session(n)
    n.add_argument('--max-rounds', type=int, default=4, help='reports per ticket before the owner decides')
    n.add_argument('--notify', help='shell command run on owner gates, acceptances and stop (text on stdin)')

    s = sub.add_parser('send', help='send a message (body from --file or stdin)')
    session(s)
    s.add_argument('--as', dest='as_', choices=ROLES, required=True)
    s.add_argument('--to', choices=ROLES, required=True)
    s.add_argument('--type', choices=TYPES, required=True)
    s.add_argument('--file')
    s.add_argument('--ticket')
    s.add_argument('--verdict', choices=VERDICTS)
    s.add_argument('--owner', action='store_true', help='mark the message as an owner gate')

    w = sub.add_parser('wait', help='block until a message arrives (exit 0), STOP (3) or timeout (4)')
    session(w)
    w.add_argument('--as', dest='as_', choices=ROLES, required=True)
    w.add_argument('--timeout', type=int, default=0, help='seconds; 0 waits forever')
    w.add_argument('--poll', type=float, default=3.0, help=argparse.SUPPRESS)

    st = sub.add_parser('status', help='where the session stands')
    session(st)
    st.add_argument('--last', type=int, default=8, help='how many recent messages to list')

    ap = sub.add_parser('approve', help='the owner opens a gate')
    session(ap)
    ap.add_argument('--to', choices=ROLES, required=True)
    ap.add_argument('--note')

    sp = sub.add_parser('stop', help='the owner ends the session; both agents stop at their next wait')
    session(sp)
    sp.add_argument('--note')

    pr = sub.add_parser('prompt', help='print the role card for an agent (maker, checker or owner)')
    pr.add_argument('role', choices=ROLES)

    tp = sub.add_parser('template', help='print a project template')
    tp.add_argument('name', choices=('AGENTS', 'ACCEPTANCE', 'TICKET'))
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    {'new': cmd_new, 'send': cmd_send, 'wait': cmd_wait, 'status': cmd_status, 'approve': cmd_approve,
     'stop': cmd_stop, 'prompt': cmd_prompt, 'template': cmd_template}[args.cmd](args)


if __name__ == '__main__':
    main()
