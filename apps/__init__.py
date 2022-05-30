from flask import Flask
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # setup with the configuration provided
    app.config.from_object('config.DevelopmentConfig')
    
    # setup all dependencies
    jwt.init_app(app)

    # register blueprint
    from apps.auth.views import auth
    from apps.post.views import post
    app.register_blueprint(auth)
    app.register_blueprint(post)
    
    return app