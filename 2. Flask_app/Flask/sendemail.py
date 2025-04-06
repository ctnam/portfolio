from flask import Flask, jsonify
from flask_mailing import Mail, Message
import httpx
import os


mail = Mail()

def create_app():
    app = Flask(__name__)


    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_SERVER'] = "smtp.gmail.com"
    app.config['MAIL_TLS'] = True
    app.config['MAIL_SSL'] = False
    mail.init_app(app)

    return app

#send a simple email using flask_mailing module.

app = create_app()

@app.get("/email")
async def simple_send():   # httpx module

    message = Message(
        subject="Flask-Mailing module Confirmation",
        recipients=["namcaocomebackp66@gmail.com"],
        body="This email is to notify that Flask-Mailing is working fine, and the email has been sent successfully.",
        )


    await mail.send_message(message)
    return jsonify(status_code=200, content={"message": "email has been sent"})
