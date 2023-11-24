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
            tranzType:"V",
            xRefNum: xRefNum,
            xCavv: xCavv,
            xEci: xEciFlag,
            x3dsAuthenticationStatus: xAuthenticateStatus,
            x3dsSignatureVerificationStatus: xSignatureVerification,
            x3dsActionCode: actionCode,
            x3dsError: ck3DS.error
        };

        console.log(postData)


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

 
    }, 30000,);
});

function sendtoserver(serverdata){

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




