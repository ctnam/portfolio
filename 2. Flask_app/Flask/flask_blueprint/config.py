import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pN,9)]l^IO9K70-KZ#^5dAjw8462fmY0hz75;+@VVzsTayu'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    #MAIL_TLS = os.environ.get('MAIL_TLS', 'true').lower() in \
        #['true', 'on', '1']
    MAIL_TLS = True
    MAIL_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    FLASKE_ADMIN = 'namcaocomebackp66@gmail.com'
    FLASKE_POSTS_PER_PAGE = 5
    FLASKE_COMMENTS_PER_PAGE = 5

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SQLALCHEMY_RECORD_QUERIES = True
    FLASKE_SLOW_DB_QUERY_TIME = 0.5

    SSL_REDIRECT = False

    #Flask-cloudy#
    STORAGE_PROVIDER = "LOCAL"
    STORAGE_KEY = None    # formerly: ""
    STORAGE_SECRET = None   # formerly: ""
    STORAGE_CONTAINER = "./files"   # formerly: "./"
    STORAGE_SERVER = True
    STORAGE_SERVER_URL = "/files"
    STORAGE_ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "wav", "m4a", "mov"]

    @staticmethod
    def init_app(app):
        pass



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKE_MAIL_SENDER,
            toaddrs=[cls.FLASKE_ADMIN],
            subject = 'Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr  ## Heroku considers any output written by the application to stdout or stderr logs
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Adding support for proxy servers // Handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_REDIRECT = True if os.environ.get('DYNO') else False  # only set to True if the environment variable DYNO exists


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


# For Unix-based servers, logging can be sent to the syslog daemon. A new configuration specifically for Unix can be created as a subclass of ProductionConfig
# With this configuration, application logs will be written to the configured syslog messages file, typically /var/log/messages or /var/log/syslog depending on the Linux distribution
class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)




config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}
