import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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
) -> None:
    """
    Send an email with the specified file as attachment.

    Args:
        filepath (str): Path to the file to attach.
        subject (str, optional): Email subject. If None, uses template from config.
        body (str, optional): Email body text. If None, uses template from config.
        config_path (str): Path to the email_config JSON file.

    Raises:
        Exception: Propagates any error during SMTP connection or sending.
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
    server = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"])
    try:
        if cfg.get("use_tls", False):
            server.starttls()
        server.login(cfg["username"], cfg["password"])
        server.sendmail(cfg["from_addr"], cfg["to_addrs"], msg.as_string())
    finally:
        server.quit()


'''if __name__ == "__main__":
    \gernerat 10 .csv File
    for file in files
        emailer filename subject ...
        '''
# only for test 
if __name__ == "__main__":
    from datetime import datetime, timedelta
    interval = 1 
        # back‐date so first send is immediate
    last_sent = datetime.now() - timedelta(minutes=interval)

    print(f"Starting email loop: every {interval} minute(s). Ctrl+C to stop.")
    try:
        while True:
            now = datetime.now()
            if now - last_sent >= timedelta(minutes=interval):
                try:
                    send_report(
                        filepath="daten.csv",
                        subject=f"Loop Test Sensor Log {now:%Y-%m-%d %H:%M}",
                        body="This is a looping test of the e-mail feature."
                    )
                    print(f"[{now:%H:%M:%S}]  Email sent")
                    last_sent = now
                except Exception as e:
                    print(f"[{now:%H:%M:%S}]  Failed to send: {e}")
            # check every second to avoid drift
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEmail loop stopped by user.")