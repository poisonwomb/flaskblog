from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.forms import RegistrationForm, LoginForm

from flaskblog import app, db, bcrypt

from flaskblog.models import AppUser, Post

posts = [
    {
        "author": "Jane Austen",
        "title": "Blog Post 1",
        "content": "Hello!!",
        "posted_date": "April 24, 2023",
    },
    {
        "author": "Adolph Hitler",
        "title": "My Struggle",
        "content": "Fourscore and seven years ago, my name was John Galt.",
        "posted_date": "April 20, 2023",
    },
]


@app.route(rule="/")
@app.route(rule="/home")
def home():
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
            args = request.args
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


@app.route(rule="/account")
@login_required
def account():
    return render_template("account.html", title="Account")
