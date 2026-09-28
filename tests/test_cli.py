"""End-to-end tests of the countersign CLI, run as a subprocess the way agents run it."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = str(Path(__file__).resolve().parent.parent / 'src')


def cs(*args, stdin='', env=None, check=True):
    e = dict(os.environ, PYTHONPATH=SRC, COUNTERSIGN_NOTIFY='off')
    e.pop('COUNTERSIGN_SESSION', None)
    e.update(env or {})
    r = subprocess.run([sys.executable, '-m', 'countersign', *args], input=stdin, text=True,
                       capture_output=True, env=e)
    if check and r.returncode != 0:
        raise AssertionError(f'countersign {args} exited {r.returncode}: {r.stderr}')
    return r


class CountersignTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = str(Path(self.tmp.name) / 'session')
        cs('new', self.ws, '--max-rounds', '2')

    def tearDown(self):
        self.tmp.cleanup()

    def state(self):
        return json.loads((Path(self.ws) / 'state.json').read_text())

    def test_a_report_reaches_the_checker_once(self):
        cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'report', '--ticket', '7', stdin='done')
        first = cs('wait', self.ws, '--as', 'checker', '--timeout', '2', '--poll', '0.1')
        self.assertIn('ticket 7', first.stdout)
        self.assertIn('done', first.stdout)
        again = cs('wait', self.ws, '--as', 'checker', '--timeout', '1', '--poll', '0.1', check=False)
        self.assertEqual(again.returncode, 4, 'a message is delivered once')

    def test_messages_are_addressed(self):
        cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'note', stdin='for the checker')
        r = cs('wait', self.ws, '--as', 'maker', '--timeout', '1', '--poll', '0.1', check=False)
        self.assertEqual(r.returncode, 4, 'the maker does not receive its own message')

    def test_a_report_needs_a_ticket_and_a_review_a_verdict(self):
        r = cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'report', stdin='x', check=False)
        self.assertEqual(r.returncode, 2)
        r = cs('send', self.ws, '--as', 'checker', '--to', 'maker', '--type', 'review', '--ticket', '1',
               stdin='x', check=False)
        self.assertEqual(r.returncode, 2)

    def test_the_report_past_the_round_limit_goes_to_the_owner(self):
        for _ in range(2):
            cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'report', '--ticket', '3', stdin='r')
        self.assertEqual(self.state()['status'], 'running')
        out = cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'report', '--ticket', '3', stdin='r')
        self.assertIn('owner gate', out.stdout)
        self.assertEqual(self.state()['status'], 'waiting_owner')
        self.assertEqual(self.state()['rounds'], {'3': 3})

    def test_blocked_is_an_owner_gate_and_approve_reopens_it(self):
        cs('send', self.ws, '--as', 'checker', '--to', 'maker', '--type', 'review', '--ticket', '1',
           '--verdict', 'blocked', stdin='scope question')
        self.assertEqual(self.state()['turn'], 'owner')
        cs('approve', self.ws, '--to', 'maker', '--note', 'go ahead')
        self.assertEqual(self.state()['turn'], 'maker')
        cs('wait', self.ws, '--as', 'maker', '--timeout', '2', '--poll', '0.1')
        r = cs('wait', self.ws, '--as', 'maker', '--timeout', '2', '--poll', '0.1')
        self.assertIn('go ahead', r.stdout)

    def test_stop_ends_every_wait_and_refuses_sends(self):
        cs('stop', self.ws, '--note', 'done for today')
        r = cs('wait', self.ws, '--as', 'checker', '--timeout', '2', '--poll', '0.1', check=False)
        self.assertEqual(r.returncode, 3)
        self.assertIn('done for today', r.stdout)
        r = cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'note', stdin='x', check=False)
        self.assertEqual(r.returncode, 2)

    def test_the_session_can_come_from_the_environment(self):
        env = {'COUNTERSIGN_SESSION': self.ws}
        cs('send', '--as', 'maker', '--to', 'checker', '--type', 'ready', stdin='ready', env=env)
        r = cs('status', env=env)
        self.assertIn('ready', r.stdout)

    def test_notify_gets_the_owner_gates_and_the_acceptances(self):
        log = Path(self.tmp.name) / 'notified.txt'
        env = {'COUNTERSIGN_NOTIFY': f'cat >> {log}; echo >> {log}'}
        cs('send', self.ws, '--as', 'checker', '--to', 'maker', '--type', 'review', '--ticket', '4',
           '--verdict', 'accepted', stdin='ok', env=env)
        cs('send', self.ws, '--as', 'checker', '--to', 'maker', '--type', 'review', '--ticket', '5',
           '--verdict', 'blocked', stdin='?', env=env)
        text = log.read_text()
        self.assertIn('ticket 4 countersigned', text)
        self.assertIn('owner decision needed', text)

    def test_messages_are_files_with_a_front_matter(self):
        cs('send', self.ws, '--as', 'maker', '--to', 'checker', '--type', 'report', '--ticket', '9', stdin='body')
        files = sorted((Path(self.ws) / 'messages').glob('*.md'))
        self.assertEqual([f.name for f in files], ['0001-maker-report.md'])
        text = files[0].read_text()
        self.assertTrue(text.startswith('---\nprotocol: 1\nseq: 1\nfrom: maker\nto: checker\ntype: report\nticket: 9\n'))
        self.assertTrue(text.rstrip().endswith('body'))

    def test_role_cards_and_templates_are_printable(self):
        for role in ('maker', 'checker', 'owner'):
            self.assertIn(f'# Role: {role}', cs('prompt', role).stdout)
        for name in ('AGENTS', 'ACCEPTANCE', 'TICKET'):
            self.assertTrue(cs('template', name).stdout.strip())


if __name__ == '__main__':
    unittest.main()
