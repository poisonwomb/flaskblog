from flask import render_template, url_for, flash, redirect
from flask_login import login_user
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


@app.route("/")
@app.route("/home")
def home():
    return render_template(template_name_or_list="home.html", posts=posts)


@app.route("/about")
def about():
    return render_template(template_name_or_list="about.html", title="About")


# methods parameter denotes the HTTP methods this route will accept.
@app.route("/register", methods=["GET", "POST"])
def register():
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


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AppUser.query.filter_by(email=form.email.data).first()
        # Check user exists and password matches hashed password.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
        else:
            flash(
                message="Invalid login credentials!",
                category="danger",
            )
    return render_template("login.html", title="Login", form=form)
