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
const alertPlaceholder = document.getElementById('TransactionLogsPlaceholder')
const modalElement = new bootstrap.Modal(document.getElementById('userNotificationModal'));
const notificationCardHeader = document.getElementById("userNotificationCardHeader");
const notificationCardHeaderP = document.getElementById("userNotificationCardHeaderP");
const notificationCardBodyH = document.getElementById("userNotificationCardBodyH");
const notificationCardBodyP = document.getElementById("userNotificationCardBodyP");


function updateUser(serverData) {
    notificationCardHeader.className = "card-header bg-success text-white text-center py-4";
    notificationCardHeaderP.innerText = "";
    notificationCardBodyH.innerText = "";
    notificationCardBodyP.innerText = "";
    document.getElementById("orderNumber").textContent = "0";
    document.getElementById("amountPaid").textContent = "0";
    document.getElementById("date").textContent  = "0";
    switch (serverData.xResult) {
        case 'A':
            console.log("xResult is A");
            notificationCardHeader.className = "card-header bg-success text-white text-center py-4";
            notificationCardHeaderP.innerText = "Transaction Approved";
            notificationCardBodyH.innerText = "Thank you for your purchase!";
            notificationCardBodyP.innerText = "Your payment has been processed successfully.";
            modalElement.show();
            break;
        case 'E':
            console.log("xResult is E");
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
            notificationCardHeader.className = "card-header bg-success text-white text-center py-4";
            notificationCardHeaderP.innerText = "Transaction Approved";
            notificationCardBodyH.innerText = "Thank you for your purchase!";
            notificationCardBodyP.innerText = "Your payment has been processed successfully.";
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
    }

    if (serverData.xRefNum || serverData.xGatewayRefnum) {
        document.getElementById("orderNumber").textContent = serverData.xRefNum || serverData.xGatewayRefnum;
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


}

function formatDate(dateString) {
    const date = new Date(dateString);

    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Append alert to alertPlaceholder
const appendAlert = (message, type, ccDeviceToggle = 'on') => {
    const wrapper = document.createElement('div');
    wrapper.className = `alert alert-${type} alert-dismissible`;
    wrapper.role = 'alert';
    wrapper.innerHTML = `
        <div>${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        ${shouldShowVoidButton(message) ? '<button type="button" class="btn btn-warning" id="voidRefundBtn">Void/Refund</button>' : ''}
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
};



// Helper function to determine if the void/refund button should be shown
const shouldShowVoidButton = (message) => {
    return /"xResult":"[AS]"/.test(message) && /xRefNum|xGatewayRefnum/.test(message);
};

// Event listener for void/refund button clicks
if (alertPlaceholder) {
    alertPlaceholder.addEventListener('click', ({ target }) => {
        if (target?.id === 'voidRefundBtn') {
            const message = target.closest('.alert').querySelector('div').innerText;
            try {
                const { xRefNum, xGatewayRefnum } = JSON.parse(message);
                const refNum = xRefNum || xGatewayRefnum;

                const formData = {
                    tranzType: "void",
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

// Function to load settings from the server
async function loadSettings() {
    try {
        const response = await fetch('/load_settings', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();

        if (data.status === 'success') {
            // Assign settings to variables
            userEmail = data.settings.useremail || '';
            userKey = data.settings.key || '';
            userCommand = data.settings.userCommand || '';
            userPhone = data.settings.phone || '';
            user3ds = data.settings.threeds;
            ccdevice = data.settings.ccdevice;



            console.log('Settings loaded successfully!', data);
        } else {
            console.log(data.message);
        }
    } catch (error) {
        console.error(error);
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
    ckGooglePay.enableGooglePay({ amountField: "amount" });

    (async () => {
        await loadSettings();
        console.log(userEmail, userKey, userCommand, userPhone, user3ds, ccdevice);

        if (user3ds === true) {
            console.log("threeds is true");
            enable3DS('staging', handle3DSResults);
        } else if (user3ds === false) {
            console.log("threeds is false");
        } else {
            console.log("threeds is neither true nor false");
        }

        if (ccdevice === true) {
            console.log("ccdevice is true");
            document.getElementById("ccdevicebtndiv").style.display = "block";
        } else if (ccdevice === false) {
            console.log("ccdevice is false");
        } else {
            console.log("ccdevice is neither true nor false");
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



        // Format the "exp" field
        formData['exp'] = formatExp(formData['exp']);

        formData['tranzType'] = "R";
        // Convert JSON to string for display or further processing
        var formDataJSON = JSON.stringify(formData);

        sendtoserver(formDataJSON)


    }, 10000,);
});

ccdevicebtn.addEventListener("click", () => {
    ccdevicebtntoggle('off');


    var formData = {};
    var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "phone"];

    fields.forEach(function (field) {
        formData[field] = document.getElementById(field).value;
    });





    formData['tranzType'] = "sessioninitiate";
    // Convert JSON to string for display or further processing
    var formDataJSON = JSON.stringify(formData);

    sendtoserver(formDataJSON)



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
                updateUser(data);
            }
            else if (data.xResult == "S") {
                appendAlert(JSON.stringify(data), 'info', 'off');
                pollDeviceSession(data.xSessionId)
            }
            else if (data.xResult == "V") {
                verify3DS(data)
                appendAlert(JSON.stringify(data), 'info');
            }
            else {
                appendAlert(JSON.stringify(data), 'danger');
                updateUser(data);
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

function pollDeviceSession(sessionid) {

    const formData = {
        tranzType: "polldevicesession",
        sessionid: sessionid
    };

    function poll() {
        fetch('/sendtocardknox', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Response data:", data); // Log the entire response

                // Check if data has the success flag and xSessionStatus
                if (data && data.xResult == 'S' && data.xSessionStatus) {
                    const status = data.xSessionStatus;
                    if (status === "INITIATING" || status === "PROCESSING") {

                        console.log(`Status: ${status}. Polling again in 1 second...`);
                        appendAlert(JSON.stringify(data), 'info', 'off');

                        setTimeout(poll, 1000); // Poll every 1 second after the initial delay
                    } else if (status === "COMPLETED") {
                        console.log(`Final Status: ${status}`);
                        appendAlert(JSON.stringify(data), 'success');
                        updateUser(data);
                    } else if (status === "ERROR" || status === "TIMEOUT" || status === "USER_CANCELLED" || status === "API_CANCELLED") {
                        console.log(`Final Status: ${status}`);
                        appendAlert(JSON.stringify(data), 'danger');
                        updateUser(data);
                    } else {
                        console.log(`Unknown Status: ${status}`);
                    }
                } else {
                    console.error("Failed to get a valid response or success flag.");
                }
            })
            .catch(error => console.error('Polling error:', error));
    }

    // Start polling after an initial 6-second delay
    setTimeout(poll, 5000);
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