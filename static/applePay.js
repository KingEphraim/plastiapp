// Utility functions
function calculateTotalAmount(lineItems) {
    return lineItems.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0);
}

function roundTo(number, decimalPlaces) {
    if (isNaN(number)) {
        console.error("Invalid number:", number);
        return 0; // or return number itself, depending on your requirements
    }
    // Ensure number is a valid number type before calling toFixed
    const validNumber = parseFloat(number);
    if (isNaN(validNumber)) {
        console.error("Invalid number after parsing:", number);
        return 0; // or handle accordingly
    }
    return parseFloat(validNumber.toFixed(decimalPlaces));
}



// onGetTransactionInfo function
function onGetTransactionInfo() {
    const lineItems = [
        { label: "Subtotal", type: "final", amount: amount.value },
        { label: "Credit Card Fee", type: "final", amount: 0 },
        { label: "Estimated Tax", type: "final", amount: 0 },
    ];

    const totalAmount = calculateTotalAmount(lineItems);
    apRequest.totalAmount = roundTo(totalAmount, 2);

    return {
        lineItems,
        total: {
            type: "final",
            label: "Total",
            amount: totalAmount,
        },
    };
}

// apButtonLoaded function
function apButtonLoaded(resp) {
    if (!resp) return;
    if (resp.status === iStatus.success) {
        //showHide(this.buttonOptions.buttonContainer, true);
        // showHide("lbAPPayload", true);
    } else if (resp.reason) {
        alert(resp.reason);
    }
}

// onValidateMerchant function
function onValidateMerchant() {
    return new Promise((resolve, reject) => {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "https://api.cardknox.com/applepay/validate");
            xhr.onload = function () {
                if (this.status >= 200 && this.status < 300) {
                    console.log("validateApplePayMerchant", JSON.stringify(xhr.response));
                    resolve(xhr.response);
                } else {
                    console.log("validateApplePayMerchant", JSON.stringify(xhr.response), this.status);
                    reject({ status: this.status, statusText: xhr.response });
                }
            };
            xhr.onerror = function () {
                console.error("validateApplePayMerchant", xhr.statusText, this.status);
                reject({ status: this.status, statusText: xhr.statusText });
            };
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send();
        } catch (err) {
            setTimeout(function () {
                console.log("getApplePaySession error: " + exMsg(err));
            }, 100);
        }
    });
}

// onPaymentAuthorize function
function onPaymentAuthorize(applePayload, totalAmount) {
    return new Promise(function (resolve, reject) {
        try {
            const paymentToken = applePayload.token.paymentData;
            const encodedToken = window.btoa(JSON.stringify(paymentToken));

            var formData = {};
            var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "phone"];
            fields.forEach(function (field) {
                formData[field] = document.getElementById(field).value;
            });
            formData['tranzType'] = "AP";
            formData['aptoken'] = encodedToken;
            formData['totalAmount'] = totalAmount;

            var formDataJSON = JSON.stringify(formData);

            sendtoserver(formDataJSON).then(function (response) {
                resolve(response);
            }).catch(function (error) {
                reject(error);
            });
        } catch (err) {
            reject(err);
        }
    });
}

// Main AP request object
const apRequest = {
    buttonOptions: {
        buttonContainer: "ap-container",
        buttonColor: APButtonColor.black,
        buttonType: APButtonType.pay,
    },

    // Init function
    initAP: function () {
        return {
            buttonOptions: this.buttonOptions,
            merchantIdentifier: "merchant.cardknox.com",
            requiredBillingContactFields: ['postalAddress', 'name', 'phone', 'email'],
            requiredShippingContactFields: ['postalAddress', 'name', 'phone', 'email'],
            onGetTransactionInfo: "onGetTransactionInfo", // Function name as a string
            onValidateMerchant: "onValidateMerchant", // Function name as a string
            onPaymentAuthorize: "onPaymentAuthorize", // Function name as a string
            onAPButtonLoaded: "apButtonLoaded", // Function name as a string
            isDebug: false,
        };
    },
};