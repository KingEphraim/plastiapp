from flask import Blueprint, request

ebtresponse__bp = Blueprint('ebtresponse', __name__)


@ebtresponse__bp.route('/ebtresponse', methods=['POST'])
def ebtresponse():
    # Extract response data (for POST requests)
    response_data = request.form.to_dict() if request.method == 'POST' else {}
    print(response_data)

    # Return a script to post the response back to the parent
    return f"""
    <script>
        window.parent.postMessage({{
            'acuResponse': {response_data}
        }}, "http://127.0.0.1:5000");
    </script>
    """
