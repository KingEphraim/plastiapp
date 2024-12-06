document.getElementById("requestPasswordResetBtn").addEventListener("click", function () {
    // Get the email value
    const emailInput = document.getElementById("email");
    const email = emailInput.value;

    // Get the button element
    const requestPasswordResetBtn = document.getElementById("requestPasswordResetBtn");

    // Disable the button
    requestPasswordResetBtn.disabled = true;

    if (!email) {
        alert("Please enter an email.");
        // Re-enable the button and return early
        requestPasswordResetBtn.disabled = false;
        return;
    }

    // Send the request to the server
    fetch(`/reset_password_request`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json(); // Parse JSON from the response
    })
    .then(data => {
        // Handle the response data
        if (data.status === 'success') {
            alert(data.message || "Password reset link has been sent to your email.");
            // Clear the input field
            emailInput.value = "";
        } else {
            alert(`Error: ${data.message || "Unable to process your request."}`);
        }
    })
    .catch(error => {
        // Handle errors
        console.error("Error during password reset request:", error);
        alert("An error occurred while processing your request. Please try again later.");
    })
    .finally(() => {
        // Re-enable the button after processing
        requestPasswordResetBtn.disabled = false;
    });
});
