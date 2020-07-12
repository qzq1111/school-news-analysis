from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = '11dsadas@@$%'
    from .index.index import index_bp

    app.register_blueprint(index_bp)
    return app
