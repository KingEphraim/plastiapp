from flask import Blueprint

customer__bp = Blueprint('customer', __name__)

@customer__bp.route('/customer', methods=['POST'])
def customer():
    return
