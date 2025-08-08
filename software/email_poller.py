import pathlib
import sys
import re, os

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


'''def process_message(msg: Message) -> None:
    """Placeholder for processing email messages."""
    logger.info('Processing message: %s', msg.get('Subject'))
'''
'''def process_message(msg: Message) -> None:
    """Save any CSV attachments to disk."""
    subject = msg.get('Subject', '<no subject>')
    logger.info('Processing message: %s', subject)

    for part in msg.walk():
        filename = part.get_filename()
        if not filename:
            continue
        if filename.lower().endswith('.csv'):
            data = part.get_payload(decode=True)
            out_path = os.path.join('downloads', filename)
            os.makedirs('downloads', exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(data)
            logger.info('Saved attachment to %s', out_path)
'''
''''
def process_message(msg):
    subject = msg.get('Subject', '<no subject>')
    logger.info("Processing message: %s", subject)

    # Ensure downloads folder exists
    os.makedirs("downloads", exist_ok=True)

    for part in msg.walk():
        filename = part.get_filename()
        if not filename or not filename.lower().endswith(".csv"):
            continue

        data = part.get_payload(decode=True)
        path = os.path.join("downloads", filename)
        with open(path, "wb") as f:
            f.write(data)
        logger.info("Saved attachment to %s", path)'''
'''
def process_message(msg):
    subject = msg.get('Subject', '')
    # 1) Extract rpi_id from subject
    m = re.search(r'pi_id[:\s]+(\d+)', subject)
    rpi_id = m.group(1) if m else 'unknown'
    logger.info('Processing message: %s (rpi_id=%s)', subject, rpi_id)

    # 2) Ensure downloads/ exists
    dl_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(dl_dir, exist_ok=True)

    # 3) Iterate parts and save CSVs
    for part in msg.walk():
        filename = part.get_filename()
        if not filename or not filename.lower().endswith(".csv"):
            continue

        # Clean up any stray dots (e.g. '..csv')
        safe_filename = filename.rstrip('.')
        # Build output name: prepend rpi_id and timestamp from subject
        ts_part = subject.split('for',1)[-1].split('pi_id',1)[0].strip().replace(' ','_').replace(':','-')
        out_name = f"{rpi_id}_{ts_part}_{safe_filename}"
        out_path = os.path.join(dl_dir, out_name)

        try:
            payload = part.get_payload(decode=True)
            with open(out_path, "wb") as f:
                f.write(payload)
            logger.info("Saved attachment to %s", out_path)
        except Exception as e:
            logger.error("Failed to save %s: %s", out_path, e)
'''
'''
def process_message(msg):
    """
    Save any CSV attachments to downloads/ and return a list of saved file paths.
    """
    saved_paths = []
    subject = msg.get('Subject', '')
    # extract rpi_id as before…
    # ensure downloads/ exists…
    for part in msg.walk():
        filename = part.get_filename()
        if not filename or not filename.lower().endswith(".csv"):
            continue

        # build out_path exactly as before…
        # then write payload...
        try:
            payload = part.get_payload(decode=True)
            with open(out_path, "wb") as f:
                f.write(payload)
            logger.info("Saved attachment to %s", out_path)
            saved_paths.append((rpi_id, out_path))
        except Exception as e:
            logger.error("Failed to save %s: %s", out_path, e)
'''
'''def process_message(msg):
    """
    Save any CSV attachments to downloads/ and return a list of (rpi_id, filepath).
    """
    saved_paths = []

    subject = msg.get('Subject', '')
    # Extract rpi_id from subject
    m = re.search(r'pi_id[:\s]+(\d+)', subject)
    rpi_id = m.group(1) if m else 'unknown'
    logger.info('Processing message: %s (rpi_id=%s)', subject, rpi_id)

    # Ensure downloads/ exists
    dl_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(dl_dir, exist_ok=True)

    # Iterate parts and save CSVs
    for part in msg.walk():
        filename = part.get_filename()
        if not filename or not filename.lower().endswith(".csv"):
            continue

        # Clean up stray dots, e.g. '..csv'
        safe_filename = filename.rstrip('.')

        # Build timestamp portion from subject
        ts_part = subject.split('for', 1)[-1].split('pi_id', 1)[0].strip()
        ts_part = ts_part.replace(' ', '_').replace(':', '-')

        # Build output filename and full path
        out_name = f"{rpi_id}_{ts_part}_{safe_filename}"
        out_path = os.path.join(dl_dir, out_name)  # define here

        try:
            payload = part.get_payload(decode=True)
            with open(out_path, "wb") as f:
                f.write(payload)
            logger.info("Saved attachment to %s", out_path)
            saved_paths.append((rpi_id, out_path))
        except Exception as e:
            # out_path is in scope here
            logger.error("Failed to save %s: %s", out_path, e)

    return saved_paths
'''

'''def process_message(msg):
    """
    Save CSV attachments to downloads/ and return a list of (rpi_id, filepath).
    Subject format example: "Sensor Log for 2025-08-07 pi_id: 2"
    """
    saved_paths = []

    subject = msg.get('Subject', '')
    # Extract rpi_id from subject
    m = re.search(r'pi_id[:\s]+(\d+)', subject)
    rpi_id = m.group(1) if m else 'unknown'
    logger.info('Processing message: %s (rpi_id=%s)', subject, rpi_id)

    # Ensure downloads/ exists
    dl_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(dl_dir, exist_ok=True)

    # Timestamp chunk from subject (between 'for' and 'pi_id')
    ts_part = subject.split('for', 1)[-1].split('pi_id', 1)[0].strip()
    ts_part = ts_part.replace(' ', '_').replace(':', '-')

    # Iterate all parts and save CSVs
    for part in msg.walk():
        filename = part.get_filename()
        if not filename or not filename.lower().endswith(".csv"):
            continue

        safe_filename = filename.rstrip('.')  # handle '..csv' oddity
        out_name = f"{rpi_id}_{ts_part}_{safe_filename}"
        out_path = os.path.join(dl_dir, out_name)

        try:
            payload = part.get_payload(decode=True)
            with open(out_path, "wb") as f:
                f.write(payload)
            logger.info("Saved attachment to %s", out_path)
            saved_paths.append((rpi_id, out_path))
        except Exception as e:
            logger.error("Failed to save %s: %s", out_path, e)

    return saved_paths'''

def process_message(msg):
    """
    Save CSV attachments to downloads/ and return a list of (rp_id:int, filepath).
    Subject format: "Sensor Log for 2025-08-07 pi_id: 2"
    """
    saved_paths = []

    subject = msg.get('Subject', '')
    m = re.search(r'pi_id[:\s]+(\d+)', subject)
    rp_id = int(m.group(1)) if m else -1
    logger.info('Processing message: %s (rp_id=%s)', subject, rp_id)

    dl_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(dl_dir, exist_ok=True)

    ts_part = subject.split('for', 1)[-1].split('pi_id', 1)[0].strip()
    ts_part = ts_part.replace(' ', '_').replace(':', '-')

    for part in msg.walk():
        filename = part.get_filename()
        if not filename or not filename.lower().endswith(".csv"):
            continue

        safe_filename = filename.rstrip('.')
        out_name = f"{rp_id}_{ts_part}_{safe_filename}"
        out_path = os.path.join(dl_dir, out_name)

        try:
            payload = part.get_payload(decode=True)
            with open(out_path, "wb") as f:
                f.write(payload)
            logger.info("Saved attachment to %s", out_path)
            saved_paths.append((rp_id, out_path))  # rp_id is INT now
        except Exception as e:
            logger.error("Failed to save %s: %s", out_path, e)

    return saved_paths

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
'''
def poll_for_reports_once() -> list[tuple[str, str]]:
    """
    Run one IMAP search+fetch cycle, save CSVs, and return
    a list of (rpi_id, filepath) for each saved attachment.
    """
    attachments = []
    config = load_imap_config()
    conn = imaplib.IMAP4_SSL(config["imap_host"], config["imap_port"])
    conn.login(config["username"], config["password"])
    conn.select(config["mailbox"])
    typ, msg_ids = conn.search(None, *config["search_criteria"])
    for msg_id in msg_ids[0].split():
        typ, msg_data = conn.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        # save_ct returns list of file paths
        saved = process_message(msg)  # modify to return list of paths
        attachments.extend(saved)
        conn.store(msg_id, "+FLAGS", "\\Seen")
    conn.logout()
    return attachments'''
'''def poll_for_reports_once() -> list[tuple[str,str]]:
    attachments = []
    config = load_imap_config()
    conn = imaplib.IMAP4_SSL(config["imap_host"], config["imap_port"])
    conn.login(config["username"], config["password"])
    conn.select(config["mailbox"])
    typ, msg_ids = conn.search(None, *config["search_criteria"])
    for msg_id in msg_ids[0].split():
        typ, msg_data = conn.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        saved = process_message(msg)       # now returns list of (rpi_id, path)
        attachments.extend(saved)          # extends the list
        conn.store(msg_id, "+FLAGS", "\\Seen")
    conn.logout()
    return attachments'''

def poll_for_reports_once() -> list[tuple[str, str]]:
    """
    Run one IMAP fetch cycle, save CSVs, and return a list of (rpi_id, filepath).
    """
    attachments: list[tuple[str, str]] = []
    cfg = load_imap_config()
    conn = imaplib.IMAP4_SSL(cfg["imap_host"], cfg["imap_port"])
    conn.login(cfg["username"], cfg["password"])
    conn.select(cfg["mailbox"])
    typ, msg_ids = conn.search(None, *cfg["search_criteria"])
    for msg_id in msg_ids[0].split():
        typ, msg_data = conn.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        saved = process_message(msg)             # returns list[(rpi_id, path)]
        attachments.extend(saved)
        conn.store(msg_id, "+FLAGS", "\\Seen")
    conn.logout()
    return attachments

if __name__ == '__main__':
    poll_for_reports()
