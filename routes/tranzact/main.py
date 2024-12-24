from flask import Blueprint, session, render_template, request

tranzact_bp = Blueprint('tranzact', __name__)


@tranzact_bp.route('/tranzact')
def tranzact():
    # Get query parameters
    payinvoice = request.args.get('payinvoice')
    name = request.args.get('name')
    amount = request.args.get('amount')

    # Check if the user is logged in
    user_is_logged_in = "username" in session

    # Render the template with pre-filled data if applicable
    return render_template(
        'tranzact.html',
        user_is_logged_in=user_is_logged_in,
        name=name if payinvoice == 'true' else '',
        amount=amount if payinvoice == 'true' else ''
    )
