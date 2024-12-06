document.getElementById("resetPasswordBtn").addEventListener("click", function() {
    // Get the password value
    const password = document.getElementById("password").value;

    if (!password) {
        alert("Please enter a password.");
        return;
    }

    // Get the token from the URL path
    const pathParts = window.location.pathname.split('/');
    const token = pathParts[pathParts.length - 1];  // The token is the last part of the URL path

    if (!token) {
        alert("Invalid token.");
        return;
    }

    // Send the password to the backend
    fetch(`/reset_password/${token}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ password: password })
    })
    .then(response => {        
        // If the server responds with a redirect (3xx status), handle it here
        if (response.redirected) {
            window.location.href = response.url;  // Redirect to the URL sent by Flask
        } else {
            return response.json();
        }
    })
    .then(data => {
        // Handle success/failure if the server doesn't perform a redirect
        if (data && data.status === "fail") {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error resetting password:", error);
        alert("An error occurred. Please try again.");
    });
});
