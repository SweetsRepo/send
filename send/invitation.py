import argparse
import smtplib
import ssl

from manager import manager

def _send_form_email(sender_email, sender_password, target_email, target_body):
    """
    Sends an email from sender to target with content in body

    Arguments:
        sender_email/password: Credentials of sender required for SMTP login
        target_email: Email address of remote user to send message to
        target_body: Body of email message to send from sender to target

    """
    port = 465
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, target_email, target_body)

def send_invite_email(sender_email, sender_password, target_email, port=None):
    """
    Sends a form email from sender to target with connection information in body

    Arguments:
        sender_email/password: Credentials of sender required for SMTP login
        target_email: Email address of remote user to send message to
        port: (Optional) Specific port to request target uses for connection

    """
    if port is None:
        port = 6000
    target_body = f"""Subject: SEND: File Transfer Request

Hello, {sender_email} would like to send you something!

Please specify a directory you would like to receive the files at and enter the
IP Address and Port given below:

IP: {manager.ip}
Port: {port}
Public Encryption Key: {manager.get_public_key().decode("ascii")}

Please send a confirmation email to them with your IP address and then start the
main application.

Thanks for using SEND!
    """
    _send_form_email(sender_email, sender_password, target_email, target_body)

def send_confirm_email(sender_email, sender_password, target_email):
    """
    Sends a confirmation form email from target back to sender with connection
    info

    Arguments:
        sender_email/password: Credentials of sender required for SMTP login
        target_email: Email address of remote user to send message to

    """
    target_body = f"""Subject: SEND: File Transfer Accept

Hello, {sender_email} is willing to recieve your file(s)!

Please add the ip address below to your whitelist and start the main application

IP: {manager.ip}

Thanks for using SEND!
    """
    _send_form_email(sender_email, sender_password, target_email, target_body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--invite",
        action="store_true",
        help="Flag indicating that an invite email should be sent"
    )
    parser.add_argument(
        "-c",
        "--confirm",
        action="store_true",
        help="Flag indicating that a confirmation email should be sent"
    )
    parser.add_argument(
        "sender_email",
        help="Email user would like to send email from. Note that less secure app access must be on https://myaccount.google.com/lesssecureapps"
    )
    parser.add_argument(
        "sender_password",
        help="Password corresponding to the email selected."
    )
    parser.add_argument(
        "target_email",
        help="Email user would liek to send email to"
    )
    args=parser.parse_args()

    if args.invite:
        send_invite_email(
            args.sender_email,
            args.sender_password,
            args.target_email
        )
    elif args.confirm:
        send_confirm_email(
            args.sender_email,
            args.sender_password,
            args.target_email
        )
