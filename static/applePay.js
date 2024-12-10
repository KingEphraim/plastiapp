const apRequest = {
    buttonOptions: {
        buttonContainer: "ap-container",
        buttonColor: APButtonColor.black,
        buttonType: APButtonType.pay
    },
    
    initAP: function() {
        return {
            buttonOptions: this.buttonOptions,
            merchantIdentifier: "merchant.cardknox.com",
            requiredBillingContactFields: ['postalAddress', 'name', 'phone', 'email'],
            requiredShippingContactFields: ['postalAddress', 'name', 'phone', 'email'],
            onGetTransactionInfo: "apRequest.onGetTransactionInfo",
            onGetShippingMethods: "apRequest.onGetShippingMethods",
            onShippingContactSelected: "apRequest.onShippingContactSelected",
            onShippingMethodSelected: "apRequest.onShippingMethodSelected",
            onPaymentMethodSelected: "apRequest.onPaymentMethodSelected",
            onValidateMerchant: "apRequest.onValidateMerchant",
            onPaymentAuthorize: "apRequest.onPaymentAuthorize",
            onPaymentComplete: "apRequest.onPaymentComplete",
            onAPButtonLoaded: "apRequest.apButtonLoaded",
            isDebug: true
        };
    },
    validateApplePayMerchant: function (url) {
        return new Promise(function (resolve, reject) {
            try {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', "https://api.cardknox.com/applepay/validate");
                xhr.onload = function () {
                    if (this.status >= 200 && this.status < 300) {
                        resolve(xhr.response);
                    } else {
                        reject({
                            status: this.status,
                            statusText: xhr.response
                        });
                    }
                };
                xhr.onerror = function () {
                    reject({
                        status: this.status,
                        statusText: xhr.statusText
                    });
                };
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.send(JSON.stringify({ validationUrl: url}));
            } catch (err) {
                setTimeout(function () { alert("getApplePaySession error: " + exMsg(err)) }, 100);
            }
        });
    },
    authorize: function(applePayload, totalAmount) {
        return new Promise(function (resolve, reject) {      

            try {
                //paymentToken = paymentResponse.paymentData.paymentMethodData.tokenizationData.token;
                //encodedToken = window.btoa(paymentToken);
                //console.log(JSON.stringify({ paymentResponse, encodedToken }));
                var formData = {};
                var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "phone"];
                fields.forEach(function (field) {
                    formData[field] = document.getElementById(field).value;
                });
                formData['tranzType'] = "AP";
                formData['aptoken'] = applePayload;
                formData['totalAmount'] = totalAmount;
                var formDataJSON = JSON.stringify(formData);
                sendtoserver(formDataJSON)
                resolve()
            } catch (err) {
                reject(err);
            }

        });
    }
}