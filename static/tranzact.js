window.onload = function () {
    ckGooglePay.enableGooglePay({ amountField: "amount" });
    enable3DS('staging', handle3DSResults);
    let style = {
        'background-color': 'rgb(255, 255, 255)',
        'border-color': 'rgb(222, 226, 230)',
        'border-radius': '6px',
        'border-style': 'solid',
        'border-width': '1px',
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
		merchantName: "test1",
	},
	buttonOptions: {
		buttonSizeMode: GPButtonSizeMode.fill,
	},
	billingParams: {
		billingAddressRequired: true,
		billingAddressFormat: GPBillingAddressFormat.full,
	},
	onGetTransactionInfo: function () {
		return {
			totalPriceStatus: "FINAL",
			currencyCode: "USD",
			totalPrice: amount.value,
		};
	},
	onProcessPayment: function (paymentResponse) {
		return processGP(paymentResponse);
	},
	onPaymentCanceled: function () {
		displayLogToast({ xStatus: "Canceled", xRefNum: "" }, "Google Pay");
	},
};
//initiates googlepay
function initGP() {
	console.log("googlepay init");
	return {
		merchantInfo: gpRequest.merchantInfo,
		buttonOptions: gpRequest.buttonOptions,
		onGetTransactionInfo: "gpRequest.onGetTransactionInfo",
		billingParameters: gpRequest.billingParams,
		onProcessPayment: "gpRequest.onProcessPayment",
		onPaymentCanceled: "gpRequest.onPaymentCanceled",
	};
}
//checks if test or production for googlepay
function gpayEnv() {
	const gpenv = document.getElementById("gpay-environment").value;
	if (gpenv === "production") {
		return "PRODUCTION";
	} else {
		return "TEST";
	}
}
//sends token and fields to server
function processGP(paymentResponse) {
	return new Promise(function (resolve, reject) {
		paymentToken =
			paymentResponse.paymentData.paymentMethodData.tokenizationData
				.token;
		encodedToken = window.btoa(paymentToken);
		
		console.log(JSON.stringify({  paymentResponse, encodedToken }));
        
        var formData = {};
        var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount",  "phone"];

        fields.forEach(function (field) {
            formData[field] = document.getElementById(field).value;
        });
        formData['tranzType'] = "GP";
        formData['gptoken'] = encodedToken;
        
        var formDataJSON = JSON.stringify(formData);

        

        sendtoserver(formDataJSON)
			.then((response) => response.json())
			.then((data) => {
				if (data.Response.xStatus) {
					if (data.Response.xStatus === "Approved") {
						resolve(data);
					} else {
						reject(data);
					}
				} else {
					reject(data);
				}
				//displayLogToast(data.Response, "Google Pay");
			});
	});
}