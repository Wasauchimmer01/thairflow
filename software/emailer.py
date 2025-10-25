import os
import json
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
# All email related logs are written to a dedicated ``longemail`` folder so
# the rest of the application can remain silent even when e‑mail delivery
# fails (e.g. no internet connection, Gmail problems, …).
LOG_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "longemail")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    log_file = os.path.join(LOG_DIR, "emailer.log")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

def load_email_config(path: str = "config_private/email_config.json") -> dict:
    """
    Load and validate email configuration from a JSON file.
    Raises:
        FileNotFoundError: If the JSON file does not exist.
        KeyError: If required keys are missing.
    Returns:
        dict: Parsed email configuration.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Email config file not found: {path}")
    with open(path, "r") as f:
        config = json.load(f)

    required = [
        "smtp_host",
        "smtp_port",
        "use_tls",
        "username",
        "password",
        "from_addr",
        "to_addrs"
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise KeyError(f"Missing required email config keys: {missing}")

    return config

def send_report(
    filepath: str,
    subject: str = None,
    body: str = None,
    config_path: str = "config_private/email_config.json"
) -> bool:
    """
    Send an email with the specified file as attachment.

    Args:
        filepath (str): Path to the file to attach.
        subject (str, optional): Email subject. If None, uses template from config.
        body (str, optional): Email body text. If None, uses template from config.
        config_path (str): Path to the email_config JSON file.

    Returns:
        bool: ``True`` if the e-mail was sent successfully, ``False`` otherwise.
    """
    # 1) Load and validate config
    cfg = load_email_config(config_path)

    # 2) Prepare subject and body, inserting today's date if templates exist
    date_str = datetime.now().strftime("%Y-%m-%d")
    subject = subject or cfg.get("subject_template", "Report for {date}").format(date=date_str)
    body    = body    or cfg.get("body_template",    "See attached file for {date}.").format(date=date_str)

    # 3) Build the MIME message
    msg = MIMEMultipart()
    msg["From"]    = cfg["from_addr"]
    msg["To"]      = ", ".join(cfg["to_addrs"])
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # 4) Attach the file
    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    filename = os.path.basename(filepath)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    # 5) Connect to SMTP, secure, authenticate, and send
    try:
        server = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"])
        if cfg.get("use_tls", False):
            server.starttls()
        server.login(cfg["username"], cfg["password"])
        server.sendmail(cfg["from_addr"], cfg["to_addrs"], msg.as_string())
        logger.info("Email with '%s' sent to %s", filename, cfg["to_addrs"])
        return True
    except Exception as exc:  # pragma: no cover - network errors are unpredictable
        logger.exception("Failed to send email: %s", exc)
        print(f"Email send failed: {exc}")
        return False
    finally:
        try:
            server.quit()
        except Exception:
            pass


if __name__ == "__main__":
    """Simple loop to manually test the email functionality."""
    import time
    from datetime import datetime, timedelta

    interval = 1  # minutes
    last_sent = datetime.now() - timedelta(minutes=interval)
    print(f"Starting email loop: every {interval} minute(s). Ctrl+C to stop.")

    try:
        while True:
            now = datetime.now()
            if now - last_sent >= timedelta(minutes=interval):
                if send_report(
                    filepath="daten.csv",
                    subject=f"Loop Test Sensor Log {now:%Y-%m-%d %H:%M}",
                    body="This is a looping test of the e-mail feature.",
                ):
                    print(f"[{now:%H:%M:%S}]  Email sent")
                    last_sent = now
                else:
                    print(f"[{now:%H:%M:%S}]  Failed to send (see log)")
            # check every second to avoid drift
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEmail loop stopped by user.")
