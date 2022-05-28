from flask import render_template
from online_store import app


@app.errorhandler(404)
def not_found_error(error):
    return render_template("4.html", error=error), 404


@app.errorhandler(400)
def bad_request_error(error):
    return render_template("4.html", error=error), 400


@app.errorhandler(401)
def unauthorized_error(error):
    return render_template("4.html", error=error), 401


@app.errorhandler(403)
def forbidden_error(error):
    return render_template("4.html", error=error), 403

@app.errorhandler(405)
def invalid_method_error(error):
    return render_template("4.html", error=error), 405


@app.errorhandler(422)
def not_processable_error(error):
    return render_template("4.html", error=error), 422


@app.errorhandler(409)
def duplicate_resource_error(error):
    return render_template("4.html", error=error), 409


@app.errorhandler(500)
def bad_request_error(error):
    return render_template("4.html", error=error), 500
