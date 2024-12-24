from flask import Blueprint, session, render_template, request

tranzact_bp = Blueprint('tranzact', __name__)


@tranzact_bp.route('/tranzact')
def tranzact():
    # Get query parameters
    payinvoice = request.args.get('payinvoice')
    name = request.args.get('name')
    amount = request.args.get('amount')
    email = request.args.get('email')
    address = request.args.get('address')
    city = request.args.get('city')
    state = request.args.get('amount')
    zip = request.args.get('zip')
    comments = request.args.get('comments')
    invoice = request.args.get('invoice')
    

    # Check if the user is logged in
    user_is_logged_in = "username" in session

    return render_template(
        'tranzact.html',
        user_is_logged_in=user_is_logged_in,
        name=name if payinvoice == 'true' else '',
        amount=amount if payinvoice == 'true' else '',
        email=email if payinvoice == 'true' else '',
        address=address if payinvoice == 'true' else '',
        city=city if payinvoice == 'true' else '',
        state=state if payinvoice == 'true' else '',
        zip = zip if payinvoice == 'true' else '',
        comments = comments if payinvoice == 'true' else '',
        invoice = invoice if payinvoice == 'true' else ''
    )
