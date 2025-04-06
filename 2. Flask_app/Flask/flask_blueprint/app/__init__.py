from flask import Flask, render_template   # to render

from flask_bootstrap import Bootstrap   # for html css
from flask_mailing import Mail   # for mail
from flask_moment import Moment   # for time
from flask_sqlalchemy import SQLAlchemy   # for db

from config import config # config.py

from flask_login import LoginManager

from flask_pagedown import PageDown

from flask_dotenv import DotEnv


from flask import request
from flask_cloudy import Storage


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # sets the endpoint for the login page - redirect to the login page when an anonymous user tries to access a protected page
                                        # blueprint 'auth'
pagedown = PageDown()
env = DotEnv()

storage = Storage()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])   ### See config.py
    config[config_name].init_app(app)   ###

    ## Thanks flask-cloudy crew
	#app.config.update({"STORAGE_PROVIDER": "LOCAL", "STORAGE_KEY": "", "STORAGE_SECRET": "", "STORAGE_CONTAINER": "./",
                        #"STORAGE_SERVER": True, "STORAGE_SERVER_URL": "/files", "STORAGE_ALLOWED_EXTENSIONS": ["png", "jpg", "jpeg", "wav", "m4a", "mov"]})
	#"STORAGE_PROVIDER": "LOCAL", # Can also be S3, GOOGLE_STORAGE, etc...LOCAL
        #^^ S3 S3_US_WEST S3_US_WEST_OREGON S3_EU_WEST S3_AP_SOUTHEAST S3_AP_NORTHEAST GOOGLE_STORAGE AZURE_BLOBS CLOUDFILES
	#"STORAGE_KEY": "",
        #^^The access key of the cloud storage provider #None for LOCAL
	#"STORAGE_SECRET": "",
        #^^The access secret key of the cloud storage provider #None for LOCAL
	#"STORAGE_CONTAINER": "./",
        #^^a directory path for local, bucket name of cloud
	#"STORAGE_SERVER": True,
        #^^For LOCAL provider only. #True to expose the files in the container so they can be accessed #Default: True
	#"STORAGE_SERVER_URL": "/files",
        #^^The url endpoint to access files on LOCAL provider (For LOCAL provider only)
    #"STORAGE_ALLOWED_EXTENSIONS": ["png", "jpg", "jpeg", "wav", "m4a", "mov"]
	#})

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app) # ~ form textareafield
    env.init_app(app)


    storage.init_app(app)

    # Register Blueprints
    from .main import main as main_blueprint ### import blueprint object 'main' from folder 'main'/__init__
    app.register_blueprint(main_blueprint) ### register blueprint 'main'
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth') # url_prefix argument is optional -> http://localhost:5000/auth/login
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    ###### attach routes and custom error pages here ######
    from flask_login import login_required
    @app.route('/secret')
    @login_required
    def secret():
        return 'So sorry! Only authenticated users have the access.'

    from .decorators import admin_required, permission_required
    from .models import Permission
    @app.route('/admin')   ##
    @login_required
    @admin_required
    def for_admins_only():
        return "For administrators!"

    @app.route('/moderate')   ##
    @login_required
    @permission_required(Permission.MODERATE)
    def for_moderators_only():
        return "For comment moderators!"

    # ...
    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)
    # ...

    ##app.config.update({"STORAGE_PROVIDER": "LOCAL", "STORAGE_KEY": "", "STORAGE_SECRET": "", "STORAGE_CONTAINER": "./",
                    ##"STORAGE_SERVER": True, "STORAGE_SERVER_URL": "/files", "STORAGE_ALLOWED_EXTENSIONS": ["png", "jpg", "jpeg", "wav", "m4a", "mov"]})
    ##Class## Storage(provider, key=None, secret=None, container=None, allowed_extensions=None)
        # provider: The storage provider - LOCAL, S3, S3_US_WEST, GOOGLE_STORAGE,..
        # key: The access key of the cloud storage. None when provider is LOCAL
        # secret: The secret access key of the cloud storage. None when provider is LOCAL
        # container: For cloud storage, use the BUCKET NAME. For LOCAL provider, it's the directory path where to access the files
        # allowed_extensions: List of extensions to upload
    ## Storage.get(object_name) : Get an object (flask-cloudy Object) in the storage by name, relative to the container.
            # method .save_to(destination, name=None, overwrite=False, delete_on_failure=True)
            # method .download_url(timeout=60, name=None)
    ## Storage.upload(file, name=None, prefix=None, extension=[], overwrite=False, public=False, random_name=False)


    ############################ Flask-cloudy
    from flask import render_template, session, redirect, url_for, flash, request, make_response
    from app.decorators import admin_required
    @app.route("/upload", methods=["POST", "GET"])
    @admin_required
    def upload():
        final_url = request.cookies.get('final_url', '')
        if request.method == "POST":
            rep = make_response(redirect(url_for('.upload')))
            file = request.files.get("file")
            my_upload = storage.upload(file)
            # some useful properties
            name = my_upload.name
            extension = my_upload.extension
            size = my_upload.size
            url = my_upload.url

            rep.set_cookie('final_url', str(url))
        return render_template("upload.html", final_url=final_url)
    	# "my-picture.jpg" => it will return a url in the format: http://domain.com/files/my-picture.jpg

    	# A download endpoint, to download the file
    @app.route("/download/<path:object_name>")
    @admin_required
    def download(object_name):
        my_object = storage.get(object_name)
        if my_object:
            download_url = my_object.download()
            return download_url
        else:
            abort(404, "File doesn't exist")


    return app
