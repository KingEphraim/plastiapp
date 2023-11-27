window.onload = function() {
    let style = {
        display: 'block',
        width: '90%',
        'font-size': '1rem',
        'font-weight': '400',
        'line-height': '1.5',
        color: 'var(--bs-body-color)',
        appearance: 'none',
        'background-color': 'var(--bs-body-bg)',
        'background-clip': 'padding-box',
        border: 'var(--bs-border-width) solid var(--bs-border-color)',
        'border-radius': 'var(--bs-border-radius)',
        transition: 'border-color .15s ease-in-out,box-shadow .15s ease-in-out',
    };
    setIfieldStyle('card-number', style);
    setIfieldStyle('cvv', style);
  };

const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
const appendAlert = (message, type) => {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('')

    alertPlaceholder.insertBefore(wrapper, alertPlaceholder.firstChild)
}



const button = document.getElementById("sbmtbtn");
button.addEventListener("click", () => {
    setAccount("ifields_cardkndemodevc039cbc0007b426295100ecf", "tranzact", "1.0");
    enable3DS('staging', handle3DSResults);
    function handle3DSResults(actionCode, xCavv, xEciFlag, xRefNum, xAuthenticateStatus, xSignatureVerification) {

        var postData = {
            tranzType: "V",
            xRefNum: xRefNum,
            xCavv: xCavv,
            xEci: xEciFlag,
            x3dsAuthenticationStatus: xAuthenticateStatus,
            x3dsSignatureVerificationStatus: xSignatureVerification,
            x3dsActionCode: actionCode,
            x3dsError: ck3DS.error
        };
        sendtoserver(JSON.stringify(postData))
    }


    getTokens(function () {
        var formData = {};
        var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "card", "exp", "cvv", "phone"];

        fields.forEach(function (field) {
            formData[field] = document.getElementById(field).value;
        });
        formData['tranzType'] = "R";
        // Convert JSON to string for display or further processing
        var formDataJSON = JSON.stringify(formData);

        // Display JSON in the console (for testing)
        // console.log(formDataJSON);
        // appendAlert(formDataJSON, 'success');

        sendtoserver(formDataJSON)


    }, 10000,);
});

function sendtoserver(serverdata) {

    fetch('/sendtocardknox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: serverdata
    })
        .then(response => response.json())
        .then(data => {
            if (data.xResult == "A") {
                appendAlert(JSON.stringify(data), 'success');
            } else if (data.xResult == "V") {
                verify3DS(data)
                appendAlert(JSON.stringify(data), 'info');
            }
            else {
                appendAlert(JSON.stringify(data), 'danger');
            }
        })
        .catch(error => console.error(error));
}





