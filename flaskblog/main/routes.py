from flask import Blueprint, render_template, request

from flaskblog.models import Post

main = Blueprint("main", __name__)


@main.route(rule="/")
@main.route(rule="/home")
def home():
    page = request.args.get("page", default=1, type=int)
    posts = Post.query.order_by(Post.posted_date.desc()).paginate(per_page=5, page=page)
    return render_template(template_name_or_list="home.html", posts=posts)


@main.route(rule="/about")
def about():
    return render_template(template_name_or_list="about.html", title="About")
