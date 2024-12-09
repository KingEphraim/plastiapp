
const apRequest = {
    buttonOptions: {
        buttonContainer: "ap-container",
        buttonColor: APButtonColor.black,
        buttonType: APButtonType.pay
    },
    totalAmount: null,
    taxAmt: null,
    shippingMethod: null,
    creditType: null,
    getTransactionInfo: function (taxAmt, shippingMethod, creditType) {
        try {
            this.shippingMethod = shippingMethod || this.shippingMethod || {
                "label": "Free Shipping",
                "amount": "0.00",
                "type": "final"
            };
            this.taxAmt = roundToNumber(taxAmt, 4) || this.taxAmt || 0.07;
            this.creditType = creditType || this.creditType;
            const amt = getAmount();
            const lineItems = [
                {
                    "label": "Subtotal",
                    "type": "final",
                    "amount": amt
                },
                this.shippingMethod
            ];
            if (this.creditType === "credit") {
                lineItems.push({
                    "label": "Credit Card Fee",
                    "amount": roundTo(0.0275 * amt, 2),
                    "type": "final"
                });
            }
            lineItems.push({
                "label": "Estimated Tax",
                "amount": roundTo(this.taxAmt * amt, 2),
                "type": "final"
            });
            let totalAmt = 0;
            lineItems.forEach((item) => {
                totalAmt += parseFloat(item.amount) || 0;
            });
            totalAmt = roundTo(totalAmt, 2);
            this.totalAmount = totalAmt;

            return {
                'lineItems': lineItems,
                total: {
                    type: 'final',
                    label: 'Total',
                    amount: totalAmt,
                }
            };
        } catch (err) {
            console.error("getTransactionInfo error ", exMsg(err));
        }
    },
    onGetTransactionInfo: function () {
        try {
            return this.getTransactionInfo();
        } catch (err) {
            console.error("onGetTransactionInfo error ", exMsg(err));
        }
    },
    onGetShippingMethods: function () {
        return [
            {
                label: 'Free Shipping',
                amount: '0.00',
                identifier: 'free',
                detail: 'Delivers in five business days',
            },
            {
                label: 'Express Shipping',
                amount: '5.00',
                identifier: 'express',
                detail: 'Delivers in two business days',
            },
        ];
    },
    onShippingContactSelected: function (shippingContact) {
        const self = this;
        return new Promise((resolve, reject) => {
            try {
                console.log("shippingContact", JSON.stringify(shippingContact));
                let taxAmt = 0.1;
                const newShippingMethods = [
                    {
                        label: 'Free Shipping',
                        amount: '0.00',
                        identifier: 'free',
                        detail: 'Delivers in five business days',
                    }
                ];
                if (shippingContact && shippingContact.administrativeArea) {
                    if (shippingContact.administrativeArea === "NY") {
                        taxAmt = 0.0875;
                        newShippingMethods.push(
                            {
                                label: 'Overnight Shipping',
                                amount: '10.00',
                                identifier: 'overnight',
                                detail: 'Delivers in one business days',
                            }
                        );
                    } else if (shippingContact.administrativeArea === "NJ") {
                        taxAmt = 0.07;
                        newShippingMethods.push(
                            {
                                label: 'Express Shipping',
                                amount: '5.00',
                                identifier: 'express',
                                detail: 'Delivers in two business days',
                            }
                        );
                    }
                }
                const resp = self.getTransactionInfo(taxAmt, newShippingMethods[0]);
                resp.shippingMethods = newShippingMethods;
                resolve(resp);
            } catch (err) {
                const apErr = {
                    code: "-101",
                    contactField: "",
                    message: exMsg(err)
                }
                console.error("onShippingContactSelected error.", exMsg(err));
                reject({ errors: [err] });
            }
        })
    },
    onShippingMethodSelected: function (shippingMethod) {
        const self = this;
        return new Promise(function (resolve, reject) {
            try {
                console.log("shippingMethod", JSON.stringify(shippingMethod));
                const resp = self.getTransactionInfo(null, shippingMethod);
                resolve(resp);
            } catch (err) {
                const apErr = {
                    code: "-102",
                    contactField: "",
                    message: exMsg(err)
                }
                console.error("onShippingMethodSelected error.", exMsg(err));
                reject({ errors: [err] });
            }
        })
    },
    onPaymentMethodSelected: function (paymentMethod) {
        const self = this;
        return new Promise((resolve, reject) => {
            try {
                console.log("paymentMethod", JSON.stringify(paymentMethod));
                const resp = self.getTransactionInfo(null, null, paymentMethod.type);
                resolve(resp);
            } catch (err) {
                const apErr = {
                    code: "-102",
                    contactField: "",
                    message: exMsg(err)
                }
                console.error("onPaymentMethodSelected error.", exMsg(err));
                reject({ errors: [err] });
            }
        })
    },
    validateApplePayMerchant: function () {
        return new Promise((resolve, reject) => {
            try {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "https://api.cardknox.com/applepay/validate");
                xhr.onload = function () {
                    if (this.status >= 200 && this.status < 300) {
                        console.log("validateApplePayMerchant", JSON.stringify(xhr.response));
                        resolve(xhr.response);
                    } else {
                        console.error("validateApplePayMerchant", JSON.stringify(xhr.response), this.status);
                        reject({
                            status: this.status,
                            statusText: xhr.response
                        });
                    }
                };
                xhr.onerror = function () {
                    console.error("validateApplePayMerchant", xhr.statusText, this.status);
                    reject({
                        status: this.status,
                        statusText: xhr.statusText
                    });
                };
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.send();
            } catch (err) {
                setTimeout(function () { console.log("getApplePaySession error: " + exMsg(err)) }, 100);
            }
        });
    },
    onValidateMerchant: function () {
        return new Promise((resolve, reject) => {
            try {
                this.validateApplePayMerchant()
                    .then((response) => {
                        try {
                            console.log(response);
                            resolve(response);
                        } catch (err) {
                            console.error("validateApplePayMerchant exception.", JSON.stringify(err));
                            reject(err);
                        }
                    })
                    .catch((err) => {
                        console.error("validateApplePayMerchant error.", JSON.stringify(err));
                        reject(err);
                    });
            } catch (err) {
                console.error("onValidateMerchant error.", JSON.stringify(err));
                reject(err);
            }
        });
    },
    authorize: function (applePayload, totalAmount) {
        return new Promise(function (resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "https://<your domain>/<path to handle authorization>");
            xhr.onload = function () {
                if (this.status >= 200 && this.status < 300) {
                    resolve(xhr.response);
                } else {
                    reject({
                        status: this.status,
                        statusText: xhr.statusText
                    });
                }
            };
            xhr.onerror = function () {
                reject({
                    status: this.status,
                    statusText: xhr.statusText
                });
            };
            const data = {
                amount: totalAmount,
                payload: applePayload
            };
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    },
    onPaymentAuthorize: function (applePayload) {
        return new Promise((resolve, reject) => {
            try {
                this.authorize(applePayload, this.totalAmount)
                    .then((response) => {
                        try {
                            console.log(response);
                            const resp = JSON.parse(response);
                            if (!resp)
                                throw "Invalid response: " + response;
                            if (resp.xError) {
                                throw resp;
                            }
                            resolve(response);
                        } catch (err) {
                            throw err;
                            // reject(err);
                        }
                    })
                    .catch((err) => {
                        console.error("authorizeAPay error.", JSON.stringify(err));
                        apRequest.handleAPError(err);
                        reject(err);
                    });
            } catch (err) {
                console.error("onPaymentAuthorize error.", JSON.stringify(err));
                apRequest.handleAPError(err);
                reject(err);
            }
        });
    },
    onPaymentComplete: function (paymentComplete) {
        if (paymentComplete.response) { //Success
            const resp = JSON.parse(paymentComplete.response);
            if (resp.xRefNum) {
                setAPPayload("Thank you for your order:(" + resp.xRefNum + ")");
            } else {
                setAPPayload("Thank you for your order.");
            }
        } else if (paymentComplete.error) {
            console.error("onPaymentComplete", exMsg(paymentComplete.error));
            handleAPError(paymentComplete.error);
        }
    },
    handleAPError: function (err) {
        if (err && err.xRefNum) {
            setAPPayload("There was a problem with your order:(" + err.xRefNum + ")");
        } else {
            setAPPayload("There was a problem with your order:" + exMsg(err));
        }
    },
    initAP: function () {
        return {
            buttonOptions: this.buttonOptions,
            merchantIdentifier: "<Your Apple Merchant ID>",
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
    apButtonLoaded: function (resp) {
        if (!resp) return;
        if (resp.status === iStatus.success) {
            showHide(this.buttonOptions.buttonContainer, true);
            showHide("lbAPPayload", true);
        } else if (resp.reason) {
            console.log(resp.reason);
        }
    }
};

function setAPPayload(value) {
    const apTxt = document.getElementById('ap-payload');
    apTxt.value = value;
    showHide(apTxt, value);
}

function showHide(elem, toShow) {
    if (typeof (elem) === "string") {
        elem = document.getElementById(elem);
    }
    if (elem) {
        toShow ? elem.classList.remove("hidden") : elem.classList.add("hidden");
    }
}
function getAmount() {
    return roundToNumber(document.getElementById("amount").value || "0", 2);
}
