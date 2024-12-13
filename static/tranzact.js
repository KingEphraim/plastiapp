let userEmail = '';
let userKey = '';
let userCommand = '';
let userPhone = '';
let user3ds = false;
let ccdevice = false;
const sbmtbtn = document.getElementById("sbmtbtn");
const sbmtbtnspin = document.getElementById("sbmtbtnspin");
const sbmtbtncont = document.getElementById("sbmtbtncont");
const ccdevicebtn = document.getElementById("ccdevicebtn");
const ccdevicebtnspin = document.getElementById("ccdevicebtnspin");
const ccdevicebtncont = document.getElementById("ccdevicebtncont");
const ebtOnlinebtn = document.getElementById("ebtOnlinebtn");
const ebtOnlinebtnspin = document.getElementById("ebtOnlinebtnspin");
const ebtOnlinebtncont = document.getElementById("ebtOnlinebtncont");
const alertPlaceholder = document.getElementById('TransactionLogsPlaceholder')
const modalElement = new bootstrap.Modal(document.getElementById('userNotificationModal'));
const notificationCardHeader = document.getElementById("userNotificationCardHeader");
const notificationCardHeaderP = document.getElementById("userNotificationCardHeaderP");
const notificationCardBodyH = document.getElementById("userNotificationCardBodyH");
const notificationCardBodyP = document.getElementById("userNotificationCardBodyP");
const transactionLogsSubHead = document.getElementById('transactionLogsSubHead');
let userGooglePay = false;
let userebtOnline = false;



function updateUser(serverData, options = {}) {
    const { transactionType = 'sale' } = options;
    console.log(transactionType);
    notificationCardHeader.className = "card-header bg-success text-white text-center py-4";
    notificationCardHeaderP.innerText = "";
    notificationCardBodyH.innerText = "";
    notificationCardBodyP.innerText = "";
    document.getElementById("referenceNumber").textContent = "0";
    document.getElementById("amountPaid").textContent = "0";
    document.getElementById("date").textContent = "0";
    document.getElementById("cardInfo").textContent = "0";
    switch (serverData.xResult) {
        case 'A':
            console.log("xResult is A");
            if (transactionType === 'void') {
                notificationCardHeader.className = "card-header bg-info text-white text-center py-4";
                notificationCardHeaderP.innerText = "Transaction Voided";
                notificationCardBodyH.innerText = "We’re grateful for the opportunity to serve you.";
                notificationCardBodyP.innerText = "Your payment has been successfully Voided.";
            } else if (transactionType === 'capture') {
                notificationCardHeader.className = "card-header bg-info text-white text-center py-4";
                notificationCardHeaderP.innerText = "Transaction Captured";
                notificationCardBodyH.innerText = "We’re grateful for the opportunity to serve you.";
                notificationCardBodyP.innerText = "Your payment has been successfully Captured.";
            }
            else {
                notificationCardHeader.className = "card-header bg-success text-white text-center py-4";
                notificationCardHeaderP.innerText = "Transaction Approved";
                notificationCardBodyH.innerText = "Thank you for your purchase!";
                notificationCardBodyP.innerText = "Your payment has been processed successfully.";

            }

            modalElement.show();
            break;
        case 'E':
            console.log("xResult is E");
            if (transactionType === 'void') {

                notificationCardHeader.className = "card-header bg-danger text-white text-center py-4";
                notificationCardHeaderP.innerText = "Void Failed";
                notificationCardBodyH.innerText = "Something went wrong";
            } else if (transactionType === 'capture') {
                notificationCardHeader.className = "card-header bg-danger text-white text-center py-4";
                notificationCardHeaderP.innerText = "Capture Failed";
                notificationCardBodyH.innerText = "Something went wrong";
            }

            else {
                notificationCardHeader.className = "card-header bg-danger text-white text-center py-4";
                notificationCardHeaderP.innerText = "Transaction Declined";
                notificationCardBodyH.innerText = "Unfortunately, your payment could not be processed.";
            }
            if (serverData.xError) {
                notificationCardBodyP.innerText = serverData.xError;
            }
            modalElement.show();
            break;
        case 'D':
            console.log("xResult is D");
            notificationCardHeader.className = "card-header bg-danger text-white text-center py-4";
            notificationCardHeaderP.innerText = "Transaction Declined";
            notificationCardBodyH.innerText = "Unfortunately, your payment could not be processed.";
            if (serverData.xError) {
                notificationCardBodyP.innerText = serverData.xError;
            }
            modalElement.show();
            break;
        case 'S':
            console.log("xResult is S");
            if (serverData.xSessionStatus === 'ERROR' || serverData.xSessionStatus === 'TIMEOUT' || serverData.xSessionStatus === 'USER_CANCELLED' | serverData.xSessionStatus === 'API_CANCELLED') {
                notificationCardHeader.className = "card-header bg-danger text-white text-center py-4";
                notificationCardHeaderP.innerText = "Transaction Declined";
                notificationCardBodyH.innerText = "Unfortunately, your payment could not be processed.";
                notificationCardBodyP.innerText = serverData.xSessionError;
            } else {
                notificationCardHeader.className = "card-header bg-success text-white text-center py-4";
                notificationCardHeaderP.innerText = "Transaction Approved";
                notificationCardBodyH.innerText = "Thank you for your purchase!";
                notificationCardBodyP.innerText = "Your payment has been processed successfully.";
            }
            modalElement.show();

            break;
        case 'V':
            // Handle case where xResult is 'V'
            console.log("xResult is V");
            break;
        default:
            console.log("xResult is something else");
            notificationCardHeader.className = "card-header bg-danger text-white text-center py-4";
            notificationCardHeaderP.innerText = "Transaction Declined";
            notificationCardBodyH.innerText = "Unfortunately, your payment could not be processed.";
            notificationCardBodyP.innerText = serverData.AccuResponseMsg || serverData;
            console.log(serverData)
            modalElement.show();
    }

    if (serverData.xRefNum || serverData.xGatewayRefnum) {
        document.getElementById("referenceNumber").textContent = serverData.xRefNum || serverData.xGatewayRefnum;
    }
    if (serverData.xAuthAmount || (serverData.xTransactionResult && serverData.xTransactionResult.xAuthAmount)) {
        const amount = serverData.xAuthAmount || serverData.xTransactionResult.xAuthAmount;
        document.getElementById("amountPaid").textContent = `$${amount}`;
    }
    if (serverData.xDate || (serverData.xTransactionResult && serverData.xTransactionResult.xDate)) {
        const date = serverData.xDate || serverData.xTransactionResult.xDate;
        const formattedDate = formatDate(date);
        document.getElementById("date").textContent = formattedDate;
    }
    if (serverData.xMaskedCardNumber || (serverData.xTransactionResult && serverData.xTransactionResult.xMaskedCardNumber)) {
        const cardNumber = serverData.xMaskedCardNumber || serverData.xTransactionResult.xMaskedCardNumber;
        const cardType = serverData.xCardType || serverData.xTransactionResult.xCardType;
        document.getElementById("cardInfo").textContent = `${cardType} (${cardNumber})`;
    }


}



// Append alert to alertPlaceholder
const appendAlert = (message, type, ccDeviceToggle = 'on', ebtOnlineToggle = 'on', ckRequest = '') => {
    const wrapper = document.createElement('div');
    wrapper.className = `alert alert-${type} alert-dismissible`;
    wrapper.role = 'alert';
    wrapper.innerHTML = `
    <div>${message}</div>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    ${(shouldShowVoidButton(message) && ckRequest.xCommand !== 'cc:voidrefund') ? '<button type="button" class="btn btn-warning" id="voidRefundBtn">Void/Refund</button>' : ''}
    ${ckRequest.xCommand === 'cc:authonly' && shouldShowCaptureButton(message) ? '<button type="button" class="btn btn-warning" id="captureBtn">Capture</button>' : ''}
`;

    try {
        const alertPlaceholder = document.getElementById('TransactionLogsPlaceholder');
        if (alertPlaceholder) {
            alertPlaceholder.prepend(wrapper);
        } else {
            console.warn('alertPlaceholder element not found. Alert not added.');
        }
    } catch (error) {
        console.error('Error while appending alert:', error);
    }

    sbmtbtntoggle('on');
    ccdevicebtntoggle(ccDeviceToggle);
    ebtOnlinebtntoggle(ebtOnlineToggle);
};




const shouldShowVoidButton = (message) => {
    return /"xResult":"[AS]"/.test(message) && /xRefNum|xGatewayRefnum/.test(message);
};
const shouldShowCaptureButton = (message) => {
    return /"xResult":"[AS]"/.test(message) && /xRefNum|xGatewayRefnum/.test(message);
};

// Event listener for void/refund button clicks
if (alertPlaceholder) {
    alertPlaceholder.addEventListener('click', ({ target }) => {
        if (target?.id === 'voidRefundBtn' || target?.id === 'captureBtn') {
            const message = target.closest('.alert').querySelector('div').innerText;
            try {
                const { xRefNum, xGatewayRefnum } = JSON.parse(message);
                const refNum = xRefNum || xGatewayRefnum;

                const tranzType = target.id === 'voidRefundBtn' ? 'void' : 'capture';

                const formData = {
                    tranzType: tranzType,
                    refnum: refNum
                };

                console.log(formData);
                sendtoserver(JSON.stringify(formData));
            } catch (error) {
                console.error("Error parsing message:", error);
            }
        }
    });
} else {
    console.warn("alertPlaceholder element not found!");
}

function formatDate(dateString) {
    const date = new Date(dateString);

    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}


async function loadSettings() {
    try {
        // Check if the user is logged in
        const authCheckResponse = await fetch('/auth_check', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const authData = await authCheckResponse.json();

        if (authData.status !== 'success') {
            console.log('User is logged out.');
            return;
        }

        // Fetch user settings
        const response = await fetch('/load_settings', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();

        if (data.status === 'success') {
            // Assign settings to variables
            userEmail = data.settings.useremail || '';
            userKey = data.settings.key || '';
            userCommand = data.settings.userCommand || '';
            userPhone = data.settings.phone || '';
            user3ds = data.settings.threeds;
            userGooglePay = data.settings.googlePay;
            userebtOnline = data.settings.ebtOnline;
            ccdevice = data.settings.ccdevice;
            transactionLogsSubHead.append(` (Key in use: ${userKey})`)
            console.log('Settings loaded successfully!', data);
        } else {
            console.log(data.message);
        }
    } catch (error) {
        console.error('Error fetching settings:', error);
    }
}





// Function to format the "exp" field
function formatExp(exp) {
    // Remove any non-numeric characters
    var formattedExp = exp.replace(/\D/g, '');

    // If the input is in "MM/YY" format, convert it to "MMYY"
    if (formattedExp.length >= 4) {
        var month = formattedExp.substring(0, 2);
        var year = formattedExp.substring(2);
        formattedExp = month + year;
    }

    return formattedExp;
}


window.onload = function () {


    (async () => {
        await loadSettings();

        if (user3ds === true) {
            console.log("threeds is true");
            enable3DS('staging', handle3DSResults);
        } else if (user3ds === false) {

        } else {

        }

        if (userGooglePay === true) {

            ckGooglePay.enableGooglePay({ amountField: "amount" });
            if (window.ApplePaySession && ApplePaySession.canMakePayments()) {
                if (ckApplePay && typeof ckApplePay.enableApplePay === 'function') {
                    ckApplePay.enableApplePay({
                        initFunction: 'apRequest.initAP',
                        amountField: 'amount'
                    });
                } else {
                    console.error("Apple Pay initialization function is missing or undefined.");
                }
            } else {
                console.error("Apple Pay not supported on this device or browser.");
                
            }
            
        } else if (userGooglePay === false) {

        } else {

        }

        if (userebtOnline === true) {


            document.getElementById("ebtOnlinebtndiv").style.display = "block";

        } else if (userebtOnline === false) {

        } else {

        }

        if (ccdevice === true) {

            document.getElementById("ccdevicebtndiv").style.display = "block";
        } else if (ccdevice === false) {

        } else {

        }
    })();

    let style = {
        'font-family': "'Inter', sans-serif",
        color: '#1f2937',
        border: '2px solid #d1d5db',
        'background-color': '#f9fafb',
        'border-radius': '8px',
        'border-width': '2px',
        'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.05)',
        transition: 'border-color 0.3s ease, box-shadow 0.3s ease',
        padding: '10px',
        'box-sizing': 'border-box',
        width: '100%',
        'overflow': 'hidden',
        'font-size': '16px',
        'font-weight': '400',
        'line-height': '28px',


    };
    let cardfocus = {
        'font-family': 'sans-serif',
        'background-color': '#fafbff',
        'border-color': '#e6e6e6',
        'border-radius': '10px',
        'border-style': 'solid',
        'border-width': '2px',
        padding: '10px',
        display: 'block',
        'box-sizing': 'border-box',
        width: '100%',
        'overflow': 'hidden',
        'font-size': '1em',
        'font-weight': '400',
        'line-height': '28px',


    };
    let cvvfocus = {
        'font-family': 'sans-serif',
        'background-color': '#fafbff',
        'border-color': '#e6e6e6',
        'border-radius': '10px',
        'border-style': 'solid',
        'border-width': '2px',
        padding: '10px',
        display: 'block',
        'box-sizing': 'border-box',
        width: '100%',
        'overflow': 'hidden',
        'font-size': '1em',
        'font-weight': '400',
        'line-height': '28px',


    };
    setIfieldStyle('card-number', style);
    setIfieldStyle('cvv', style);


};

addIfieldCallback('focus', function (data) {
    console.log(data)
});



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

        grecaptcha.ready(function () {
            grecaptcha.execute('6LfF85YqAAAAAKSObF9eWGm-WNIhz18hdNZq3KcB', { action: 'checkout' }).then(function (token) {
                formData['g-recaptcha-response'] = token; // Add reCAPTCHA token to form data           

                // Format the "exp" field
                formData['exp'] = formatExp(formData['exp']);

                formData['tranzType'] = "R";
                // Convert JSON to string for display or further processing
                var formDataJSON = JSON.stringify(formData);

                sendtoserver(formDataJSON)

            });
        });

    }, 10000,);
});

ccdevicebtn.addEventListener("click", () => {
    ccdevicebtntoggle('off');


    var formData = {};
    var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "phone"];

    fields.forEach(function (field) {
        formData[field] = document.getElementById(field).value;
    });





    formData['tranzType'] = "cloudIM";
    // Convert JSON to string for display or further processing
    var formDataJSON = JSON.stringify(formData);

    sendtoserver(formDataJSON)



});

ebtOnlinebtn.addEventListener("click", () => {
    ebtOnlinebtntoggle('off');
    setAccount("ifields_ephraimdev1f011616e4ba4f75b0bbcf26417", "tranzact", "1.0");
    getTokens(function () {
        var formData = {};
        var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "card", "exp", "cvv", "phone"];

        fields.forEach(function (field) {
            formData[field] = document.getElementById(field).value;
        });



        // Format the "exp" field
        formData['exp'] = formatExp(formData['exp']);

        formData['tranzType'] = "ebtOnlineInitiate";
        // Convert JSON to string for display or further processing
        var formDataJSON = JSON.stringify(formData);

        data = sendtoserver(formDataJSON)
    }, 10000,);
});


function showAcuPinPad(data, action) {
    // Generate the modal content
    const modalHtml = `
    <div class="modal fade" id="dynamicModal" tabindex="-1" aria-labelledby="dynamicModalLabel" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="dynamicModalLabel">Form Submission</h5>
            
          </div>
          <div class="modal-body">
            <form id="dynamicForm" method="POST" action="${action}" target="dynamicIframe">
              ${Object.keys(data)
            .map(
                (key) =>
                    `<input type="hidden" name="${key}" value="${data[key]}" />`
            )
            .join('')}
            </form>
            <iframe name="dynamicIframe" id="dynamicIframe" style="width: 100%; height: 400px; border: none;"></iframe>
          </div>
          <div class="modal-footer">
          </div>
        </div>
      </div>
    </div>
`;


    // Add the modal to the DOM
    const modalContainer = document.getElementById('dynamicModalContainer');
    modalContainer.innerHTML = modalHtml;

    // Automatically submit the form once the modal is added
    const form = document.getElementById('dynamicForm');
    form.submit();

    // Show the modal
    const modalElement = document.getElementById('dynamicModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Close the modal when the iframe is redirected
    const iframe = document.getElementById('dynamicIframe');
    const originalURL = iframe.src;
    iframe.addEventListener('load', () => {
        try {
            // Check the current URL of the iframe
            const currentURL = iframe.contentWindow.location.href;

            // Compare the current URL with the original URL
            if (currentURL !== originalURL) {
                console.log('The iframe has been redirected.');
                console.log("closing modal")
                modal.hide(); // Close the modal
            }
        } catch (error) {
            // Handle cross-origin errors (if the iframe redirects to a domain with different origin)
            console.warn('Unable to access iframe content due to cross-origin restrictions.', error);
        }
    });
}

// Listen for messages from your Flask app
window.addEventListener("message", function (event) {

    // Validate the origin of the message
    const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
    const allowedOrigin = isLocal ? 'http://127.0.0.1:5000' : 'https://app.cardknox.link';

    if (event.origin !== allowedOrigin) return;
    if (event.data.acuResponse) {
        var acuPinPadResponse = event.data.acuResponse;
        if (acuPinPadResponse.AccuResponseCode === "ACCU000") {
            console.log("Good: ", acuPinPadResponse.AccuResponseCode);
            console.log(ckResponse.xRefNum);

            var formData = {};
            var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "phone"];
            fields.forEach(function (field) {
                formData[field] = document.getElementById(field).value;
            });
            formData['tranzType'] = "ebtOnlineComplete";
            formData['refnum'] = ckResponse.xRefNum;
            var formDataJSON = JSON.stringify(formData);

            sendtoserver(formDataJSON);
        } else {
            console.log("Bad: ", acuPinPadResponse.AccuResponseCode);
            appendAlert(JSON.stringify(acuPinPadResponse), 'danger', 'on', 'on', ckRequest);
            updateUser(acuPinPadResponse);
        }
    } else {
        console.log("acuResponse is not defined.");
    }



}, false);


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
            responseStatus = data.status
            responseMessage = data.message
            console.log(responseStatus)
            if (responseStatus === "success") {
                ckRequest = data.ckRequest
                ckResponse = data.ckResponse

                if (ckResponse.xResult == "A" || ckResponse.xResult == "S") {
                    if (ckResponse.xResult == "A" && ckRequest.xCommand == "ebtonline:initiate") {
                        console.log(ckResponse);

                        // Check if the environment is local (localhost or 127.0.0.1)
                        const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';

                        const pinPadData = {
                            AccuId: ckResponse.xAccuID,
                            AccuReturnURL: isLocal ? 'http://127.0.0.1:5000/ebtresponse' : 'https://app.cardknox.link/ebtresponse',
                            AccuLanguage: 'en-US',
                        };

                        showAcuPinPad(pinPadData, ckResponse.xPinPadURL);
                    }
                    else {
                        appendAlert(JSON.stringify(ckResponse), 'success', 'on', 'on', ckRequest);
                        if (JSON.parse(serverdata).tranzType === 'void') {
                            updateUser(ckResponse, { transactionType: 'void' });
                        } else if (JSON.parse(serverdata).tranzType === 'capture') {
                            updateUser(ckResponse, { transactionType: 'capture' });
                        } else {

                            updateUser(ckResponse);
                        }
                    }

                }
                else if (ckResponse.xResult == "V") {
                    verify3DS(ckResponse)
                    appendAlert(JSON.stringify(ckResponse), 'info', 'off', 'on', ckRequest);
                }
                else {
                    appendAlert(JSON.stringify(ckResponse), 'danger', 'on', 'on', ckRequest);

                    if (JSON.parse(serverdata).tranzType === 'void') {
                        updateUser(ckResponse, { transactionType: 'void' });
                    } else if (JSON.parse(serverdata).tranzType === 'capture') {
                        updateUser(ckResponse, { transactionType: 'capture' });
                    }
                    else {
                        updateUser(ckResponse);
                    }
                }
            } else if (responseStatus === "fail") {
                appendAlert(responseMessage, 'danger', 'on', 'on', '');
                updateUser(responseMessage);
            } else {
                console.log("Unknown response status.");
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
        billingAddressRequired: false,
        billingAddressFormat: GPBillingAddressFormat.full,
    },
    shippingParameters: {
        shippingAddressRequired: false,
        shippingOptionRequired: false
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
    return {
        merchantInfo: gpRequest.merchantInfo,
        buttonOptions: gpRequest.buttonOptions,
        onGetTransactionInfo: "gpRequest.onGetTransactionInfo",
        environment: "PRODUCTION",
        billingParameters: gpRequest.billingParams,
        shippingParameters: gpRequest.shippingParameters,
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
        sbmtbtncont.textContent = "Pay with card";
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

function ccdevicebtntoggle(state) {



    if (state === 'on') {
        ccdevicebtn.disabled = false;
        ccdevicebtnspin.hidden = true;
        ccdevicebtncont.textContent = "Pay with cloudim";
        // Perform actions when the switch is turned on
        console.log('Switch is ON');
        // Add more code as needed
    } else if (state === 'off') {
        ccdevicebtn.disabled = true;
        ccdevicebtnspin.hidden = false;
        ccdevicebtncont.textContent = "Please Wait";

        // Perform actions when the switch is turned off
        console.log('Switch is OFF');
        // Add more code as needed
    } else {
        // Handle invalid state
        console.error('Invalid state. Please provide "on" or "off".');
    }
}

function ebtOnlinebtntoggle(state) {



    if (state === 'on') {
        ebtOnlinebtn.disabled = false;
        ebtOnlinebtnspin.hidden = true;
        ebtOnlinebtncont.textContent = "Pay with EBT online";
        // Perform actions when the switch is turned on
        console.log('Switch is ON');
        // Add more code as needed
    } else if (state === 'off') {
        ebtOnlinebtn.disabled = true;
        ebtOnlinebtnspin.hidden = false;
        ebtOnlinebtncont.textContent = "Please Wait";

        // Perform actions when the switch is turned off
        console.log('Switch is OFF');
        // Add more code as needed
    } else {
        // Handle invalid state
        console.error('Invalid state. Please provide "on" or "off".');
    }
}