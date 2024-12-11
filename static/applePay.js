const apRequest = {
    buttonOptions: {
        buttonContainer: "ap-container",
        buttonColor: APButtonColor.black,
        buttonType: APButtonType.pay
    },
    onGetTransactionInfo: function () {

        const lineItems = [
            {
                label: "Subtotal",
                type: "final",
                amount: amount.value,
            },
            {
                label: "Credit Card Fee",
                amount: roundTo(0.0275 * amount.value, 2),
                type: "final",
            },
            {
                label: "Estimated Tax",
                amount: roundTo(0.07 * amount.value, 2),
                type: "final",
            },
        ];
        finalPrice = 0;
        lineItems.forEach((item) => {
            finalPrice += parseFloat(item.amount) || 0;
        });
        apRequest.totalAmount = roundTo(finalPrice, 2);
        return {
            lineItems: lineItems,
            total: {
                type: "final",
                label: "Total",
                amount: finalPrice,
            },
        };

    },

    apButtonLoaded: function (resp) {
        if (!resp) return;
        if (resp.status === iStatus.success) {
            //showHide(this.buttonOptions.buttonContainer, true);
            // showHide("lbAPPayload", true);
        } else if (resp.reason) {
            alert(resp.reason);
        }
    },

    initAP: function () {
        return {
            buttonOptions: this.buttonOptions,
            merchantIdentifier: "merchant.cardknox.com",
            requiredBillingContactFields: ['postalAddress', 'name', 'phone', 'email'],
            requiredShippingContactFields: ['postalAddress', 'name', 'phone', 'email'],
            onGetTransactionInfo: "apRequest.onGetTransactionInfo",
            onValidateMerchant: "apRequest.onValidateMerchant",
            onPaymentAuthorize: "apRequest.onPaymentAuthorize",
            onAPButtonLoaded: "apRequest.apButtonLoaded",
            isDebug: true
        };
    },

    onValidateMerchant: function () {
        return new Promise((resolve, reject) => {
            try {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "https://api.cardknox.com/applepay/validate");
                xhr.onload = function () {
                    if (this.status >= 200 && this.status < 300) {
                        console.log(
                            "validateApplePayMerchant",
                            JSON.stringify(xhr.response)
                        );
                        resolve(xhr.response);
                    } else {
                        console.log(
                            "validateApplePayMerchant",
                            JSON.stringify(xhr.response),
                            this.status
                        );
                        reject({
                            status: this.status,
                            statusText: xhr.response,
                        });
                    }
                };
                xhr.onerror = function () {
                    console.error(
                        "validateApplePayMerchant",
                        xhr.statusText,
                        this.status
                    );
                    reject({
                        status: this.status,
                        statusText: xhr.statusText,
                    });
                };
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.send();
            } catch (err) {
                setTimeout(function () {
                    console.log("getApplePaySession error: " + exMsg(err));
                }, 100);
            }
        });
    },

    onPaymentAuthorize: function (applePayload, totalAmount) {
        return new Promise(function (resolve, reject) {
            try {     
                paymentToken = applePayload.token.paymentData;
                console.log(paymentToken);
                encodedToken = window.btoa(JSON.stringify(paymentToken));
                console.log(encodedToken);
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
};
