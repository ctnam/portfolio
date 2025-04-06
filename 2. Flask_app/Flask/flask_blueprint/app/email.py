
from flask_mailing import Message
from . import mail
from flask_login import current_user

async def send_confirmationmail(recipientt, _template_body, **kwargs):
    message = Message(recipients = [recipientt],
                        subject = 'User registration confirmed',
                        template_body = _template_body)
    await mail.send_message(message, template_name='mail/newuserconfirmation.html')

async def resend_confirmationmail(recipient, _template_body, **kwargs):
    message = Message(recipients = [recipientt],
                        subject = 'User registration confirmed',
                        template_body = _template_body)
    await mail.send_message(message, template_name='mail/resend_newuserconfirmation.html')

####################

async def mail_todayschedule(recipient, _template_body, **kwargs):
    message = Message(recipients = [recipient],
                        subject = 'Today schedule',
                        template_body = _template_body)
    await mail.send_message(message, template_name='daytasks_mail.html')

async def mail_tomorrowschedule(recipient, _template_body, **kwargs):
    message = Message(recipients = [recipient],
                        subject = 'Tomorrow schedule',
                        template_body = _template_body)
    await mail.send_message(message, template_name='daytasks_mail.html')

async def mail_thisweekschedule(recipient, _template_body, **kwargs):
    message = Message(recipients = [recipient],
                        subject = 'This week schedule',
                        template_body = _template_body)
    await mail.send_message(message, template_name='weektasks_mail.html')

async def mail_nextweekschedule(recipient, _template_body, **kwargs):
    message = Message(recipients = [recipient],
                        subject = 'Next week schedule',
                        template_body = _template_body)
    await mail.send_message(message, template_name='weektasks_mail.html')
