from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired,Length,Regexp,Email,Required
from ..models import User,Role

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Save')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Which Role', coerce=int)   ### WTForm’s wrapper for the <select> HTML form control, which implements a drop-down list, used in this form to select a user role
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Save')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        ### role.choices = list of tuples
        self.role.choices = [(role.id, role.rolename)
                             for role in Role.query.order_by(Role.rolename).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

from flask_pagedown.fields import PageDownField
class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[Required()])
    #print(dir(body.field_class))
    submit = SubmitField('Submit')
class EditPostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Update')


class CommentForm(FlaskForm):
    body = PageDownField('', validators=[Required()])
    submit = SubmitField('Submit')
class EditCommentForm(FlaskForm):
    body = PageDownField('', validators=[Required()])
    submit = SubmitField('Update')








from wtforms import DateTimeField
from ..models import Tasktype
class TaskForm(FlaskForm):
    searchsubmit = SubmitField('Search')
    taskname = StringField ('Name of that task')
    priority = SelectField(choices=["Normal", "High"])
    info = StringField('Essential information:')
    desc = TextAreaField('Full description:')
    ##
    day = StringField('Day (1-31)')
    month = StringField('Month (1-12)')
    year = StringField('Year (Currently 2021) ')
    ##
    hour = StringField('Hour (0-23)')
    minute = StringField('Minute (0-59)')
    #second = StringField('Second (0-59)')
    est_endtime = StringField('Ending latest by (18:5)', validators=[Required()])
    ##
    type = SelectField('What type?', coerce=int) #####
    submit = SubmitField('Create')
    def __init__(self, task, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.type.choices = [(tasktype.id, tasktype.name)
                             for tasktype in Tasktype.query.order_by(Tasktype.id).all()]
        self.task = task

class TaskUpdateForm(FlaskForm):
    Finished = BooleanField('FINISHED')
    taskname = StringField ('Name of that task', validators=[DataRequired()])
    Result = TextAreaField('RESULT:')
    priority = SelectField(choices=["Normal", "High"])
    info = StringField('Essential information:')
    desc = TextAreaField('FULL DESCRIPTION:')
    ##
    day = StringField('Day (1-31)', validators=[DataRequired()])
    month = StringField('Month (1-12)', validators=[DataRequired()])
    year = StringField('Year (Currently 2021)', validators=[DataRequired()])
    ##
    hour = StringField('Hour (0-23)', validators=[DataRequired()])
    minute = StringField('Minute (0-59)')
    #second = StringField('Second (0-59)')
    est_endtime = StringField('Ending latest by              (yyyy-mm-dd hh:mm:ss)')
    ##
    type = SelectField('What type? ', coerce=int) #####
    submit = SubmitField('Update')
    def __init__(self, task, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)
        self.type.choices = [(tasktype.id, tasktype.name)
                             for tasktype in Tasktype.query.order_by(Tasktype.id).all()]
        self.task = task

class TaskModifyForm(FlaskForm):
    Finished = BooleanField('Finished')
    taskname = StringField ('Name of that task', validators=[DataRequired()])
    Result = TextAreaField('Result')
    priority = SelectField(choices=["Normal", "High"])
    info = StringField('Essential information')
    desc = TextAreaField('Full description')
    ##
    day = StringField('Day (1-31)', validators=[DataRequired()])
    month = StringField('Month (1-12)', validators=[DataRequired()])
    year = StringField('Year (Currently 2021)', validators=[DataRequired()])
    hour = StringField('Hour (0-23)', validators=[DataRequired()])
    minute = StringField('Minute (0-59)')
    #second = StringField('Second (0-59)')
    est_endtime = StringField('Ending latest by (yyyy-mm-dd hh:mm:ss)')
    ##
    type = SelectField('Type', coerce=int) #####
    creationtime = DateTimeField('Creation timepoint of this task information')
    trashed = BooleanField('Trashed')
    submit = SubmitField('Save')
    def __init__(self, task, *args, **kwargs):
        super(TaskModifyForm, self).__init__(*args, **kwargs)
        self.type.choices = [(tasktype.id, tasktype.name)
                             for tasktype in Tasktype.query.order_by(Tasktype.id).all()]
        self.task = task




class CreateInsulinTypeForm(FlaskForm):
    full_name = StringField('Full name of that insulin type', validators=[Required()])
    full_description = PageDownField('General usage, identity properties', validators=[Required()])
    ##
    storing_unit = SelectField('Storing unit', choices=['Pen(s)/Needle(s)', 'Bottle(s)/Box(es)', 'Tablet(s)'])
    amount_perstoringunit = StringField('Quantity in each storing unit', validators=[Required()])
    ##
    manufacturer = StringField('Manufacturer')
    origin = StringField('Origin')
    submit = SubmitField('Add')

from ..models import NamsInsulin
class addnewpurchase_form(FlaskForm):
    type = SelectField('Type of Insulin', coerce=int)  ####
    purchase_info = StringField('Purchase info')
    storing_unit = SelectField('Storing unit', choices=['Pen(s)/Needle(s)', 'Bottle(s)/Box(es)', 'Tablet(s)'])  ####
    quantity = StringField('How many full-new ones purchased?')
    submit1 = SubmitField('Add up')
    added = StringField('Total quantity added manually (smallest unit)')
    deducted = StringField('Total quantity deducted manually (smallest unit)')
    submit1m = SubmitField('Adjust manually')
    def __init__(self, namsinsulin, *args, **kwargs):
        super(addnewpurchase_form, self).__init__(*args, **kwargs)
        self.type.choices = [(insulin.id, insulin.insulin_name)
                             for insulin in NamsInsulin.query.filter_by(currently_inuse=True).order_by(NamsInsulin.id).all()]
        self.namsinsulin = namsinsulin

class updateinfo_form(FlaskForm):
    type = SelectField('Type of Insulin', coerce=int)  ####
    info = PageDownField('Doctor info; notes about personal usage, dosage')
    submit2 = SubmitField('Update')
    def __init__(self, namsinsulin, *args, **kwargs):
        super(updateinfo_form, self).__init__(*args, **kwargs)
        self.type.choices = [(insulin.id, insulin.insulin_name)
                             for insulin in NamsInsulin.query.filter_by(currently_inuse=True).order_by(NamsInsulin.id).all()]
        self.namsinsulin = namsinsulin

class modifycurrentamount_form(FlaskForm):
    type = SelectField('Type of Insulin', coerce=int)  ####
    submit3r = SubmitField('Retrieve data')
    avgamount_perday = StringField('Quantity injected each day')
    avgamount_pertime = StringField('Quantity injected each time')
    current_amount = StringField('Total quanity available currently')
    currently_inuse = BooleanField('Still using this Insulin?')
    submit3 = SubmitField('Save')
    def __init__(self, namsinsulin, *args, **kwargs):
        super(modifycurrentamount_form, self).__init__(*args, **kwargs)
        self.type.choices = [(insulin.id, insulin.insulin_name)
                             for insulin in NamsInsulin.query.filter_by(currently_inuse=True).order_by(NamsInsulin.id).all()]
        self.namsinsulin = namsinsulin

class addpumpchanges_form(FlaskForm):
    type = SelectField('Type of Insulin', coerce=int)  ####
    info = StringField('Reasons for that change..')
    onthescale = SelectField('On the scale of', choices=['One injection time', 'One day'])
    changedquantity = StringField('How much is that changed quantity?')
    submit4 = SubmitField('Update')
    def __init__(self, namsinsulin, *args, **kwargs):
        super(addpumpchanges_form, self).__init__(*args, **kwargs)
        self.type.choices = [(insulin.id, insulin.insulin_name)
                             for insulin in NamsInsulin.query.filter_by(currently_inuse=True).order_by(NamsInsulin.id).all()]
        self.namsinsulin = namsinsulin

class AmendInsulin(FlaskForm):
    full_name = StringField('Full name of that insulin type', validators=[Required()])
    full_description = TextAreaField('General usage, identity properties', validators=[Required()])
    storing_unit = SelectField('Storing unit', choices=['Pen(s)/Needle(s)', 'Bottle(s)/Box(es)', 'Tablet(s)'])
    amount_perstoringunit = StringField('Quantity in each storing unit', validators=[Required()])
    manufacturer = StringField('Manufacturer')
    origin = StringField('Origin')
    submit = SubmitField('Save')

class ConfirmAuthorityForm(FlaskForm):
    secret_key = StringField('')
    submit = SubmitField('Submit')

from wtforms import RadioField
class InsulinSettingForm(FlaskForm):
    option = RadioField('Select: ', choices=['None', 'Below 7 Days alert', '2 Weeks alert', '1 Month alert'])
    submit = SubmitField('Set')








class DateTimeForm(FlaskForm):
    day = StringField('Day:')
    month = SelectField('Month:', choices=['January','February','March','April','May','June','July','August','September','October','November','December'])
    year = StringField('Year:')
    submit = SubmitField('Submit')
class DeadlineDisplayMode(FlaskForm):
    set = SubmitField('Retrieve')
    option = RadioField(choices=['Current deadlines', 'Imported from Tasks'])
class FilterTimerangeDisplay(FlaskForm):
    opt1 = BooleanField('Today')
    opt2 = BooleanField('This week')
    opt3 = BooleanField('This month')
    set = SubmitField('Retrieve')
class EmailForm(FlaskForm):
    email = StringField('Mail address', validators=[Email(), Required()])
    send = SubmitField('Send')
