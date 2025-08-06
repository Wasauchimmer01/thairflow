from software.emailer import send_report

if __name__ == "__main__":
    send_report(
        filepath="daten.csv",
        subject="Test from test_email.py",
        body="Hello! Testing email feature from terminal script.",
        # config_path default is "email_config.json" so you can omit it if yours is named that
    )
    print("send_report() completed.")