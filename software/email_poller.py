import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

import imaplib
import email
from email.message import Message
import time
import os
import logging

from software.config import load_imap_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('email_poller')


def process_message(msg: Message) -> None:
    """Placeholder for processing email messages."""
    logger.info('Processing message: %s', msg.get('Subject'))


def poll_for_reports() -> None:
    """Continuously poll an IMAP inbox for new reports."""
    config = load_imap_config()
    while True:
        try:
            logger.info('Connecting to %s:%s', config['imap_host'], config['imap_port'])
            conn = imaplib.IMAP4_SSL(config['imap_host'], config['imap_port'])
            try:
                conn.login(config['username'], config['password'])
                logger.info('Logged in as %s', config['username'])
                conn.select(config['mailbox'])
                logger.info('Mailbox selected: %s', config['mailbox'])
                status, messages = conn.search(None, *config['search_criteria'])
                if status != 'OK':
                    logger.error('Search failed with status %s', status)
                else:
                    for msg_id in messages[0].split():
                        status, data = conn.fetch(msg_id, '(RFC822)')
                        if status != 'OK':
                            logger.error('Failed to fetch message %s: %s', msg_id, status)
                            continue
                        msg = email.message_from_bytes(data[0][1])
                        logger.info('Fetched message %s', msg_id)
                        process_message(msg)
                        conn.store(msg_id, '+FLAGS', '\\Seen')
                        logger.info('Marked message %s as seen', msg_id)
            finally:
                conn.logout()
                logger.info('Logged out')
        except Exception as exc:
            logger.error('Error while polling: %s', exc)
        if os.environ.get('EMAIL_POLLER_RUN_ONCE') == '1':
            break
        time.sleep(60)


if __name__ == '__main__':
    poll_for_reports()
