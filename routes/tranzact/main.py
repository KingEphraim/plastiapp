from flask import Blueprint,session,render_template


tranzact_bp = Blueprint('tranzact', __name__)


@tranzact_bp.route('/tranzact')
def tranzact():
    if "username" in session: 
        user_is_logged_in = session.get('user_is_logged_in', True)        
        return render_template('tranzact.html', user_is_logged_in=user_is_logged_in)
    else:
        return render_template('tranzact.html')     
    