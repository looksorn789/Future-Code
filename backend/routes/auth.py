from flask import Blueprint, jsonify

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/ping', methods=['GET'])

def test_ping():
    ping = {
        "ok": True
    }
    return jsonify(ping), 200