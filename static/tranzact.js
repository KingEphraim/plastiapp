const button = document.getElementById("sbmtbtn");
button.addEventListener("click", () => {
    
    var formData = {};
    var fields = ["name", "email", "address", "city", "state", "zip", "invoice", "comments", "amount", "card", "exp", "cvv"];
    
    fields.forEach(function(field) {
        formData[field] = document.getElementById(field).value;
    });

    // Convert JSON to string for display or further processing
    var formDataJSON = JSON.stringify(formData);

    // Display JSON in the console (for testing)
    console.log(formDataJSON);


    fetch('/sendtocardknox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formDataJSON)
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));

});