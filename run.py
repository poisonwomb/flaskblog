from flaskblog import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Host="0.0.0.0" is necessary to access the app when running in Docker.
    app.run(debug=True, host="0.0.0.0", port=5000)
