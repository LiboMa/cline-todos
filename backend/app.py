from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.config import Config
from backend.models import db, Todo
from backend.auth import auth_bp, init_jwt

app = Flask(__name__, static_folder=Config.STATIC_FOLDER)
app.config.from_object(Config)

# Initialize JWT
jwt = init_jwt(app)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Setup CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins in development
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize SQLAlchemy
db.init_app(app)

# Create tables on startup
with app.app_context():
    db.create_all()

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({'error': 'Unprocessable Entity', 'message': str(error)}), 422

# Frontend routes
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Protected API routes
@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    try:
        current_user_id = int(get_jwt_identity())
        todos = Todo.query.filter_by(user_id=current_user_id).all()
        return jsonify([todo.to_dict() for todo in todos])
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to fetch todos', 'message': str(e)}), 500

@app.route('/api/todos', methods=['POST'])
@jwt_required()
def add_todo():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        current_user_id = int(get_jwt_identity())
        todo_data = request.get_json()
        
        if not todo_data:
            return jsonify({'error': 'No data provided'}), 400

        new_todo = Todo.from_dict(todo_data, current_user_id)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create todo', 'message': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    try:
        current_user_id = int(get_jwt_identity())
        todo = Todo.query.get_or_404(todo_id)
        
        # Verify ownership
        if todo.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        todo_data = request.get_json()
        if not todo_data:
            return jsonify({'error': 'No data provided'}), 400

        if 'name' in todo_data:
            if not todo_data['name']:
                return jsonify({'error': 'Name cannot be empty'}), 400
            todo.name = todo_data['name']
        if 'comment' in todo_data:
            todo.comment = todo_data['comment']

        db.session.commit()
        return jsonify(todo.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update todo', 'message': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    try:
        current_user_id = int(get_jwt_identity())
        todo = Todo.query.get_or_404(todo_id)
        
        # Verify ownership
        if todo.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access'}), 403

        db.session.delete(todo)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete todo', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
