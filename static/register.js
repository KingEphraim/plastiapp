const registerbtn = document.getElementById("registerbtn");
const message = document.getElementById("message");
const userName = document.getElementById("username");
const userEmail = document.getElementById("email");
// Validation functions
function validateUsername(username) {
    // Check if username is at least 6 alphanumeric characters
    return /^[a-zA-Z0-9]{6,}$/.test(username);
}

function validateEmail(email) {
    // Check if email is valid
    return /\S+@\S+\.\S+/.test(email);
}

registerbtn.addEventListener("click", function () {
    var formData = {};
    var fields = ["username", "password", "email"];
    var isValid = true; // Flag to check overall form validity



    fields.forEach(function (field) {
        var value = document.getElementById(field).value;
        formData[field] = value;

        // Perform validation for each field
        if (field === "username") {
            if (!validateUsername(value)) {
                isValid = false;
                message.innerText = "Please enter a Username that is at least 6 characters";
            }
        } else if (field === "email") {
            if (!validateEmail(value)) {
                isValid = false;
                message.innerText = "Please enter a valid email address.";
            }
        }
    });

    // If form is valid, proceed to send data to server
    if (isValid) {
        formData['tranzType'] = "N";
        var formDataJSON = JSON.stringify(formData);
        sendtoserver(formDataJSON);
    }
});

function sendtoserver(serverdata) {
    console.log('test')
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: serverdata,
    })
        .then(response => response.json())
        .then(data => {

            console.log(data.status);
            if (data.status == 'fail') {
                console.log(data);
                message.innerHTML = data.message;
            } if (data.status == 'success') {
                console.log(data.redirect);
                const redirectUrlWithMessage = `${data.redirect}?redirectmessage=userredirect`;
                window.location.href = redirectUrlWithMessage;
            }

        })
        .catch(error => {
            console.error('Error:', error);
        });
}