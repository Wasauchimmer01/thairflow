import pathlib, sys
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

import imaplib
import email
from email.message import Message
import re
import os
import time
import logging

from software.config import load_imap_config

logger = logging.getLogger('email_poller')
# Persist errors to file for later inspection
error_handler = logging.FileHandler('email_errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s'))
logger.addHandler(error_handler)


def process_message(msg: Message):
    """
    Save CSV attachments to downloads/ and return a list of (rp_id:int, filepath).
    Subject format example: "Sensor Log for 2025-08-07 pi_id: 2"
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

        safe_filename = filename.rstrip('.')  # handle '..csv' oddity
        out_name = f"{rp_id}_{ts_part}_{safe_filename}"
        out_path = os.path.join(dl_dir, out_name)

        try:
            payload = part.get_payload(decode=True)
            with open(out_path, "wb") as f:
                f.write(payload)
            logger.info("Saved attachment to %s", out_path)
            saved_paths.append((rp_id, out_path))
        except Exception as e:
            logger.error("Failed to save %s: %s", out_path, e)

    return saved_paths


def poll_for_reports_once(max_per_cycle: int | None = None) -> list[tuple[int, str]]:
    """
    Run one IMAP fetch cycle, save CSVs, and return a list of (rp_id, filepath).

    Robust to IMAP quota errors:
    - If FETCH fails for a message, skip it and continue.
    - If STORE (mark seen) fails due to OVERQUOTA, stop marking further messages
      (to avoid more errors), but still return the files we already saved so the
      caller can ingest them.
    """
    attachments: list[tuple[int, str]] = []

    cfg = load_imap_config()
    max_per_cycle = max_per_cycle or int(cfg.get("max_per_cycle", 50))
    per_cmd_sleep = float(cfg.get("per_command_sleep", 0.2))

    conn = None
    try:
        logger.info('Connecting to %s:%s', cfg["imap_host"], cfg["imap_port"])
        try:
            conn = imaplib.IMAP4_SSL(cfg["imap_host"], cfg["imap_port"])
            conn.login(cfg["username"], cfg["password"])
        except (OSError, imaplib.IMAP4.error):
            logger.warning("No internet connection – unable to poll emails")
            return attachments
        logger.info('Logged in as %s', cfg["username"])

        conn.select(cfg["mailbox"])
        logger.info('Mailbox selected: %s', cfg["mailbox"])

        typ, msg_ids = conn.search(None, *cfg["search_criteria"])
        if typ != "OK":
            logger.error("IMAP search failed: %s", typ)
            return attachments

        ids = msg_ids[0].split()
        if not ids:
            return attachments

        ids = ids[:max_per_cycle]  # backpressure to avoid quota hits
        logger.info("Found %d message(s); processing %d this cycle", len(msg_ids[0].split()), len(ids))

        # If Gmail complains while marking seen, we’ll stop marking to avoid crash
        allow_mark_seen = True

        for msg_id in ids:
            try:
                typ, msg_data = conn.fetch(msg_id, "(RFC822)")
                if typ != "OK":
                    logger.warning("Failed to fetch message %s: %s", msg_id, typ)
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                saved = process_message(msg)
                attachments.extend(saved)

                if allow_mark_seen:
                    # Be gentle with the server
                    time.sleep(per_cmd_sleep)
                    try:
                        conn.store(msg_id, "+FLAGS", "\\Seen")
                    except imaplib.IMAP4.abort as e:
                        # quota / bandwidth / other abort -> keep going without marking
                        logger.warning("IMAP abort while marking seen (likely OVERQUOTA). "
                                       "Leaving remaining messages UNSEEN for retry: %s", e)
                        allow_mark_seen = False
                    except imaplib.IMAP4.error as e:
                        logger.warning("IMAP error on STORE for %s: %s", msg_id, e)
                        # continue; we’ll just leave it unseen

            except imaplib.IMAP4.abort as e:
                logger.warning("IMAP abort while fetching %s: %s", msg_id, e)
                break
            except Exception as e:
                logger.exception("Unexpected error while processing %s: %s", msg_id, e)
                # continue with next id

        return attachments

    finally:
        if conn is not None:
            try:
                conn.logout()
                logger.info('Logged out')
            except Exception:
                # If we’re already disconnected because of abort, ignore.
                pass


def run_forever():
    """Continuously poll for reports, pausing on errors or empty cycles."""
    while True:
        try:
            attachments = poll_for_reports_once()
            if attachments:
                logger.info("Saved %d attachment file(s) this run", len(attachments))
                continue
        except Exception:
            logger.exception("Poller failure")

        logger.info("retrying in 15 minutes")
        next_attempt = time.time() + 15 * 60
        logger.info("Next attempt at %s", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_attempt)))
        while True:
            remaining = int(next_attempt - time.time())
            if remaining <= 0:
                break
            logger.info("Next attempt in %d seconds", remaining)
            time.sleep(min(60, remaining))


if __name__ == '__main__':
    run_forever()
