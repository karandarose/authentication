import routes

def register_blueprint(app):
    app.register_blueprint(routes.users)
    app.register_blueprint(routes.auth)
    app.register_blueprint(routes.org)
    app.register_blueprint(routes.search)