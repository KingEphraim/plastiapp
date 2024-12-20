const loginBtn = document.getElementById("loginbtn");
const message = document.getElementById("message");
const username = document.getElementById("username");
const password = document.getElementById("password");

loginBtn.addEventListener("click", function () {
    const formData = {
        username: username.value,
        password: password.value
    };

    sendDataToServer(formData);
});

function sendDataToServer(formData) {
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.status);
        if (data.status === 'fail') {
            message.innerText = data.message;
            // Optionally, show a "Forgot your password?" link if login fails
            const forgotPasswordLink = document.getElementById('forgot-password-link');
            forgotPasswordLink.style.display = 'block';
        } else if (data.status === 'success') {
            // Redirect to success page or perform other actions
            console.log(data.message);
            window.location.href = '/dashboard'; // Redirect to success page
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
