const registerbtn = document.getElementById("registerbtn");
const message = document.getElementById("message");
const userEmail = document.getElementById("username");

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
registerbtn.addEventListener("click", function () {
    const currentemail = userEmail.value;
    if (validateEmail(currentemail)) {
        
        var formData = {};
        var fields = ["username", "password"];
        fields.forEach(function (field) {
            formData[field] = document.getElementById(field).value;
        });
        formData['tranzType'] = "N";
        var formDataJSON = JSON.stringify(formData);
        sendtoserver(formDataJSON)

    } else {
        message.innerHTML = "Invalid email address";
    }


});

function sendtoserver(serverdata) {

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(serverdata),
    })
        .then(response => response.json())
        .then(data => {

            console.log(data.status);
            if (data.status == 'fail') {
                console.log(data);
                message.innerHTML = data.message;
            } if (data.status == 'success') {
                console.log(data.redirect);
                window.location.href = data.redirect;
            }

        })
        .catch(error => {
            console.error('Error:', error);
        });
}