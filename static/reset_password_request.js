document.getElementById("requestPasswordResetBtn").addEventListener("click", function() {
    // Get the password value
    const email = document.getElementById("email").value;

    if (!email) {
        alert("Please enter a email.");
        return;
    }


    
    fetch(`/reset_password_request`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: email })
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
