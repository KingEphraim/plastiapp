//global params
const sbmtbtn = document.getElementById("sbmtbtn");
const sbmtbtnspin = document.getElementById("sbmtbtnspin");
const sbmtbtncont = document.getElementById("sbmtbtncont");
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
    sbmtbtntoggle('on');
}

window.onload = function () {
    ckGooglePay.enableGooglePay({ amountField: "amount" });
    enable3DS('staging', handle3DSResults);
    let style = {
        'background-color': 'rgb(255, 255, 255)',
        'border-color': 'rgb(222, 226, 230)',
        'border-radius': '6px',
        'border-style': 'solid',
        'border-width': '1px',
        padding: '1rem .75rem',
        display: 'block',
        'box-sizing': 'border-box',
        width: '100%',
        'overflow': 'hidden',
        'font-size': '1rem',
        'font-weight': '400',
        'line-height': '24px',
    };
    setIfieldStyle('card-number', style);
    setIfieldStyle('cvv', style);


};
function handle3DSResults(x3dsActionCode, xCavv, xEci, xRefNum, x3dsAuthenticationStatus, x3dsSignatureVerificationStatus) {

    var postData = {
        tranzType: "V",
        x3dsActionCode: x3dsActionCode,
        xCavv: xCavv,
        xEci: xEci,
        xRefNum: xRefNum,
        x3dsAuthenticationStatus: x3dsAuthenticationStatus,
        x3dsSignatureVerificationStatus: x3dsSignatureVerificationStatus,
        //x3dsError: ck3DS.error
    };
    sendtoserver(JSON.stringify(postData))
}







sbmtbtn.addEventListener("click", () => {
    sbmtbtntoggle('off');
    setAccount("ifields_ephraimdev1f011616e4ba4f75b0bbcf26417", "tranzact", "1.0");
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

//googlepay object
const gpRequest = {
    merchantInfo: {
        merchantName: "Tranzact",
    },
    buttonOptions: {
        buttonColor: GPButtonColor.default,
        buttonType: GPButtonType.plain,
        buttonSizeMode: GPButtonSizeMode.fill
    },
    billingParams: {
        //allowedAuthMethods:["PAN_ONLY"],
        //allowedCardNetworks:["AMEX", "DISCOVER", "MASTERCARD", "VISA"],
        phoneNumberRequired: false,
        billingAddressRequired: true,
        billingAddressFormat: GPBillingAddressFormat.full,
    },
    onGetTransactionInfo: function () {
        return {
            totalPriceStatus: "FINAL",
            currencyCode: "USD",
            totalPrice: amount.value ? amount.value : "0",            
        };
    },
    onProcessPayment: function (paymentResponse) {
        return processGP(paymentResponse);
    },
    onPaymentCanceled: function () {
        setTimeout(function () { appendAlert("Payment was canceled", 'info') }, 500);
    },
};

//initiates googlepay
function initGP() {
    console.log("googlepay init");
    return {
        merchantInfo: gpRequest.merchantInfo,
        buttonOptions: gpRequest.buttonOptions,
        onGetTransactionInfo: "gpRequest.onGetTransactionInfo",
        environment: "PRODUCTION",
        billingParameters: gpRequest.billingParams,
        onProcessPayment: "gpRequest.onProcessPayment",
        onPaymentCanceled: "gpRequest.onPaymentCanceled",
    };
}

//process googlepay
function processGP(paymentResponse) {
    return new Promise(function (resolve, reject) {
        try {
            paymentToken = paymentResponse.paymentData.paymentMethodData.tokenizationData.token;
            encodedToken = window.btoa(paymentToken);
            console.log(JSON.stringify({ paymentResponse, encodedToken }));
            var formData = {};
            var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "phone"];
            fields.forEach(function (field) {
                formData[field] = document.getElementById(field).value;
            });        
            formData['tranzType'] = "GP";
            formData['gptoken'] = encodedToken;
            var formDataJSON = JSON.stringify(formData);
            sendtoserver(formDataJSON)
            resolve()
        } catch (err) {
            reject(err);
        }
    });
}

//PayButtonToggle
function sbmtbtntoggle(state) {



    if (state === 'on') {
        sbmtbtn.disabled = false;
        sbmtbtnspin.hidden = true;
        sbmtbtncont.textContent = "Pay Now";
        // Perform actions when the switch is turned on
        console.log('Switch is ON');
        // Add more code as needed
    } else if (state === 'off') {
        sbmtbtn.disabled = true;
        sbmtbtnspin.hidden = false;
        sbmtbtncont.textContent = "Please Wait";

        // Perform actions when the switch is turned off
        console.log('Switch is OFF');
        // Add more code as needed
    } else {
        // Handle invalid state
        console.error('Invalid state. Please provide "on" or "off".');
    }
}