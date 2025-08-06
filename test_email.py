
import time
from datetime import datetime, timedelta
from software.emailer import send_report

INTERVAL_MINUTES = 1   # change to 1–5 for quick tests, then back to 59

def main():
    # back‐date so first send is immediate
    last_sent = datetime.now() - timedelta(minutes=INTERVAL_MINUTES)

    print(f"Starting email loop: every {INTERVAL_MINUTES} minute(s). Ctrl+C to stop.")
    try:
        while True:
            now = datetime.now()
            if now - last_sent >= timedelta(minutes=INTERVAL_MINUTES):
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

if __name__ == "__main__":
    main()
