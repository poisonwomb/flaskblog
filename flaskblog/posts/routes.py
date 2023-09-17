from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import current_user, login_required

from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

posts = Blueprint("posts", __name__)


@posts.route(rule="/new-post", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))
    return render_template(
        "new_post.html", title="New Post", form=form, legend="New Post"
    )


@posts.route(rule="/post/<int:post_id>")
def post(post_id: int):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@posts.route(rule="/post/<int:post_id>/update", methods=["GET", "POST"])
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
        return redirect(url_for("posts.post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "new_post.html", title="Update Post", form=form, legend="Update Post"
    )


@posts.route(rule="/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(message="Your post has been deleted!", category="success")
    return redirect(url_for("main.home"))
