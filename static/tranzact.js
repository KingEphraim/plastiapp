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
    getTokens(function () {
        var formData = {};
        var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "card", "exp", "cvv", "phone"];

        fields.forEach(function (field) {
            formData[field] = document.getElementById(field).value;
        });

        // Convert JSON to string for display or further processing
        var formDataJSON = JSON.stringify(formData);

        // Display JSON in the console (for testing)
        // console.log(formDataJSON);
        // appendAlert(formDataJSON, 'success');

        fetch('/sendtocardknox', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formDataJSON)
        })
            .then(response => response.json())
            .then(data => {
                if (data.xResult == "A") {
                    appendAlert(JSON.stringify(data), 'success');
                } else {
                    appendAlert(JSON.stringify(data), 'info');
                }
            })
            .catch(error => console.error(error));
    }, 30000,);
});






