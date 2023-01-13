from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, Subject, To

from marinachain.secrets import SENDGRID_API_KEY

DEFAULT_FROM = "tech@marinachain.io"


def send_email(
        to_address: str,
        subject: str,
        body_html: str,
        from_address: str = DEFAULT_FROM):
    sg = SendGridAPIClient(SENDGRID_API_KEY)

    mail = Mail()
    mail.to = To(to_address)
    mail.from_email = Email(from_address)
    mail.subject = Subject(subject)
    mail.content = Content('text/html', body_html)

    response = sg.send(mail)
    return response
