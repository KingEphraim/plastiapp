from flask import Blueprint

invoice__bp = Blueprint('invoice', __name__)

@invoice__bp.route('/invoice', methods=['POST'])
def invoice():
    return
