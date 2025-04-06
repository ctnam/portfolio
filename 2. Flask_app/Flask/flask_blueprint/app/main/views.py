from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request, current_app

from . import main   ### import blueprint object 'main'
from .forms import NameForm, EditProfileForm   # still missing now (move codes there soon)

from .. import db   ### folder 'app'/__init__.py   at line 11 'db = SQLAlchemy()'
from ..models import User,Role,Comment   # still missing now (move codes there soon)

from flask_login import login_required
from flask_login import current_user

from ..models import Post
from .forms import PostForm,EditPostForm,CommentForm
from ..models import Permission

import time
from ..ext_functions import currenttimepoint, currentyear, currentmonth

@main.route('/', methods=['GET', 'POST'])   ### 'main.route' instead of 'app.route'
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object()) # Line 192 and 220 'Models.py'
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))

    ### Paginating the blog post list
    page = request.args.get('page', 1, type=int) # When a page isn’t given, a default page of 1 (the first page) is used
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5, error_out=False) # Flask-SQLAlchemy’s 'paginate()', not 'all()'
    posts = pagination.items


    show_followed = False
    show_amem = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
        print('show_followed =' + str(show_followed))
        show_amem = bool(request.cookies.get('show_amem', ''))
        print('show_amem =' + str(show_amem))

    if show_amem==True and show_followed==False:
        querying = Post.query.filter_by(toquery_authornamestartswitha=True)
    if show_followed==True and show_amem==False:
        querying = current_user.followed_posts
    if show_followed==False and show_amem==False:
        querying = Post.query
    pagination = querying.order_by(Post.timestamp.desc()).paginate(page, per_page=5,error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, show_amem=show_amem, pagination=pagination)
## Return value of paginate() is an object of class Pagination
## Flask-SQLAlchemy pagination object attributes: items, query, page, prev_num, next_num, has_next, has_prev, pages, per_page, total

from flask import make_response
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    resp.set_cookie('show_amem', '', max_age=30*24*60*60)
    return resp
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    resp.set_cookie('show_amem', '', max_age=30*24*60*60)
    return resp
@main.route('/amem')
@login_required
def show_amem():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_amem', '1', max_age=30*24*60*60)
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp





# profile page route
@main.route('/user/<username>')
def user(username):
    from flask import abort
    user = User.query.filter_by(username=username).first_or_404()   ###### Excellent method!
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    ### Good ^^^
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)



# edit profile route
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())   ###### Excellent method!
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username)) # Line 31
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)



from ..decorators import admin_required
from .forms import EditProfileAdminForm
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])   ### 'id' -> Line 43 in 'user.html'
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id) ###### User object with the argumented 'id'
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)   ### Lines 95-99 models.py
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id   ###
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)



@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)   ###
    latestp = (post.comments.count() - 1) // current_app.config['FLASKE_COMMENTS_PER_PAGE'] + 1
    form = CommentForm()
    #print('FORM.BODY is below')
    #print(form.body)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object()) #### current_user is a context variable proxy object

        db.session.add(comment)
        db.session.commit()
        latestp = (post.comments.count() - 1) // current_app.config['FLASKE_COMMENTS_PER_PAGE'] + 1
        time.sleep(4)
        flash('Your comment has been published.')
        #return redirect(url_for('.post', id=post.id, page=-1)) ##~~## A special page number that is used to request the last page of comments
        return redirect(url_for('.post', id=post.id, page=latestp))
    page = request.args.get('page', latestp, type=int)  #### PAGE based on user's request, otherwise =default=latestp
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(  ##~~## latest comments at the last page
        page, per_page=current_app.config['FLASKE_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination, post=post)

from .forms import EditCommentForm
@main.route('/editcomment/<int:id>', methods=['GET', 'POST'])
@login_required
def editcomment(id):
    comment = Comment.query.get_or_404(id)
    post = Post.query.get_or_404(comment.post_id)
    if current_user != comment.author and not current_user.is_administrator():
        abort(403)
    form = EditCommentForm()
    form.submit.data==False
    #form.body.data = comment.body   ###### NOT HERE
    if form.validate_on_submit():
        comment.body = form.body.data   ###### this is EDIT
        db.session.add(comment)
        db.session.commit()
        flash(''' Your comment has just been updated. ''')
        #return redirect(url_for('.editcomment', id=comment.id))
    form.body.data = comment.body

# per_page=5, comment 30 at p6, comment 31 at p7
    numberofpages = latestpage = (post.comments.count() - 1) // 5 + 1
    for p in range(1,latestpage+1):
        pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(p, per_page=5, error_out=False)
        if Comment.query.filter_by(id=comment.id).first() in pagination.items:
            currentpage = p

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(latestpage+1, per_page=5, error_out=False)
    comments = pagination.items

    if form.submit.data==True:
        #time.sleep(4)
        pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(currentpage, per_page=5, error_out=False)
        comments = pagination.items
        commentid = str(comment.id)
        try:
            with open('commentid', 'w') as f:
                f.write(commentid)
        except FileNotFoundError:
            pass
        return redirect(url_for('.post', id=post.id, page=currentpage))

    commentid = str(comment.id)
    return render_template('post_copy.html', form=form, post=post, posts=[post],
                            pagination=pagination, comments=comments)


from flask import abort
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)



from ..decorators import permission_required
## follow route and view function
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user) # db.session.add(user)
    db.session.commit()
    flash('You have just followed %s.' % username)
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You have not been following this user yet.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You have just unfollowed %s.' % username)
    return redirect(url_for('.user', username=username))

from ..model_Follow import Follow

@main.route('/following/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first() # user of that accessed page
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
        page, per_page=4, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)

@main.route('/followedby/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.timestamp.desc()).paginate(
        page, per_page=4, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followed_by.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
# Shutdown route will work only when the application is running in testing mode;
# invoking it in other configurations will return a 404 status code response


###### Reporting slow database queries
from flask_sqlalchemy import get_debug_queries
@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKE_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(   ### To be able to store these log entries, the logger must be configured
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                    (query.statement, query.parameters, query.duration,
                     query.context))
    return response













import datetime as dt
@main.route('/about', methods=['GET', 'POST'])
@admin_required
def about():
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    return render_template('about.html', now=now)


import random
import datetime as dt
from ..models import Namstask, Tasktype, Keyword, NamsInsulin, DeadLine
from .forms import TaskForm
@main.route('/namslife', methods=['GET', 'POST'])
@admin_required
def namslife():
## 1632711361.909349
## 2021-09-27 09:56:01.909349 ##
## datetime.datetime(2021, 9, 27, 9, 56, 1, 909349)
    # utcnow = datetime.utcnow()  ## utc international 0 >< local Vietnam +7 ##

    lasttime_checkinsulin = request.cookies.get('lasttime_checkinsulin', '')
    if lasttime_checkinsulin != str(dt.date.today()):
        checkinsulin_process = make_response(redirect(url_for('.namsinsulin_main'))) # HERE HERE
        checkinsulin_process.set_cookie('lasttime_checkinsulin', str(dt.date.today()))
        checkinsulin_process.set_cookie('namslife_checkinginsulin', '1')
        print('REDIRECTING to NAMSINSULIN to Check')
        return checkinsulin_process
    if lasttime_checkinsulin == str(dt.date.today()):
        pass

    alertinsulinnamslife = False
    alertedinsulin = NamsInsulin.query.filter_by(currently_inuse=True).filter_by(alerted=True).first()
    if alertedinsulin is not None:
        alertinsulinnamslife = True
        flash('ALERT: CHECK YOUR INSULIN SOURCES! YOU MIGHT BE HAVING NOT ENOUGH INSULIN SHORTLY, NAM..')

    checkedinsulin = NamsInsulin.query.filter_by(insulin_name='NovoRapid').first()
##########################
    alldeadlines = DeadLine.query.all()
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    for deadline in alldeadlines:
        from ..ext_functions import today
        if str(today()) in str(deadline.deadline_time):
            deadline.todayed = True
        if str(today()) not in str(deadline.deadline_time):
            deadline.todayed = False
        if (now-deadline.deadline_time).total_seconds() < 0:
            deadline.overdrafted = False
        if (now-deadline.deadline_time).total_seconds() > 0:
            deadline.overdrafted = True
        db.session.add(deadline)
        db.session.commit()
    upcomingdeadline = DeadLine.query.filter_by(overdrafted=False).order_by(DeadLine.deadline_time.asc()).first() ####
##################^^^^^^^^##################CHECKING to UPDATE DISPLAY of INSULIN+DEADLINES on NAMSLIFE ^^^^^^^^
## Checking overlapping on main page, not only form.validate_on_submit()

#################### NO NEED THAT CHECK of OVERLAPPING ABOVE anymore :( (deleted)
    checkedtasklist = Namstask.query.filter(Namstask.trashed!=True).all()
    if len(checkedtasklist) > 1:
        for checkedtask2 in checkedtasklist:
            if checkedtask2 is not None:
                remainingtasks2 = [t for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all()\
                                        if t != checkedtask2]
                main_overlappinglist2 = list()
                checkedtask2.overlapping = False
                for it in remainingtasks2:
                    if str(it.runtime).split(' ')[0] == str(checkedtask2.runtime).split(' ')[0]:
                        if it.runtime < checkedtask2.runtime < it.est_endtime or it.runtime < checkedtask2.est_endtime < it.est_endtime:
                            checkedtask2.overlapping = True
                            it.overlapping = True
                            main_overlappinglist2.append(it.taskname)
                        if checkedtask2.runtime < it.runtime and checkedtask2.est_endtime > it.est_endtime:
                            checkedtask2.overlapping = True
                            it.overlapping = True
                            main_overlappinglist2.append(it.taskname)
                    else:
                        it.overlapping = False
                    db.session.add(it)
                    db.session.add(checkedtask2)
                    db.session.commit()

####################################

    tasks = Namstask.query.all()

    today = dt.date.today()
    for t in tasks:
        if str(today) in str(t.runtime):
            t.runtime_todayed = True
        if str(today) not in str(t.runtime):
            t.runtime_todayed = False

    struct_time = time.localtime()
    current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    for t in tasks:
        if (t.runtime-current_time).total_seconds()>0:
            t.alive = True
        elif (t.runtime-current_time).total_seconds()<0:
            t.alive = False
        db.session.add(t)
        db.session.commit()

    nexttask = None
    nexttasks = Namstask.query.filter_by(alive=True).order_by(Namstask.runtime.asc()).all()
    for nt in nexttasks:
        if nt.trashed != True:
            nexttask = nt
            break

    ######## Only if outdated tasks exist => draw <hr> line
    outdatedtasks_exist = False
    y = Namstask.query.filter(Namstask.trashed!=True).all()
    for u in y:
        if u.alive == False:
            outdatedtasks_exist = True
            break

    numberof_alloutdatedtasks = len([t for t in Namstask.query.filter_by(alive=False).order_by(Namstask.runtime.asc()).all()\
                                    if t.trashed!=True])
    numberof_allfinishedtasks = len([t for t in Namstask.query.filter_by(finished=True).order_by(Namstask.runtime.asc()).all()\
                                    if t.trashed!=True])

    numberof_todayedtasks = len([t for t in Namstask.query.filter_by(alive=True).order_by(Namstask.runtime.asc()).all()\
                                if t.finished==False and t.runtime_todayed==True and t.trashed!=True])
    numberof_availabletasks = len([t for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all()])

    form = TaskForm(task=Namstask())
    onetask = Namstask()
    if form.validate_on_submit() and form.submit.data == True:
        try:
            year = int(form.year.data)
            month = int(form.month.data)
            day = int(form.day.data)
            hour = int(form.hour.data)
            minute = int(form.minute.data)
            ##second = int(form.second.data)
            if ':' not in str(form.est_endtime.data):
                endtime_hour = int(form.est_endtime.data)
                endtime_minute = 0
            if ':' in str(form.est_endtime.data):
                endtime_hour = int(str(form.est_endtime.data).split(':')[0])
                endtime_minute = int(str(form.est_endtime.data).split(':')[1])
        except ValueError:
            flash('Error: Unable to create task. Hi Nam, your entered data has not been correctly formated.')
            return redirect(url_for('.namslife'))
        formruntime = datetime(year, month, day, hour, minute, 0, 0)
        formruntime_end = datetime(year, month, day, endtime_hour, endtime_minute, 0, 0)

        onetask.taskname = form.taskname.data
        # Check overlapping
        onetask.runtime = formruntime
        onetask.est_endtime = formruntime_end
        #
        onetask.finished = False
        onetask.info = form.info.data
        onetask.desc = form.desc.data
        onetask.priority = form.priority.data
        onetask.Tasktype = Tasktype.query.get(form.type.data)    ####

        # Checking overlapping
        overlappinglist = list()
        for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all():
            if str(t.runtime).split(' ')[0] == str(formruntime).split(' ')[0]:
                if t.runtime < formruntime < t.est_endtime or t.runtime < formruntime_end < t.est_endtime:
                    onetask.overlapping = True
                    t.overlapping = True
                    overlappinglist.append(t.taskname)
            else:
                t.overlapping = False
                # onetask.overlapping = False Reverted back False after True ????
            db.session.add(t)
            #db.session.add(onetask)
            db.session.commit()
        if len(overlappinglist)>0:
            flash('Attention: Runtime overlapping with '+ str(overlappinglist))
        ####

        struct_time = time.localtime()
        onetask.thisinfo_creationtime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        onetask.thisinfo_lastupdatetime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        db.session.add(onetask)
        db.session.commit()
        flash('Hallo Nam, your task has just been created.')
        ress = make_response(redirect(url_for('.namslife')))
        ress.set_cookie('latest_processedtask', str(onetask.id))
        return ress


    if form.searchsubmit.data == True and form.taskname.data != None:
        structtime = time.localtime()
        timenow = datetime(structtime.tm_year, structtime.tm_mon, structtime.tm_mday, structtime.tm_hour, structtime.tm_min, structtime.tm_sec, 0)
        keyword = form.taskname.data
        kw = Keyword(keyword=keyword, searchtime=timenow)
        db.session.add(kw)
        db.session.commit()
        keyword_id = Keyword.query.filter_by(keyword=keyword).first().id
        return redirect(url_for('main.namstask_searchresults', keyword_id=keyword_id))

    form.priority.data = form.priority.choices[0]
    form.year.data = currentyear()
    form.minute.data = 0
    ##form.second.data = 0

########################
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    todayshow = fullday(str(time.asctime()).split(' ')[0])+', '+str(now.day)+' '+fullmonth(str(time.asctime()).split(' ')[1].split(' ')[0])+' '+str(now.year)
########################

    page = request.args.get('page', -1, type=int)
    pagination = Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).paginate(page, per_page=5, error_out=False)####
    tasks = pagination.items

    return render_template('namlife__.html', tasks = tasks, current_time=current_time, today=today,
                            pagination=pagination, form=form, nexttask=nexttask, outdatedtasks_exist=outdatedtasks_exist,
                            numberof_alloutdatedtasks=numberof_alloutdatedtasks, numberof_allfinishedtasks=numberof_allfinishedtasks,
                            numberof_todayedtasks=numberof_todayedtasks, numberof_availabletasks=numberof_availabletasks,
                            alertinsulinnamslife=alertinsulinnamslife, upcomingdeadline=upcomingdeadline,
                            checkedinsulin=checkedinsulin, todayshow=todayshow)

from .forms import EmailForm
from ..email import mail_todayschedule
@main.route('/namslife/today', methods=['GET', 'POST'])
#@admin_required
async def namslifetoday():
    if current_user.username == "namadmin":
        todaytasks = [t for t in Namstask.query.order_by(Namstask.runtime.asc()).all()\
                                        if t.runtime_todayed==True and t.trashed!=True]
        morningtasks = [t for t in todaytasks if t.runtime.hour<=12]
        afternoontasks = [t for t in todaytasks if 12<t.runtime.hour<18]
        eveningtasks = [t for t in todaytasks if t.runtime.hour>=18]

        mailform = EmailForm()
        if mailform.validate_on_submit():
            response = make_response(redirect(url_for('.namslifetoday')))
            recipient_email = mailform.email.data
            await mail_todayschedule(recipient_email, _template_body={'todaytasks': todaytasks,
                                'morningtasks': morningtasks, 'afternoontasks': afternoontasks, 'eveningtasks': eveningtasks})
            flash('Today schedule has been sent via email.')
            return response
        return render_template("daytasks.html", todaytasks=todaytasks, morningtasks=morningtasks, afternoontasks=afternoontasks, eveningtasks=eveningtasks,
                                        mailform=mailform, current_user=current_user)
    else:
        abort(403)

from ..email import mail_tomorrowschedule
@main.route('/namslife/tomorrow', methods=['GET', 'POST'])
#@admin_required
async def namslifetomorrow():
    if current_user.username == "namadmin":
        tomorrowtasks = [t for t in Namstask.query.order_by(Namstask.runtime.asc()).all()\
                        if t.trashed!=True and t.runtime.timetuple().tm_yday==(time.localtime().tm_yday+1)]
        morningtasks = [t for t in tomorrowtasks if t.runtime.hour<=12]
        afternoontasks = [t for t in tomorrowtasks if 12<t.runtime.hour<18]
        eveningtasks = [t for t in tomorrowtasks if t.runtime.hour>=18]

        tomorrow = True
        mailform = EmailForm()
        if mailform.validate_on_submit():
            response = make_response(redirect(url_for('.namslifetomorrow')))
            recipient_email = mailform.email.data
            await mail_todayschedule(recipient_email, _template_body={'tomorrowtasks': tomorrowtasks,
                                'morningtasks': morningtasks, 'afternoontasks': afternoontasks, 'eveningtasks': eveningtasks, 'tomorrow': tomorrow})
            flash('Tomorrow schedule has been sent via email.')
            return response
        return render_template("daytasks.html", tomorrowtasks=tomorrowtasks, morningtasks=morningtasks, afternoontasks=afternoontasks, eveningtasks=eveningtasks,
                    tomorrow=tomorrow, mailform=mailform)
    else:
        abort(403)

from ..email import mail_thisweekschedule
@main.route('/namslife/thisweek', methods=['GET', 'POST'])
#@admin_required
async def namslifethisweek():
    if current_user.username == "namadmin":
        struct_time = time.localtime()
        now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)

        thisweektasks = [t for t in Namstask.query.order_by(Namstask.runtime.asc()).all()\
                        if t.trashed!=True and t.runtime.isocalendar().week==now.isocalendar().week]
        mon_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==1]
        tue_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==2]
        wed_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==3]
        thur_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==4]
        fri_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==5]
        sat_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==6]
        sun_tasks = [t for t in thisweektasks if t.runtime.isocalendar().weekday==7]

        mailform = EmailForm()
        if mailform.validate_on_submit():
            response = make_response(redirect(url_for('.namslifethisweek')))
            recipient_email = mailform.email.data
            await mail_thisweekschedule(recipient_email, _template_body={'mon_tasks':mon_tasks, 'tue_tasks':tue_tasks, 'wed_tasks':wed_tasks, 'thur_tasks':thur_tasks, 'fri_tasks':fri_tasks, 'sat_tasks':sat_tasks, 'sun_tasks':sun_tasks})
            flash('This week schedule has been sent via email.')
            return response

        return render_template('weektasks.html',
        mon_tasks=mon_tasks, tue_tasks=tue_tasks, wed_tasks=wed_tasks, thur_tasks=thur_tasks, fri_tasks=fri_tasks, sat_tasks=sat_tasks, sun_tasks=sun_tasks,
        mailform=mailform)
    else:
        abort(403)

from ..email import mail_nextweekschedule
@main.route('/namslife/nextweek', methods=['GET', 'POST'])
#@admin_required
async def namslifenextweek():
    if current_user.username == "namadmin":
        struct_time = time.localtime()
        now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)

        nextweektasks = [t for t in Namstask.query.order_by(Namstask.runtime.asc()).all()\
                        if t.trashed!=True and t.runtime.isocalendar().week==(now.isocalendar().week+1)]
        mon_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==1]
        tue_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==2]
        wed_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==3]
        thur_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==4]
        fri_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==5]
        sat_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==6]
        sun_tasks = [t for t in nextweektasks if t.runtime.isocalendar().weekday==7]
        nextweek = True

        mailform = EmailForm()
        if mailform.validate_on_submit():
            response = make_response(redirect(url_for('.namslifenextweek')))
            recipient_email = mailform.email.data
            await mail_nextweekschedule(recipient_email, _template_body={'mon_tasks':mon_tasks, 'tue_tasks':tue_tasks, 'wed_tasks':wed_tasks, 'thur_tasks':thur_tasks, 'fri_tasks':fri_tasks, 'sat_tasks':sat_tasks, 'sun_tasks':sun_tasks, 'nextweek':nextweek})
            flash('Next week schedule has been sent via email.')
            return response

        return render_template('weektasks.html',
        mon_tasks=mon_tasks, tue_tasks=tue_tasks, wed_tasks=wed_tasks, thur_tasks=thur_tasks, fri_tasks=fri_tasks, sat_tasks=sat_tasks, sun_tasks=sun_tasks,
        nextweek=nextweek, mailform=mailform)
    else:
        abort(403)


from .forms import TaskUpdateForm
@main.route('/namsupdatetask/<int:id>', methods=['GET', 'POST'])
@admin_required
def namsupdatetask(id):
    alldeadlines = DeadLine.query.all()
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    for deadline in alldeadlines:
        from ..ext_functions import today
        if str(today()) in str(deadline.deadline_time):
            deadline.todayed = True
        if str(today()) not in str(deadline.deadline_time):
            deadline.todayed = False
        if (now-deadline.deadline_time).total_seconds() < 0:
            deadline.overdrafted = False
        if (now-deadline.deadline_time).total_seconds() > 0:
            deadline.overdrafted = True
        db.session.add(deadline)
        db.session.commit()
    upcomingdeadline = DeadLine.query.filter_by(overdrafted=False).order_by(DeadLine.deadline_time.asc()).first() ####


    today = dt.date.today()

    struct_time = time.localtime()
    current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)

    numberof_alloutdatedtasks = len([t for t in Namstask.query.filter_by(alive=False).order_by(Namstask.runtime.asc()).all()\
                                    if t.trashed!=True])
    numberof_allfinishedtasks = len([t for t in Namstask.query.filter_by(finished=True).order_by(Namstask.runtime.asc()).all()\
                                    if t.trashed!=True])

    numberof_todayedtasks = len([t for t in Namstask.query.filter_by(alive=True).order_by(Namstask.runtime.asc()).all()\
                                if t.finished==False and t.runtime_todayed==True and t.trashed!=True])
    numberof_availabletasks = len([t for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all()])

    updatedtask = Namstask.query.filter_by(id=id).first()
    form = TaskUpdateForm(task=Namstask())

    nexttask = Namstask.query.filter_by(alive=True).order_by(Namstask.runtime.asc()).first()
    ######## Only if outdated tasks exist => draw <hr> line
    outdatedtasks_exist = False
    y = Namstask.query.filter(Namstask.trashed!=True).all()
    for u in y:
        if u.alive == False:
            outdatedtasks_exist = True
            break

    page = request.args.get('page', -1, type=int)
    alltasks = Namstask.query.filter(Namstask.trashed!=True).all()
    numberofpages = latestpage = (len(alltasks) - 1) // 5 + 1
    for p in range(1,latestpage+1):
        pagination = Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).paginate(p, per_page=5, error_out=False)
        if Namstask.query.filter_by(id=updatedtask.id).first() in pagination.items:
            currentpage = p
            print('CURRENT PAGE: '+str(currentpage))

    if form.validate_on_submit() and form.submit.data == True:
        year = int(form.year.data)
        month = int(form.month.data)
        day = int(form.day.data)
        hour = int(form.hour.data)
        minute = int(form.minute.data)
        ##second = int(form.second.data)
        form_runtime = datetime(year, month, day, hour, minute, 0, 0)

        updatedtask.taskname = form.taskname.data
        updatedtask.runtime = form_runtime
        updatedtask.finished = form.Finished.data
        updatedtask.info = form.info.data
        updatedtask.desc = form.desc.data
        updatedtask.result = form.Result.data
        updatedtask.priority = form.priority.data
        updatedtask.Tasktype = Tasktype.query.get(form.type.data)

        ##
        from ..ext_functions import strdatetime_todatetime
        updatedtask.est_endtime = strdatetime_todatetime(form.est_endtime.data)  # Error: '2021-10-20 11:58:00'

        # Checking overlapping HEREHERE
        overlappinglist = list()
        for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all():
            if str(t.runtime).split(' ')[0] == str(updatedtask.runtime).split(' ')[0]:
                if t.runtime < updatedtask.runtime < t.est_endtime or t.runtime < updatedtask.est_endtime < t.est_endtime:
                    updatedtask.overlapping = True
                    t.overlapping = True
                    overlappinglist.append(t.taskname)
            else:
                t.overlapping = False
                #updatedtask.overlapping = False
            db.session.add(t)
            #db.session.add(updatedtask)
            db.session.commit()

        if len(overlappinglist)>0:
            flash('Attention: Runtime overlapping with '+ str(overlappinglist))
        ####

        struct_time = time.localtime()
        updatedtask.thisinfo_lastupdatetime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        if (updatedtask.thisinfo_lastupdatetime-updatedtask.runtime).total_seconds()<0:
            updatedtask.finished = False
        db.session.add(updatedtask)
        db.session.commit()
        updatedtask_id = updatedtask.id ####
        try:
            with open('updatedtask_id', 'w') as f:
                f.write(str(updatedtask_id))
        except FileNotFoundError:
            print('FileNotFoundError - Line 494')
            pass
        flash('Successfully updated.')
        ress = make_response(redirect(url_for('.namslife', page=currentpage)))
        ress.set_cookie('latest_processedtask', str(updatedtask.id))
        return ress

    form.taskname.data = updatedtask.taskname
    form.info.data = updatedtask.info
    form.desc.data = updatedtask.desc
    form.Result.data = updatedtask.result
    form.Finished.data = updatedtask.finished
    form.priority.data = updatedtask.priority
    form.type.data = form.type.coerce(updatedtask.Tasktype.id)

    form.year.data = updatedtask.runtime.year
    form.month.data = updatedtask.runtime.month
    form.day.data = updatedtask.runtime.day
    form.hour.data = updatedtask.runtime.hour
    form.minute.data = updatedtask.runtime.minute
    ##form.second.data = updatedtask.runtime.second
    form.est_endtime.data = updatedtask.est_endtime

    page = request.args.get('page', latestpage+1, type=int)
    pagination = Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).paginate(page, per_page=5, error_out=False)
    tasks = pagination.items

    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    todayshow = fullday(str(time.asctime()).split(' ')[0])+', '+str(now.day)+' '+fullmonth(str(time.asctime()).split(' ')[1].split(' ')[0])+' '+str(now.year)

    return render_template('namlife__.html', tasks = tasks, pagination=pagination, form=form, nexttask=nexttask,
                            current_time=current_time, today=today, outdatedtasks_exist=outdatedtasks_exist,
                            numberof_alloutdatedtasks=numberof_alloutdatedtasks, numberof_allfinishedtasks=numberof_allfinishedtasks,
                            numberof_todayedtasks=numberof_todayedtasks, numberof_availabletasks=numberof_availabletasks,
                            upcomingdeadline=upcomingdeadline, todayshow=todayshow)


@main.route('/namsmarktaskfinished/<int:id>', methods=['GET', 'POST'])
@admin_required
def namsmarktaskfinished(id):
    tasks = Namstask.query.filter(Namstask.trashed!=True).all()    ######
    finishmarkedtask = Namstask.query.filter_by(id=id).first()
    finishmarkedtask.finished = True
    struct_time = time.localtime()
    finishmarkedtask.thisinfo_lastupdatetime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    db.session.add(finishmarkedtask)
    db.session.commit()
    numberofpages = latestpage = (len(tasks) - 1) // 5 + 1
    for p in range(1,latestpage+1):
        pagination = Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).paginate(p, per_page=5, error_out=False)
        if Namstask.query.filter_by(id=finishmarkedtask.id).first() in pagination.items:
            currentpage = p
    return redirect(url_for('.namslife', page=currentpage))


@main.route('/tasksearchresults/<int:keyword_id>', methods=['GET', 'POST'])
@admin_required
def namstask_searchresults(keyword_id):
    alltasks = Namstask.query.all()
    keyword = Keyword.query.filter_by(id=keyword_id).first().keyword
    for t in alltasks:
        if keyword.lower() in t.taskname.lower() or keyword.lower() in t.info.lower():
            t.matching_searchrequest = True
        else:
            t.matching_searchrequest = False

    searchmatchingtasks = Namstask.query.filter_by(matching_searchrequest=True).all()
    numberofresults = len(searchmatchingtasks)
    if numberofresults>1:
        result_or_results = "results"
    elif numberofresults<=1:
        result_or_results = "result"

    page = request.args.get('page', 1, type=int)
    pagination = Namstask.query.filter_by(matching_searchrequest=True).order_by(Namstask.runtime.asc()).paginate(page, per_page=5, error_out=False)
    matchingtasks = pagination.items
    return render_template('searchresults_totasks.html', matchingtasks=matchingtasks, numberofresults=numberofresults,
                            pagination=pagination, keyword_id=keyword_id, result_or_results=result_or_results)


@main.route('/taskfullview/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def taskfullview(task_id):
## Checking overlapping on main page, not only form.validate_on_submit()


#################### NO NEED THAT CHECK of OVERLAPPING ABOVE anymore :(
    checkedtask2 = Namstask.query.filter(Namstask.trashed!=True).first()
    if checkedtask2 is not None:
        remainingtasks2 = [t for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all()\
                                if t != checkedtask2]
        main_overlappinglist2 = list()
        checkedtask2.overlapping = False
        for it in remainingtasks2:
            if str(it.runtime).split(' ')[0] == str(checkedtask2.runtime).split(' ')[0]:
                if it.runtime < checkedtask2.runtime < it.est_endtime or it.runtime < checkedtask2.est_endtime < it.est_endtime:
                    checkedtask2.overlapping = True
                    it.overlapping = True
                    main_overlappinglist2.append(it.taskname)
                if checkedtask2.runtime < it.runtime and checkedtask2.est_endtime > it.est_endtime:
                    checkedtask2.overlapping = True
                    it.overlapping = True
                    main_overlappinglist2.append(it.taskname)
            else:
                it.overlapping = False
            db.session.add(it)
            db.session.add(checkedtask2)
            db.session.commit()

####################################
    task = Namstask.query.filter_by(id=task_id).first()
    return render_template("taskfullview.html", task=task)

@main.route('/taskfullview/delete/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def deletetask(task_id):
    deletedtask = Namstask.query.filter_by(id=task_id).first()
    db.session.delete(deletedtask)
    db.session.commit()
    flash('Task has just been deleted.')
    return redirect(url_for('.namslife'))

@main.route('/tasktrashbin/delete/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def deletetask_intasktrashbin(task_id):
    deletedtask = Namstask.query.filter_by(id=task_id).first()
    db.session.delete(deletedtask)
    db.session.commit()
    flash('Task has just been deleted.')
    return redirect(url_for('main.tasktrashbin'))

from .forms import TaskModifyForm
@main.route('/taskfullview/modify/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def modifytask(task_id):
    modifiedtask = Namstask.query.filter_by(id=task_id).first()
    task_id = modifiedtask.id
    form = TaskModifyForm(task=Namstask())

## Checking overlapping on main page, not only form.validate_on_submit()


####################################

    if form.validate_on_submit() and form.submit.data == True:
        year = int(form.year.data)
        month = int(form.month.data)
        day = int(form.day.data)
        hour = int(form.hour.data)
        minute = int(form.minute.data)
        #second = int(form.second.data)
        form_runtime = datetime(year, month, day, hour, minute, 0, 0)

        modifiedtask.taskname = form.taskname.data
        modifiedtask.runtime = form_runtime
        modifiedtask.finished = form.Finished.data
        modifiedtask.info = form.info.data
        modifiedtask.desc = form.desc.data
        modifiedtask.result = form.Result.data
        modifiedtask.priority = form.priority.data
        modifiedtask.Tasktype = Tasktype.query.get(form.type.data)
        modifiedtask.trashed = form.trashed.data
        ##
        from ..ext_functions import strdatetime_todatetime
        modifiedtask.est_endtime = strdatetime_todatetime(form.est_endtime.data)  # Error: '2021-10-20 11:58:00'
        modifiedtask.thisinfo_creationtime = strdatetime_todatetime(str(form.creationtime.data)) ####

        # Checking overlapping HEREHERE
        overlappinglist = list()
        for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all():
            if str(t.runtime).split(' ')[0] == str(modifiedtask.runtime).split(' ')[0]:
                if t.runtime < modifiedtask.runtime < t.est_endtime or t.runtime < modifiedtask.est_endtime < t.est_endtime:
                    modifiedtask.overlapping = True
                    t.overlapping = True
                    overlappinglist.append(t.taskname)
            else:
                t.overlapping = False
                #modifiedtask.overlapping = False  #Unable to let it reverted after True
            db.session.add(t)
            #db.session.add(modifiedtask)
            db.session.commit()
        if len(overlappinglist)>0:
            flash('Attention: Runtime overlapping with '+ str(overlappinglist))
        ####

        struct_time = time.localtime()
        modifiedtask.thisinfo_lastupdatetime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        db.session.add(modifiedtask)
        db.session.commit()
        flash('Successfully modified.')
        ress = make_response(redirect(url_for('.taskfullview', task_id=modifiedtask.id))) ## HERE HERE
        ress.set_cookie('latest_processedtask', str(modifiedtask.id))
        return ress


    form.taskname.data = modifiedtask.taskname
    form.info.data = modifiedtask.info
    form.desc.data = modifiedtask.desc
    form.Result.data = modifiedtask.result
    form.Finished.data = modifiedtask.finished
    form.priority.data = modifiedtask.priority
    form.type.data = form.type.coerce(modifiedtask.Tasktype.id)
    form.creationtime.data = modifiedtask.thisinfo_creationtime
    form.trashed.data = modifiedtask.trashed

    form.year.data = modifiedtask.runtime.year
    form.month.data = modifiedtask.runtime.month
    form.day.data = modifiedtask.runtime.day
    form.hour.data = modifiedtask.runtime.hour
    form.minute.data = modifiedtask.runtime.minute
    ##form.second.data = modifiedtask.runtime.second
    form.est_endtime.data = modifiedtask.est_endtime

    return render_template('taskfullview_modify.html', task_id=task_id, form=form, task=modifiedtask)

@main.route('/taskfullview/movetotrash/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def trashmovetask(task_id):
    trashtask = Namstask.query.filter_by(id=task_id).first()
    trashtask.trashed = True
    db.session.add(trashtask)
    db.session.commit()
    flash('Task has just been moved to trash.')
    return redirect(url_for('main.namslife'))

@main.route('/namslife/outdatedtasks', methods=['GET', 'POST'])
@admin_required
def outdatedtasks():
    outdatedtasks = [t for t in Namstask.query.filter_by(alive=False).all() if t.trashed!=True]
    numberof_outdatedtasks = len(outdatedtasks)

    page = request.args.get('page', 1, type=int)
    pagination = Namstask.query.filter_by(alive=False).filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).\
                                            paginate(page, per_page=5, error_out=False)
    outdatedtasks = pagination.items
    return render_template("outdatedtasks.html", pagination=pagination, outdatedtasks=outdatedtasks, numberof_outdatedtasks=numberof_outdatedtasks)

@main.route('/namslife/finishedtasks', methods=['GET', 'POST'])
@admin_required
def finishedtasks():
    finishedtasks = [t for t in Namstask.query.filter_by(finished=True).all() if t.trashed!=True]
    numberof_finishedtasks = len(finishedtasks)

    page = request.args.get('page', 1, type=int)
    pagination = Namstask.query.filter_by(finished=True).filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).\
                                            paginate(page, per_page=5, error_out=False)
    finishedtasks = pagination.items
    return render_template("finishedtasks.html", pagination=pagination, finishedtasks=finishedtasks, numberof_finishedtasks=numberof_finishedtasks)

@main.route('/namslife/markalloutdatedasfinished', methods=['GET', 'POST'])
@admin_required
def markalloutdated_asfinished():
    markedtasks = Namstask.query.filter_by(alive=False).all()
    for t in markedtasks:
        t.finished = True
        db.session.add(t)
        db.session.commit()
    flash('All of your outdated tasks have been marked as finished. Finished tasks are unborderedly exhibited, FYI fella.')
    return redirect(url_for('.namslife'))

@main.route('/tasktrashbin', methods=['GET', 'POST'])
@admin_required
def tasktrashbin():
    trashedtasks = Namstask.query.filter_by(trashed=True).all()
    numberofpieces = len(trashedtasks)

    page = request.args.get('page', 1, type=int)
    pagination = Namstask.query.filter_by(trashed=True).order_by(Namstask.runtime.asc()).\
                                            paginate(page, per_page=5, error_out=False)
    trashedtasks = pagination.items
    if numberofpieces>1:
        piece_or_pieces = "pieces"
    elif numberofpieces<=1:
        piece_or_pieces = "piece"
    return render_template("trashbin.html", trashedtasks=trashedtasks, numberofpieces=numberofpieces,
                            pagination=pagination, piece_or_pieces=piece_or_pieces)

@main.route('/tasktrashbin/recover/<int:recover_taskid>', methods=['GET', 'POST'])
@admin_required
def taskrecovery(recover_taskid):
    recoveredtask = Namstask.query.filter_by(id=recover_taskid).first()
    recoveredtask.trashed = False
    db.session.add(recoveredtask)
    db.session.commit()
    flash('Successfully recovered.')
    return redirect(url_for('main.tasktrashbin'))    ##############

@main.route('/namslife/cleanoutdatedtasks', methods=['GET', 'POST'])
@admin_required
def cleanoutdatedtasks():
    outdatedtasks = Namstask.query.filter_by(alive=False).all()
    for t in outdatedtasks:
        t.trashed = True
        db.session.add(t)
        db.session.commit()
    flash('Successfully cleaned outdated tasks.')
    return redirect(url_for('main.namslife'))

@main.route('/namslife/cleanoutfinishedtasks', methods=['GET', 'POST'])
@admin_required
def cleanoutfinishedtasks():
    finishedtasks = Namstask.query.filter_by(finished=True).all()
    for t in finishedtasks:
        t.trashed = True
        db.session.add(t)
        db.session.commit()
    flash('Successfully cleaned marked-as-finished tasks.')
    return redirect(url_for('main.namslife'))

@main.route('/tasktrashbin/emptyall', methods=['GET', 'POST'])
@admin_required
def emptyalltrashbin():
    deletedtasks = Namstask.query.filter_by(trashed=True).all()
    for t in deletedtasks:
        db.session.delete(t)
        db.session.commit()
    flash('Hi Nam, everything in your trash bin has just been emptied. Keep up your excellent career and relationships. Cheers!')
    return redirect(url_for('main.tasktrashbin'))





@main.route('/namslifeupdated', methods=['GET', 'POST'])
@admin_required
def namslifeupdated():
## 1632711361.909349
## 2021-09-27 09:56:01.909349 ##
## datetime.datetime(2021, 9, 27, 9, 56, 1, 909349)
    # utcnow = datetime.utcnow()  ## utc international 0 >< local Vietnam +7 ##
    lasttime_checkinsulin = request.cookies.get('lasttime_checkinsulin', '')
    if lasttime_checkinsulin != str(dt.date.today()):
        checkinsulin_process = make_response(redirect(url_for('.namsinsulin_main'))) # HERE HERE
        checkinsulin_process.set_cookie('lasttime_checkinsulin', str(dt.date.today()))
        checkinsulin_process.set_cookie('namslife_checkinginsulin', '1')
        print('REDIRECTING to NAMSINSULIN to Check')
        return checkinsulin_process
    if lasttime_checkinsulin == str(dt.date.today()):
        pass

    alertinsulinnamslife = False
    alertedinsulin = NamsInsulin.query.filter_by(currently_inuse=True).filter_by(alerted=True).first()
    if alertedinsulin is not None:
        alertinsulinnamslife = True
        flash('ALERT: CHECK YOUR INSULIN SOURCES! YOU MIGHT BE HAVING NOT ENOUGH INSULIN SHORTLY, NAM..')

    checkedinsulin = NamsInsulin.query.filter_by(insulin_name='NovoRapid').first()
##########################
    alldeadlines = DeadLine.query.all()
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    for deadline in alldeadlines:
        from ..ext_functions import today
        if str(today()) in str(deadline.deadline_time):
            deadline.todayed = True
        if str(today()) not in str(deadline.deadline_time):
            deadline.todayed = False
        if (now-deadline.deadline_time).total_seconds() < 0:
            deadline.overdrafted = False
        if (now-deadline.deadline_time).total_seconds() > 0:
            deadline.overdrafted = True
        db.session.add(deadline)
        db.session.commit()
    upcomingdeadline = DeadLine.query.filter_by(overdrafted=False).order_by(DeadLine.deadline_time.asc()).first() ####
##################^^^^^^^^##################CHECKING to UPDATE DISPLAY of INSULIN+DEADLINES on NAMSLIFE ^^^^^^^^
## Checking overlapping on main page, not only form.validate_on_submit()

#################### NO NEED THAT CHECK of OVERLAPPING ABOVE anymore :( (deleted)
    checkedtask2 = Namstask.query.filter(Namstask.trashed!=True).first()
    if checkedtask2 is not None:
        remainingtasks2 = [t for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all()\
                                if t != checkedtask2]
        main_overlappinglist2 = list()
        checkedtask2.overlapping = False
        for it in remainingtasks2:
            if str(it.runtime).split(' ')[0] == str(checkedtask2.runtime).split(' ')[0]:
                if it.runtime < checkedtask2.runtime < it.est_endtime or it.runtime < checkedtask2.est_endtime < it.est_endtime:
                    checkedtask2.overlapping = True
                    it.overlapping = True
                    main_overlappinglist2.append(it.taskname)
                if checkedtask2.runtime < it.runtime and checkedtask2.est_endtime > it.est_endtime:
                    checkedtask2.overlapping = True
                    it.overlapping = True
                    main_overlappinglist2.append(it.taskname)
            else:
                it.overlapping = False
            db.session.add(it)
            db.session.add(checkedtask2)
            db.session.commit()

####################################
####################################
    updatedprocess = True
    with open('updatedtask_id', 'r') as f:
        updatedtask_id = f.read()
    tasks = Namstask.query.all()

    today = dt.date.today()
    for t in tasks:
        if str(today) in str(t.runtime):
            t.runtime_todayed = True
        if str(today) not in str(t.runtime):
            t.runtime_todayed = False

    struct_time = time.localtime()
    current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    for t in tasks:
        if (t.runtime-current_time).total_seconds()>0:
            t.alive = True
        elif (t.runtime-current_time).total_seconds()<0:
            t.alive = False
        db.session.add(t)
        db.session.commit()
    nexttasks = Namstask.query.filter_by(alive=True).order_by(Namstask.runtime.asc()).all()
    for nt in nexttasks:
        if nt.trashed != True:
            nexttask = nt
            break

    ######## Only if outdated tasks exist => draw <hr> line
    outdatedtasks_exist = False
    y = Namstask.query.filter(Namstask.trashed!=True).all()
    for u in y:
        if u.alive == False:
            outdatedtasks_exist = True
            break

    numberof_alloutdatedtasks = len([t for t in Namstask.query.filter_by(alive=False).order_by(Namstask.runtime.asc()).all()\
                                    if t.trashed!=True])
    numberof_allfinishedtasks = len([t for t in Namstask.query.filter_by(finished=True).order_by(Namstask.runtime.asc()).all()\
                                    if t.trashed!=True])

    numberof_todayedtasks = len([t for t in Namstask.query.filter_by(alive=True).order_by(Namstask.runtime.asc()).all()\
                                if t.finished==False and t.runtime_todayed==True and t.trashed!=True])
    numberof_availabletasks = len([t for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all()])

    form = TaskForm(task=Namstask())
    onetask = Namstask()
    if form.validate_on_submit() and form.submit.data == True:
        try:
            year = int(form.year.data)
            month = int(form.month.data)
            day = int(form.day.data)
            hour = int(form.hour.data)
            minute = int(form.minute.data)

            if ':' not in str(form.est_endtime.data):
                endtime_hour = int(form.est_endtime.data)
                endtime_minute = 0
            if ':' in str(form.est_endtime.data):
                endtime_hour = int(str(form.est_endtime.data).split(':')[0])
                endtime_minute = int(str(form.est_endtime.data).split(':')[1])
        except ValueError:
            flash('Error: Unable to create task. Hi Nam, your entered data has not been correctly formated.')
            return redirect(url_for('.namslife'))
        formruntime = datetime(year, month, day, hour, minute, 0, 0)
        formruntime_end = datetime(year, month, day, endtime_hour, endtime_minute, 0, 0)

        onetask.est_endtime = formruntime_end
        onetask.taskname = form.taskname.data
        onetask.runtime = formruntime
        onetask.finished = False
        onetask.info = form.info.data
        onetask.desc = form.desc.data
        onetask.priority = form.priority.data
        onetask.Tasktype = Tasktype.query.get(form.type.data)    ####

        # Checking overlapping
        overlappinglist = list()
        for t in Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).all():
            if str(t.runtime).split(' ')[0] == str(formruntime).split(' ')[0]:
                if t.runtime < formruntime < t.est_endtime or t.runtime < formruntime_end < t.est_endtime:
                    onetask.overlapping = True
                    t.overlapping = True
                    overlappinglist.append(t.taskname)
            else:
                t.overlapping = False
                #onetask.overlapping = False
            db.session.add(t)
            #db.session.add(onetask)
            db.session.commit()
        if len(overlappinglist)>0:
            flash('Attention: Runtime overlapping with '+ str(overlappinglist))
        ####

        struct_time = time.localtime()
        onetask.thisinfo_creationtime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        onetask.thisinfo_lastupdatetime = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        db.session.add(onetask)
        db.session.commit()
        flash('Hallo Nam, your task has just been created.')
        ress = make_response(redirect(url_for('.namslife')))
        ress.set_cookie('latest_processedtask', str(onetask.id))
        return ress


    if form.searchsubmit.data == True and form.taskname.data != None:
        structtime = time.localtime()
        timenow = datetime(structtime.tm_year, structtime.tm_mon, structtime.tm_mday, structtime.tm_hour, structtime.tm_min, structtime.tm_sec, 0)
        keyword = form.taskname.data
        kw = Keyword(keyword=keyword, searchtime=timenow)
        db.session.add(kw)
        db.session.commit()
        keyword_id = Keyword.query.filter_by(keyword=keyword).first().id
        return redirect(url_for('main.namstask_searchresults', keyword_id=keyword_id))

    form.priority.data = form.priority.choices[0]
    form.year.data = currentyear()
    form.minute.data = 0

    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    todayshow = fullday(str(time.asctime()).split(' ')[0])+', '+str(now.day)+' '+fullmonth(str(time.asctime()).split(' ')[1].split(' ')[0])+' '+str(now.year)

    page = request.args.get('page', -1, type=int)
    pagination = Namstask.query.filter(Namstask.trashed!=True).order_by(Namstask.runtime.asc()).paginate(page, per_page=5, error_out=False)####
    tasks = pagination.items

    return render_template('namlife__updated.html', tasks = tasks, current_time=current_time, today=today,
                            pagination=pagination, form=form, nexttask=nexttask, outdatedtasks_exist=outdatedtasks_exist,
                            numberof_alloutdatedtasks=numberof_alloutdatedtasks, numberof_allfinishedtasks=numberof_allfinishedtasks,
                            numberof_todayedtasks=numberof_todayedtasks, numberof_availabletasks=numberof_availabletasks,
                            updatedprocess=updatedprocess, updatedtask_id=updatedtask_id, alertinsulinnamslife=alertinsulinnamslife,
                            upcomingdeadline=upcomingdeadline, todayshow=todayshow)





from .forms import CreateInsulinTypeForm, InsulinSettingForm
from ..models import Insulin, NamsInsulin
@main.route('/namsinsulin', methods=["GET", "POST"])
@admin_required
def namsinsulin_main():
    newinsulinadded = False
    newinsulin_id = None
    newinsulinadded = bool(request.cookies.get('newinsulinadded', ''))
    newinsulin_id = request.cookies.get('newinsulinadded_id', '')

    allinsulins = NamsInsulin.query.filter_by(currently_inuse=True).all()
    numberofinsulins = len(allinsulins)
    if len(allinsulins) == 1:
        namesofnamsinsulins = allinsulins[0].insulin_name
    elif len(allinsulins) == 0:
        namesofnamsinsulins = ''
    elif len(allinsulins) > 1:
        namesofnamsinsulins = allinsulins[0].insulin_name
        for namsi in allinsulins[1:]:
            namesofnamsinsulins = namesofnamsinsulins + ', ' + namsi.insulin_name

    struct_time = time.localtime()
    current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    # HERE HERE
    for insulin in allinsulins:
        if insulin.current_amount is not None and insulin.lasttimepoint_updatebalance is not None:
            print('INSULIN '+str(insulin.insulin_name))
            print('INSULIN.CURRENT_AMOUNT = '+str(insulin.current_amount))
            timepassed = (current_time - insulin.lasttimepoint_updatebalance).total_seconds() #
            timepassed2 = (current_time - insulin.startusing_since).total_seconds() ##
            timepassed_bydays = timepassed // (60*60*24)
            timepassed_bydays2 = timepassed2 // (60*60*24)
            print('TIME SECONDS PASSED: '+str(timepassed2))
            print('TIME DAYS PASSED: '+str(timepassed_bydays2))
            consumedquantity = timepassed_bydays*insulin.avgamount_perday
            print('CONSUMED QUANTITY: '+str(consumedquantity))
            new_currentamount = insulin.current_amount - int(consumedquantity)
            print('NEW CURRENT BALANCE: '+str(new_currentamount))
            if new_currentamount < int(insulin.current_amount):
                insulin.current_amount = new_currentamount
                insulin.numberofdays_enoughinsulin = insulin.current_amount // insulin.avgamount_perday
                insulin.lasttimepoint_updatebalance = current_time
                db.session.add(insulin)
                db.session.commit()
    for insulin in allinsulins:
        if insulin.lasttimepoint_updatebalance is not None and insulin.avgamount_perday != 0:
            insulin.numberofdays_enoughinsulin = insulin.current_amount // insulin.avgamount_perday
            db.session.add(insulin)
            db.session.commit()
###############################
    formsetting = InsulinSettingForm()
    if formsetting.submit.data == True:
        rsp = make_response(redirect(url_for('.namsinsulin_main')))
        if formsetting.option.data == 'Below 7 Days alert':
            rsp.set_cookie('currentsetting', 'Current setting: Below 7 Days alert')
        if formsetting.option.data == '2 Weeks alert':
            rsp.set_cookie('currentsetting', 'Current setting: 2 Weeks alert')
        if formsetting.option.data == '1 Month alert':
            rsp.set_cookie('currentsetting', 'Current setting: 1 Month alert')
        if formsetting.option.data == 'None':
            rsp.set_cookie('currentsetting', 'Current setting: None')
        flash('Setting applied. Current setting: '+str(formsetting.option.data))
        return rsp

    currentsettingopt = request.cookies.get('currentsetting', '')
    if currentsettingopt == '':
        currentsettingopt = 'Current setting: None'
    print('currentsettingopt = '+str(currentsettingopt))
    if currentsettingopt == 'Current setting: None':
        for insulin in allinsulins:
            insulin.alerted = False
            db.session.add(insulin)
            db.session.commit()
    if currentsettingopt == 'Current setting: Below 7 Days alert':
        for insulin in allinsulins:
            try:
                if 0 < insulin.numberofdays_enoughinsulin <= 7 and insulin.numberofdays_enoughinsulin is not None:
                    insulin.alerted = True
                else:
                    insulin.alerted = False
                db.session.add(insulin)
                db.session.commit()
            except:
                pass
    if currentsettingopt == 'Current setting: 2 Weeks alert':
        for insulin in allinsulins:
            try:
                if 0 < insulin.numberofdays_enoughinsulin <= 14 and insulin.numberofdays_enoughinsulin is not None:
                    insulin.alerted = True
                else:
                    insulin.alerted = False
                db.session.add(insulin)
                db.session.commit()
            except:
                pass
    if currentsettingopt == 'Current setting: 1 Month alert':
        for insulin in allinsulins:
            try:
                if 0 < insulin.numberofdays_enoughinsulin <= 28 and insulin.numberofdays_enoughinsulin is not None:
                    insulin.alerted = True
                else:
                    insulin.alerted = False
                db.session.add(insulin)
                db.session.commit()
            except:
                pass
    alertnotification = False ####
    for insulin in allinsulins:
        if insulin.alerted == True:
            alertnotification = True
            break

    wtc = request.cookies.get('currentsetting', '')
    if wtc == 'Current setting: None':
        formsetting.option.data = 'None'
    if wtc == 'Current setting: Below 7 Days alert':
        formsetting.option.data = 'Below 7 Days alert'
    if wtc == 'Current setting: 2 Weeks alert':
        formsetting.option.data = '2 Weeks alert'
    if wtc == 'Current setting: 1 Month alert':
        formsetting.option.data = '1 Month alert'
################################################################
    modify_currentamount = False
    add_pumpchanges = False
    update_info = False

    modify_currentamount = bool(request.cookies.get('modify_currentamount', ''))
    add_pumpchanges = bool(request.cookies.get('add_pumpchanges', ''))
    update_info = bool(request.cookies.get('update_info', ''))


    from .forms import addpumpchanges_form
    if add_pumpchanges==True and modify_currentamount==False and update_info==False:
        form = addpumpchanges_form(NamsInsulin()) ###
        if form.submit4.data == True and form.validate_on_submit():
            struct_time = time.localtime()
            currently_when = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)

            thatinsulin = NamsInsulin.query.get(form.type.data)

            if form.onthescale.data == 'One day':
                surplus = int(form.changedquantity.data) - int(thatinsulin.avgamount_perday)
            if form.onthescale.data == 'One injection time':
                surplus = int(form.changedquantity.data) - int(thatinsulin.avgamount_pertime)
            thatinsulin.lasttime_pumpchange_info = form.info.data
            thatinsulin.lasttime_pumpchange_timestamp = currently_when

            thatinsulin.current_amount = int(thatinsulin.current_amount) - int(surplus) ####
            db.session.add(thatinsulin)
            db.session.commit()
            resp = make_response(redirect(url_for('.namsinsulin_main')))
            flash('One variation in the Insulin level injected has been added. Your total balance of Insulin quantity might have been changed also..')
            return resp

    from .forms import modifycurrentamount_form
    if modify_currentamount==True and add_pumpchanges==False and update_info==False:
        form = modifycurrentamount_form(NamsInsulin()) ######
        refresh_working = True
        update_working = False
        refresh_working = bool(request.cookies.get('refresh_working', ''))
        update_working = bool(request.cookies.get('update_working', ''))

        if form.submit3r.data == True:
            resp = make_response(redirect(url_for('.namsinsulin_main'))) ###### AFTER REFRESH, redirect to id #namsinsulinform???? New function Try
            resp.set_cookie('which_insulinname', NamsInsulin.query.get(form.type.data).insulin_name, max_age=300)
            resp.set_cookie('modify_currentamount', '1', max_age=300)
            resp.set_cookie('add_pumpchanges', '', max_age=300)
            resp.set_cookie('update_info', '', max_age=300)
            thatinsulin = NamsInsulin.query.get(form.type.data)
            resp.set_cookie('avgamount_perday', str(thatinsulin.avgamount_perday), max_age=3)
            resp.set_cookie('avgamount_pertime', str(thatinsulin.avgamount_pertime), max_age=3)
            resp.set_cookie('current_amount', str(thatinsulin.current_amount), max_age=3)
            resp.set_cookie('currently_inuse', str(thatinsulin.currently_inuse), max_age=3)
            resp.set_cookie('thatid', str(thatinsulin.id), max_age=3)
            resp.set_cookie('refresh_working', '1', max_age=20)
            resp.set_cookie('update_working', '', max_age=20)
            return resp

        if refresh_working == False and update_working == True:
            thatinsulin = NamsInsulin.query.filter_by(insulin_name=request.cookies.get('which_insulinname', '')).first()
            try:
                form.type.data = form.type.coerce(request.cookies.get('thatid', ''))
            except:
                pass
            thatinsulin.avgamount_perday = request.cookies.get('avgamount_perday', '')
            thatinsulin.avgamount_pertime = request.cookies.get('avgamount_pertime', '')
            thatinsulin.current_amount = request.cookies.get('current_amount', '')
            print('RESULT HERE : '+request.cookies.get('currently_inuse', ''))
            if request.cookies.get('currently_inuse', '') == 'True':
                thatinsulin.currently_inuse = True
            elif request.cookies.get('currently_inuse', '') != 'True':
                thatinsulin.currently_inuse = False
            db.session.add(thatinsulin)
            db.session.commit()
            resp = make_response(redirect(url_for('.namsinsulin_main')))
            resp.set_cookie('refresh_working', '', max_age=20)
            resp.set_cookie('update_working', '', max_age=20)
            return resp

        if form.submit3.data == True and form.validate_on_submit():
            thatinsulin = NamsInsulin.query.get(form.type.data)

            resp = make_response(redirect(url_for('.namsinsulin_main')))

            resp.set_cookie('avgamount_perday', str(form.avgamount_perday.data), max_age=3)
            resp.set_cookie('avgamount_pertime', str(form.avgamount_pertime.data), max_age=3)
            resp.set_cookie('current_amount', str(form.current_amount.data), max_age=3)
            resp.set_cookie('currently_inuse', str(form.currently_inuse.data), max_age=3)

            resp.set_cookie('which_insulinname', NamsInsulin.query.get(form.type.data).insulin_name, max_age=300)
            resp.set_cookie('thatid', str(thatinsulin.id), max_age=3)
            resp.set_cookie('modify_currentamount', '1', max_age=300)
            resp.set_cookie('add_pumpchanges', '', max_age=300)
            resp.set_cookie('update_info', '', max_age=300)

            resp.set_cookie('refresh_working', '', max_age=20)
            resp.set_cookie('update_working', '1', max_age=20)

            flash('Successfully change(s) applied on Insulin ['+str(thatinsulin.insulin_name)+"]. Bitte schön, Nam!")
            return resp

        if request.cookies.get('currently_inuse') == 'True':
            form.currently_inuse.data = True
        elif request.cookies.get('currently_inuse') == 'False' or request.cookies.get('currently_inuse') == 'None':
            form.currently_inuse.data = False

        if refresh_working == True and update_working == False:
            form.avgamount_perday.data = request.cookies.get('avgamount_perday', '')
            form.avgamount_pertime.data = request.cookies.get('avgamount_pertime', '')
            form.current_amount.data = request.cookies.get('current_amount' '')
            try:
                form.type.data = form.type.coerce(request.cookies.get('thatid', ''))
            except:
                pass

###############################
    from .forms import updateinfo_form
    if modify_currentamount==False and add_pumpchanges==False and update_info==True:
        form = updateinfo_form(NamsInsulin()) ###
        if form.submit2.data == True and form.validate_on_submit():
            thatinsulin = NamsInsulin.query.get(form.type.data) # Formerly: NamsInsulin.query.filter_by(insulin_name=NamsInsulin.query.get(form.type.data))
            thatinsulin.info = form.info.data
            db.session.add(thatinsulin)
            db.session.commit()
            flash('Latest information updated. You are so trendy and informed!')
            return redirect(url_for('.namsinsulin_main'))
###############################
    from .forms import addnewpurchase_form
    if modify_currentamount==False and add_pumpchanges==False and update_info==False:
        form = addnewpurchase_form(NamsInsulin()) ###
        if form.submit1m.data == True and form.validate_on_submit():
            ####### Manually add up
            thatinsulin = NamsInsulin.query.get(form.type.data)
            try:
                if thatinsulin.current_amount != None:
                    thatinsulin.current_amount = int(thatinsulin.current_amount) + int(form.added.data) - int(form.deducted.data)
                elif thatinsulin.current_amount == None:
                    thatinsulin.current_amount = int(form.added.data) - int(form.deducted.data)
            except ValueError:
                thatinsulin.current_amount = int(form.added.data) - int(form.deducted.data)
            db.session.add(thatinsulin)
            db.session.commit()
            flash('Adjustment process completed. You might want to check out your current balance of Insulin quantity to recognize that change on Insulin ['+str(thatinsulin.insulin_name)+']. Herzliche Grüße!')
            return redirect(url_for('.namsinsulin_main'))
        form.added.data = 0
        form.deducted.data = 0

        if form.submit1.data == True and form.validate_on_submit():
            thatinsulin = NamsInsulin.query.get(form.type.data)
            per_storingunit_object = Insulin.query.filter_by(full_name=thatinsulin.insulin_name).filter_by(storing_unit=form.storing_unit.data).first()
            if per_storingunit_object is None:
                flash("Error: Unavailable data for storing unit "+"["+str(form.storing_unit.data)+"]. "+"Currently, Insulin ["+str(thatinsulin.insulin_name)+"] storage avails only in "+str(Insulin.query.filter_by(full_name=thatinsulin.insulin_name).first().storing_unit))
                return redirect(url_for('.namsinsulin_main'))
            per_storingunit = Insulin.query.filter_by(full_name=thatinsulin.insulin_name).filter_by(storing_unit=form.storing_unit.data).first().amount_perstoringunit
            struct_time = time.localtime()
            current_timestamp = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)

            thatinsulin.last_purchasetime = current_timestamp
            thatinsulin.lastpurchasetime_info = form.purchase_info.data
            if thatinsulin.current_amount != None:
                thatinsulin.current_amount = int(thatinsulin.current_amount) + int(form.quantity.data)*int(per_storingunit)
            elif thatinsulin.current_amount == None:
                thatinsulin.current_amount = int(form.quantity.data)*int(per_storingunit)
            db.session.add(thatinsulin)
            if thatinsulin.Insulin.storing_unit==None:
                db.session.rollback()
                flash("Error: Unavailable data for storing unit "+"["+str(form.storing_unit.data)+"]. "+"Currently, Insulin ["+str(thatinsulin.insulin_name)+"] storage avails only in "+str(Insulin.query.filter_by(full_name=thatinsulin.insulin_name).first().storing_unit))
                return redirect(url_for('.namsinsulin_main'))
            db.session.commit()
            flash('Insulin source(s) has(have) just been replenished. Keep up your vigorous well-being!')
            return redirect(url_for('.namsinsulin_main'))
###############################

    if bool(request.cookies.get('namslife_checkinginsulin','')) == True:
        repl = make_response(redirect(url_for('.namslife')))
        repl.set_cookie('namslife_checkinginsulin', '')
        print('CHECKING INSULIN Day '+str(dt.date.today())+' DONE. Now back to Namslife..')
        return repl
    return render_template("namsinsulin_main.html", numberofinsulins=numberofinsulins,
                            newinsulinadded=newinsulinadded, newinsulin_id=newinsulin_id,
                            form=form, allinsulins=allinsulins,
                            modify_currentamount=modify_currentamount, add_pumpchanges=add_pumpchanges, update_info=update_info,
                            namesofnamsinsulins=namesofnamsinsulins,
                            formsetting=formsetting, currentsettingopt=currentsettingopt, alertnotification=alertnotification)
####FORM####  add new purchase // update info about doctor, predescription, personal dosage // add pump changes // modify current average pump rates, current amount, still in use or not
######## more about Insulin types (add new types // edit current types // delete some type)
#### REMEMBER to test when 0 Insulin types in database
from flask import make_response
@main.route('/namsinsulin/addnewpurchase')
@login_required
def add_newpurchase():
    resp = make_response(redirect(url_for('.namsinsulin_main')))
    resp.set_cookie('modify_currentamount', '', max_age=30*24*60*60)
    resp.set_cookie('add_pumpchanges', '', max_age=30*24*60*60)
    resp.set_cookie('update_info', '', max_age=30*24*60*60)
    return resp
@main.route('/namsinsulin/modifycurrentamount')
@login_required
def modify_currentamount():
    resp = make_response(redirect(url_for('.namsinsulin_main')))
    resp.set_cookie('modify_currentamount', '1', max_age=30*24*60*60)
    resp.set_cookie('add_pumpchanges', '', max_age=30*24*60*60)
    resp.set_cookie('update_info', '', max_age=30*24*60*60)
    return resp
@main.route('/namsinsulin/addpumpchanges')
@login_required
def add_pumpchanges():
    resp = make_response(redirect(url_for('.namsinsulin_main')))
    resp.set_cookie('add_pumpchanges', '1', max_age=30*24*60*60)
    resp.set_cookie('modify_currentamount', '', max_age=30*24*60*60)
    resp.set_cookie('update_info', '', max_age=30*24*60*60)
    return resp
@main.route('/namsinsulin/updateinfo')
@login_required
def update_info():
    resp = make_response(redirect(url_for('.namsinsulin_main')))
    resp.set_cookie('add_pumpchanges', '', max_age=30*24*60*60)
    resp.set_cookie('modify_currentamount', '', max_age=30*24*60*60)
    resp.set_cookie('update_info', '1', max_age=30*24*60*60)
    return resp


@main.route('/namsinsulin/activate/<int:insulin_id>', methods=["GET", "POST"])
@admin_required
def activatenamsinsulin(insulin_id):
    insulin_id = request.cookies.get('newinsulinadded_id', '')
    thatname = request.cookies.get('newinsulinadded_name', '')

    activatedinsulin = NamsInsulin.query.filter_by(insulin_name=thatname).first()
    if activatedinsulin is not None:
        activatedinsulin.currently_inuse = True
        struct_time = time.localtime()
        current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        activatedinsulin.startusing_since = current_time ####
        activatedinsulin.lasttimepoint_updatebalance = current_time
        db.session.add(activatedinsulin)
        db.session.commit()
        flash('Insulin ['+str(activatedinsulin.insulin_name)+'] has been put in use. Stay healthy!')
    if activatedinsulin is None:
        newinsulin_toNam = NamsInsulin()
        newinsulin_toNam.insulin_name = thatname
        newinsulin_toNam.type_id = Insulin.query.filter_by(full_name=thatname).first().id ######
        newinsulin_toNam.avgamount_perday = 0
        newinsulin_toNam.avgamount_pertime = 0
        newinsulin_toNam.current_amount = 0
        newinsulin_toNam.currently_inuse = True
        struct_time = time.localtime()
        current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        newinsulin_toNam.startusing_since = current_time
        newinsulin_toNam.lasttimepoint_updatebalance = current_time
        db.session.add(newinsulin_toNam)
        db.session.commit()
        flash('Insulin ['+str(thatname)+'] has been put in use. Stay healthy!')
    return redirect(url_for('.namsinsulin_main'))

@main.route('/namsinsulin/dbactivate/<int:insulin_id>', methods=["GET", "POST"])
@admin_required
def activatenamsinsulindb(insulin_id):
    thatname = Insulin.query.filter_by(id=insulin_id).first().full_name
    activatedinsulin = NamsInsulin.query.filter_by(insulin_name=thatname).first()
    if activatedinsulin is not None:
        activatedinsulin.currently_inuse = True
        struct_time = time.localtime()
        current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        activatedinsulin.startusing_since = current_time ####
        activatedinsulin.lasttimepoint_updatebalance = current_time
        db.session.add(activatedinsulin)
        db.session.commit()
        flash('Insulin ['+str(activatedinsulin.insulin_name)+'] has been put in use. Stay healthy!')
    if activatedinsulin is None:
        newinsulin_toNam = NamsInsulin()
        newinsulin_toNam.insulin_name = thatname
        newinsulin_toNam.type_id = Insulin.query.filter_by(full_name=thatname).first().id ######
        newinsulin_toNam.avgamount_perday = 0
        newinsulin_toNam.avgamount_pertime = 0
        newinsulin_toNam.current_amount = 0
        newinsulin_toNam.currently_inuse = True
        struct_time = time.localtime()
        current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        newinsulin_toNam.startusing_since = current_time
        newinsulin_toNam.lasttimepoint_updatebalance = current_time
        db.session.add(newinsulin_toNam)
        db.session.commit()
        flash('Insulin ['+str(thatname)+'] has been put in use. Stay healthy!')
    return redirect(url_for('.namsinsulin_main'))



@main.route('/namsinsulin/deactivate/<int:insulin_id>', methods=["GET", "POST"])
@admin_required
def deactivatenamsinsulin(insulin_id):
    insulin_id = request.cookies.get('newinsulinadded_id', '')
    thatname = request.cookies.get('newinsulinadded_name', '')

    deactivatedinsulin = NamsInsulin.query.filter_by(insulin_name=thatname).first()

    if deactivatedinsulin is not None:
        deactivatedinsulin.currently_inuse = False
        struct_time = time.localtime()
        current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        deactivatedinsulin.stopusing_since = current_time ####
        db.session.add(deactivatedinsulin)
        db.session.commit()
        flash('Insulin ['+str(deactivatedinsulin.insulin_name)+'] has been put out of use. Viele Grüße!')
    if deactivatedinsulin is None:
        flash('ERROR: Views.py/function deactivatenamsinsulin(insulin_id)')
    return redirect(url_for('.namsinsulin_main'))

@main.route('/namsinsulin/dbdeactivate/<int:insulin_id>', methods=["GET", "POST"])
@admin_required
def deactivatenamsinsulindb(insulin_id):
    thatname = Insulin.query.filter_by(id=insulin_id).first().full_name
    deactivatedinsulin = NamsInsulin.query.filter_by(insulin_name=thatname).first()

    if deactivatedinsulin is not None:
        deactivatedinsulin.currently_inuse = False
        struct_time = time.localtime()
        current_time = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
        deactivatedinsulin.stopusing_since = current_time ####
        db.session.add(deactivatedinsulin)
        db.session.commit()
        flash('Insulin ['+str(deactivatedinsulin.insulin_name)+'] has been put out of use. Viele Grüße!')
    if deactivatedinsulin is None:
        flash('ERROR: Views.py/function deactivatenamsinsulin(insulin_id)')
    return redirect(url_for('.namsinsulin_main'))

@main.route('/namsinsulin/addnewtype', methods=["GET", "POST"])
@admin_required
def namsinsulin_addnewtype():
    insulin_removepersonaluse_besidesdatabase = bool(request.cookies.get('insulin_removepersonaluse_besidesdatabase', ''))
    insulinid_removeusealso = request.cookies.get('insulinid_removeusealso', '')

    alldatainsulins = Insulin.query.all()
    numberof_datainsulins = len(alldatainsulins)
    for insu in alldatainsulins:
        matchinginsulin = NamsInsulin.query.filter_by(insulin_name=insu.full_name).first() # Nam's insulin same name as each data insulin
        if matchinginsulin == None:
            insu.NamisUsing = False
            db.session.add(insu)
            db.session.commit()
        if matchinginsulin is not None:
            if matchinginsulin.currently_inuse == True:
                insu.NamisUsing = True
                db.session.add(insu)
                db.session.commit()
            elif matchinginsulin.currently_inuse != True:
                insu.NamisUsing = False
                db.session.add(insu)
                db.session.commit()


    addnewinsulintype_form = CreateInsulinTypeForm()
    if addnewinsulintype_form.validate_on_submit():
        for i in Insulin.query.all():
            if addnewinsulintype_form.full_name.data == i.full_name:
                flash('Error: Unable to add due to that already existed name. Please check again')
                return redirect(url_for('.namsinsulin_addnewtype'))
        newinsulintype = Insulin()
        newinsulintype.full_name = addnewinsulintype_form.full_name.data
        newinsulintype.full_description = addnewinsulintype_form.full_description.data
        newinsulintype.storing_unit = addnewinsulintype_form.storing_unit.data ####
        newinsulintype.amount_perstoringunit = addnewinsulintype_form.amount_perstoringunit.data ####
        newinsulintype.manufacturer = addnewinsulintype_form.manufacturer.data
        newinsulintype.origin = addnewinsulintype_form.origin.data
        db.session.add(newinsulintype)
        db.session.commit()

        addnewinsulintype_form.amount_perstoringunit.data = 0
        addnewinsulintype_form.storing_unit.data = 'Pen(s)/Needle(s)'

        #### Auto-add to class NamsInsulin
        pseudoi = NamsInsulin.query.filter_by(insulin_name=newinsulintype.full_name).first()
        if pseudoi == None:
            namsinsulin_onetype = NamsInsulin()
            namsinsulin_onetype.insulin_name = newinsulintype.full_name
            namsinsulin_onetype.type_id = Insulin.query.filter_by(full_name=newinsulintype.full_name).first().id
            namsinsulin_onetype.avgamount_perday = 0
            namsinsulin_onetype.avgamount_pertime = 0
            namsinsulin_onetype.current_amount = 0
            ########## namsinsulin_onetype.lasttimepoint_updatebalance
            db.session.add(namsinsulin_onetype)
            db.session.commit()
            flash('Dear Nam, one new type of Insulin '+ "["+str(newinsulintype.full_name)+"]" +' has just been successfully added to database and your personal list. Are you currently using this type? ')
            resp = make_response(redirect(url_for('.namsinsulin_main')))
            resp.set_cookie('newinsulinadded', '1', max_age=4)
            resp.set_cookie('newinsulinadded_id', str(namsinsulin_onetype.id), max_age=300)
            resp.set_cookie('newinsulinadded_name', str(namsinsulin_onetype.insulin_name), max_age=300)
            return resp
        elif pseudoi is not None:
            flash('Notification: Though added to your database, we are unable to add to your personal list simultaneously. This type of Insulin has been already in your personal list. Wir wünschen Ihnen einen guten Tag!')
            return redirect(url_for('.namsinsulin_addnewtype'))

    return render_template("namsinsulin.html", form=addnewinsulintype_form,
                    numberof_datainsulins=numberof_datainsulins, alldatainsulins=alldatainsulins,
                    insulin_removepersonaluse_besidesdatabase=insulin_removepersonaluse_besidesdatabase, insulinid_removeusealso=insulinid_removeusealso)

from .forms import AmendInsulin
@main.route('/namsinsulin/amendment/<int:id>', methods=['GET', 'POST'])
@admin_required
def namsinsulin_amendment(id):
    form = AmendInsulin()
    amendedinsulin = Insulin.query.filter_by(id=id).first()
    if form.validate_on_submit() and form.submit.data == True:
        amendedinsulin.full_name = form.full_name.data
        amendedinsulin.full_description = form.full_description.data
        amendedinsulin.storing_unit = form.storing_unit.data
        amendedinsulin.amount_perstoringunit = form.amount_perstoringunit.data
        amendedinsulin.manufacturer = form.manufacturer.data
        amendedinsulin.origin = form.origin.data
        db.session.add(amendedinsulin)
        db.session.commit()
        flash('Insulin ['+str(amendedinsulin.full_name)+'] has just been amended successfully. Life is beautiful!')
        return redirect(url_for('.namsinsulin_addnewtype'))
    form.full_name.data = amendedinsulin.full_name
    form.full_description.data = amendedinsulin.full_description
    form.storing_unit.data = amendedinsulin.storing_unit
    form.amount_perstoringunit.data = amendedinsulin.amount_perstoringunit
    form.manufacturer.data = amendedinsulin.manufacturer
    form.origin.data = amendedinsulin.origin
    return render_template('namsinsulin_amendment.html', form=form, id=id)

@main.route('/namsinsulin/removefromdb/<int:id>', methods=['GET', 'POST'])
@admin_required
def namsinsulin_removal(id):
    response = make_response(redirect(url_for('.namsinsulin_addnewtype')))
    thatname = Insulin.query.filter_by(id=id).first().full_name
    pseudoi = NamsInsulin.query.filter_by(insulin_name=thatname).first()

    if pseudoi == None:
        removedinsulin = Insulin.query.filter_by(id=id).first()
        db.session.delete(removedinsulin)
        db.session.commit()
        flash('Insulin ['+str(removedinsulin.full_name)+'] has been removed from your databse.')
    if pseudoi is not None:
        thatid = pseudoi.id
        removedinsulin = Insulin.query.filter_by(id=id).first()
        db.session.delete(removedinsulin)
        db.session.commit()
        flash('Insulin ['+str(removedinsulin.full_name)+'] has been removed from your database.')
        flash('Möchten Sie dieses Insulin auch von Ihrer persönlichen Liste entfernen? Life changes when we change!')
        response.set_cookie('insulin_removepersonaluse_besidesdatabase', '1', max_age=4)
        response.set_cookie('insulinid_removeusealso', str(thatid), max_age=4)
    return response

@main.route('/namsinsulin/removefrompersonallist/<int:id>', methods=['GET', 'POST'])
@admin_required
def namsinsulin_removalusealso(id):
    removedinsulin = NamsInsulin.query.filter_by(id=id).first()
    db.session.delete(removedinsulin)
    db.session.commit()
    flash('Insulin ['+str(removedinsulin.insulin_name)+'] has been removed from your personal list. Alles Gutes!')
    response = make_response(redirect(url_for('.namsinsulin_main')))
    response.set_cookie('insulin_removepersonaluse_besidesdatabase', '', max_age=4)
    return response

import os
from .forms import ConfirmAuthorityForm
@main.route('/namsinsulin/confirmprocess/<int:id>', methods=['GET', 'POST'])
@admin_required
def confirmprocess(id):
    form = ConfirmAuthorityForm()
    if form.submit.data == True:
        if form.secret_key.data == os.environ.get('AUTHORITY_CODE'):
            return redirect(url_for('.namsinsulin_removal', id=id))
        if form.secret_key.data != os.environ.get('AUTHORITY_CODE'):
            flash('Code entered was not correct. Heißen Sie Nam? Vielen Dank!')
            return redirect(url_for('.namsinsulin_amendment', id=id))
    return render_template('confirmprocess.html', form=form, id=id)









from ..models import DeadLine
@main.route('/enterdeadlines', methods=['GET', 'POST'])
@admin_required
def enterdeadlines():
    if request.method == "POST":
        rep = make_response(redirect(url_for('.viewalldeadlines')))
        deadline = DeadLine()
        html_datetime = request.values.get('datetime_box')  ## 2021-10-28T19:42
        year, month, day = int(html_datetime.split('-')[0]), int(html_datetime.split('-')[1]), int(html_datetime.split('-')[2].split('T')[0])
        hour, minute = int(html_datetime.split('T')[1].split(':')[0]), int(html_datetime.split(':')[1])

        deadline.deadline_time = datetime(year, month, day, hour, minute, 0, 0)
        deadline.duty = request.values.get('title_box')
        deadline.remember_info = request.values.get('rememberinfo_box')
        deadline.image_url = request.values.get('imageurl_box')

        db.session.add(deadline)
        db.session.commit()
        flash('Hallo there, one new deadline has just been posted. Good luck!')
        return rep
    return render_template("enterdeadlines.html")

import time
from ..ext_functions import today, fullday, fullmonth
from .forms import DeadlineDisplayMode
@main.route('/viewdeadlines', methods=['GET', 'POST'])
@admin_required
def viewalldeadlines():
    alldeadlines = DeadLine.query.all()
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    for deadline in alldeadlines:
        if str(today()) in str(deadline.deadline_time):
            deadline.todayed = True
        if str(today()) not in str(deadline.deadline_time):
            deadline.todayed = False
        if (now-deadline.deadline_time).total_seconds() < 0:
            deadline.overdrafted = False
        if (now-deadline.deadline_time).total_seconds() > 0:
            deadline.overdrafted = True
        db.session.add(deadline)
        db.session.commit()

    ########

    form = DeadlineDisplayMode()
    displaymode = request.cookies.get('displaymode', '')
    if form.set.data == True:
        rep = make_response(redirect(url_for('.viewalldeadlines')))
        rep.set_cookie('displaymode', str(form.option.data))
        return rep
    importedtasks_mode = False
    taskobjects = None
    if displaymode == "Imported from Tasks":
        importedtasks_mode = True
        taskobjects = Namstask.query.filter(Namstask.trashed!=True).all()
    form.option.data = displaymode

    timerange_mode = request.cookies.get('timerange', '')
    if timerange_mode == 'today':
        alldeadlines = DeadLine.query.filter_by(todayed=True).all()
    if timerange_mode == 'thisweek':
        alldeadlines = [d for d in DeadLine.query.all() if d.deadline_time.isocalendar().week==now.isocalendar().week]
    if timerange_mode == 'twoweeks':
        alldeadlines = [d for d in DeadLine.query.all() if d.deadline_time.isocalendar().week==now.isocalendar().week or d.deadline_time.isocalendar().week==now.isocalendar().week+1]
    if timerange_mode == 'thismonth':
        alldeadlines = [d for d in DeadLine.query.all() if d.deadline_time.month==now.month]
    if timerange_mode == 'allsorted':
        alldeadlines = DeadLine.query.order_by(DeadLine.deadline_time.asc()).all()
    ##print('now.isocalendar().week = '+str(now.isocalendar())) ## datetime.IsoCalendarDate(year=2021, week=42, weekday=2)
    ##print(now.month) ## 10
    ##print(now.isoweekday()) ## 2
    ##print(time.asctime()) ## Tue Oct 19 08:27:56 2021
    return render_template('viewdeadlines.html', alldeadlines=alldeadlines, now=now, displaymode=displaymode, form=form,
                            importedtasks_mode=importedtasks_mode, taskobjects=taskobjects, timerange_mode=timerange_mode)

@main.route('/viewdeadlines/allsorted', methods=["GET", "POST"])
@admin_required
def deadlinesallsorted():
    rep = make_response(redirect(url_for('.viewalldeadlines')))
    rep.set_cookie('timerange', 'allsorted', max_age=4)
    return rep

@main.route('/viewdeadlines/today', methods=["GET", "POST"])
@admin_required
def deadlinestoday():
    rep = make_response(redirect(url_for('.viewalldeadlines')))
    rep.set_cookie('timerange', 'today')
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    todayshow = fullday(str(time.asctime()).split(' ')[0])+', '+str(now.day)+' '+fullmonth(str(time.asctime()).split(' ')[1].split(' ')[0])+' '+str(now.year)
    flash(todayshow)
    return rep

@main.route('/viewdeadlines/thisweek', methods=["GET", "POST"])
@admin_required
def deadlinesthisweek():
    rep = make_response(redirect(url_for('.viewalldeadlines')))
    rep.set_cookie('timerange', 'thisweek')
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    dayofweek = now.isoweekday()
    within = 7 - int(now.isoweekday())
    flash('Within ~'+str(within)+' day(s)')
    return rep

@main.route('/viewdeadlines/twoweeks', methods=["GET", "POST"])
@admin_required
def deadlinesintwoweeks():
    rep = make_response(redirect(url_for('.viewalldeadlines')))
    rep.set_cookie('timerange', 'twoweeks')
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    dayofweek = now.isoweekday()
    within = 14 - int(now.isoweekday())
    flash('Within ~'+str(within)+' day(s)')
    return rep

@main.route('/viewdeadlines/thismonth', methods=["GET", "POST"])
@admin_required
def deadlinesthismonth():
    rep = make_response(redirect(url_for('.viewalldeadlines')))
    rep.set_cookie('timerange', 'thismonth')
    struct_time = time.localtime()
    now = datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec, 0)
    value_nowday = now.day
    if len(str(now.day)) > 1 and str(now.day)[0]=='0':
        value_nowday = int(str(now.day)[1])
    within = 30 - value_nowday
    if fullmonth(str(time.asctime()).split(' ')[1].split(' ')[0]) == 'February':
        within = 28 - value_nowday
    flash('Within ~'+str(within)+' day(s)')
    return rep

#############################################

@main.route('/offdeadlines/<int:id>')
@admin_required
def offdeadlines(id):
    deadline = DeadLine.query.filter_by(id=id).first()
    db.session.delete(deadline)
    db.session.commit()
    flash('Fertig!')
    return redirect(url_for('.viewalldeadlines'))

@main.route('/setdeadlines/<int:id>')
@admin_required
def setdeadlines(id):
    deadline = DeadLine()
    mission_name = Namstask.query.filter_by(id=id).first().taskname
    deadlinetotask = True
    return render_template('enterdeadlines.html', mission_name=mission_name, deadlinetotask=deadlinetotask)
