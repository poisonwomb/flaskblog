from pathlib import Path
import secrets

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm

# Pillow (image resizing)
from PIL import Image

from flaskblog import app, db, bcrypt

from flaskblog.models import AppUser, Post


@app.route(rule="/")
@app.route(rule="/home")
def home():
    page = request.args.get("page", default=1, type=int)
    posts = Post.query.order_by(Post.posted_date.desc()).paginate(per_page=5, page=page)
    return render_template(template_name_or_list="home.html", posts=posts)


@app.route(rule="/about")
def about():
    return render_template(template_name_or_list="about.html", title="About")


# methods parameter denotes the HTTP methods this route will accept.
@app.route(rule="/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    """This instantiates the form class imported from forms.py that
    is then passed to register.html using Jinja templating."""
    form = RegistrationForm()
    # Validate the input of the form
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = AppUser(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        """Flash (Flask class) allows you to show a message (message parameter).
        Category parameter is the bootstrap css class 'success' for styling."""
        flash(
            message="Your account has been created! You are now able to log in.",
            category="success",
        )
        # url_for dynamically retrieves the URL of the home route.
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route(rule="/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    # If input passes the validation defined in forms.py...
    if form.validate_on_submit():
        # Query the database for the user, using their email.
        user = AppUser.query.filter_by(email=form.email.data).first()
        # Check user exists and password matches hashed password.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in with flask_login.
            login_user(user, remember=form.remember.data)
            # Get the (optional) 'next' argument passed by the prev page.
            next_page = request.args.get("next")
            # If the 'next' argument was provided, redirect to that page, else home.
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(
                message="Invalid login credentials!",
                category="danger",
            )
    return render_template("login.html", title="Login", form=form)


@app.route(rule="/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def save_picture(form_picture):
    pics_path = Path(app.root_path) / "static/profile_pics"
    random_hex = secrets.token_hex(8)
    f_ext = Path(form_picture.filename).suffix

    picture_filename = random_hex + f_ext
    new_picture_path = pics_path / picture_filename
    prev_picture_path = pics_path / current_user.image_file

    output_size = (250, 250)
    # Create a new pillow image object from the uploaded picture.
    image = Image.open(form_picture)
    # Reduce the image to the size in output_size.
    image.thumbnail(output_size)

    if prev_picture_path.exists():
        # Delete the previous picture.
        prev_picture_path.unlink()
    image.save(new_picture_path)
    return picture_filename


@app.route(rule="/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(message="Your account has been updated!", category="success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@app.route(rule="/new-post", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash(message="Your post has been created!", category="success")
        return redirect(url_for("home"))
    return render_template(
        "new_post.html", title="New Post", form=form, legend="New Post"
    )


@app.route(rule="/post/<int:post_id>")
def post(post_id: int):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route(rule="/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # No need to add to the session as the post is already in the db.
        db.session.commit()
        flash(message="Your post has been updated!", category="success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "new_post.html", title="Update Post", form=form, legend="Update Post"
    )


@app.route(rule="/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(message="Your post has been deleted!", category="success")
    return redirect(url_for("home"))


@app.route(rule="/user/<string:username>")
def user_posts(username):
    user = AppUser.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", default=1, type=int)
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.posted_date.desc())
        .paginate(per_page=5, page=page)
    )
    return render_template(
        template_name_or_list="user_posts.html", posts=posts, user=user
    )
