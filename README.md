# flaskblog

Flask Blog

To make sure the database file is created, and to use models from this app within the REPL, you may need to run
the following commands from within the REPL:

from flaskblog import app, db
app.app_context().push()
db.create_all()

Then the .db file is created in a folder called "Instance" in your project. 