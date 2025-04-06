from . import api
from ..auth import auth
from flask_login import login_required


#@auth.login_required
#@api.route('/posts/')
#@login_required
#def get_posts():
#    pass

#from ..models import Post
#@api.route('/posts/', methods=['POST'])
#def new_post():
#    post = Post.from_json(request.json)
#    post.author = g.current_user
#    db.session.add(post)
#    db.session.commit()
#    return jsonify(post.to_json())

#@api.route('/posts/')
#def get_posts():
#    posts = Post.query.all()
#    return jsonify({ 'posts': [post.to_json() for post in posts] })

@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

from .decorators import permission_required
from ..models import Permission
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)  # def from_json(json_post)  return Post(body=body)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}  #### model is written to the database,
                                        # a 201 status code is returned,
                                        # and a Location header is added with the URL of the newly created resource.

# PUT resource handler for editting posts
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)  ##
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())

# Post pagination
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKE_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev_url': prev,
        'next_url': next,
        'count': pagination.total
    })
