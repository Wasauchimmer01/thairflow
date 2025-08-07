# Features

## Feature 2: Email Polling

The `software/email_poller.py` module monitors an IMAP inbox for new messages. Each retrieved email is passed as a raw `email.message.Message` object to a placeholder `process_message(msg)` function. Feature 3 will implement attachment extraction and further handling of this message object.

This email polling relies on **Feature 1: Data Contract Definition** to interpret CSV attachments that will be parsed later in the pipeline. Any change to the CSV schema defined in Feature 1 may require updates to the polling workflow.
