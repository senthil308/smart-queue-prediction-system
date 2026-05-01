from flask import Flask
from config import Config
from extensions import db, bcrypt, jwt, socketio, cors
import os # Moved import os here as it's used for config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Add specific config parameters, potentially overriding those from config_class
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Completely disable 15 minute timer expiration

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    from models.admin import Admin
    from auth.routes import auth_bp
    from queues.routes import queue_bp
    from tokens.routes import tokens_bp
    from sharing.routes import sharing_bp
    from admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(queue_bp, url_prefix='/api/queue')
    app.register_blueprint(tokens_bp, url_prefix='/api/tokens')
    app.register_blueprint(sharing_bp, url_prefix='/api/sharing')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from flask import send_from_directory, redirect

    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

    @app.route('/')
    def serve_root():
        return redirect('/login.html')

    @app.route('/login.html')
    def serve_login():
        return send_from_directory(frontend_dir, 'login.html')

    @app.route('/user.html')
    def serve_user():
        return send_from_directory(frontend_dir, 'user.html')

    @app.route('/admin.html')
    def serve_admin():
        return send_from_directory(frontend_dir, 'admin.html')

    # Legacy index.html still accessible
    @app.route('/index.html')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/css/<path:path>')
    def serve_css(path):
        return send_from_directory(os.path.join(frontend_dir, 'css'), path)

    @app.route('/js/<path:path>')
    def serve_js(path):
        return send_from_directory(os.path.join(frontend_dir, 'js'), path)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all() # Creates tables if they don't exist
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=5000)
