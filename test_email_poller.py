import os
import unittest
from unittest.mock import patch
import email
import imaplib

from software import email_poller


with open('tests/sample_report.eml', 'rb') as f:
    SAMPLE_BYTES = f.read()
    SAMPLE_MESSAGE = email.message_from_bytes(SAMPLE_BYTES)


class MockIMAP4(imaplib.IMAP4_SSL):
    login_calls = 0
    seen_calls = 0

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sent = False

    def login(self, username, password):
        MockIMAP4.login_calls += 1
        return 'OK', [b'Logged in']

    def select(self, mailbox):
        return 'OK', [b'']

    def search(self, charset, *criteria):
        if not self.sent:
            self.sent = True
            return 'OK', [b'1']
        return 'OK', [b'']

    def fetch(self, msg_id, _):
        return 'OK', [(b'1', SAMPLE_BYTES)]

    def store(self, msg_id, flags, data):
        MockIMAP4.seen_calls += 1
        return 'OK', [b'']

    def logout(self):
        return 'OK', [b'']


class EmailPollerTest(unittest.TestCase):
    def test_poll_for_reports(self):
        processed = {}

        def fake_process(msg):
            processed['called'] = True
            # Optionally assert the message is same as sample
            self.assertEqual(msg.get('Subject'), SAMPLE_MESSAGE.get('Subject'))
            return []

        config = {
            'imap_host': 'localhost',
            'imap_port': 993,
            'use_ssl': True,
            'username': 'user',
            'password': 'pass',
            'mailbox': 'INBOX',
            'search_criteria': ['UNSEEN'],
        }

        with patch('software.email_poller.load_imap_config', return_value=config), \
             patch('imaplib.IMAP4_SSL', MockIMAP4), \
             patch('software.email_poller.process_message', side_effect=fake_process), \
             patch('software.email_poller.time.sleep', return_value=None):
            email_poller.poll_for_reports_once()

        self.assertEqual(MockIMAP4.login_calls, 1)
        self.assertEqual(MockIMAP4.seen_calls, 1)
        self.assertTrue(processed.get('called'))

    def test_poll_for_reports_no_internet(self):
        config = {
            'imap_host': 'localhost',
            'imap_port': 993,
            'use_ssl': True,
            'username': 'user',
            'password': 'pass',
            'mailbox': 'INBOX',
            'search_criteria': ['UNSEEN'],
        }

        with patch('software.email_poller.load_imap_config', return_value=config), \
             patch('imaplib.IMAP4_SSL', side_effect=OSError('network down')), \
             self.assertLogs('email_poller', level='WARNING') as cm:
            result = email_poller.poll_for_reports_once()

        self.assertEqual(result, [])
        self.assertIn('No internet connection', cm.output[0])


if __name__ == '__main__':
    unittest.main()
