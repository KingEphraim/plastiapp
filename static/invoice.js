      
function createInvoice(url, data) {
    // Send JSON data using fetch
    fetch(url, {
        method: 'POST', // or 'PUT', depending on your server-side requirements
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data), // Convert the JavaScript object to JSON
    })
    .then(response => response.json()) // Parse the response as JSON
    .then(result => {
        console.log('Success:', result); // Handle the success response
    })
    .catch(error => {
        console.error('Error:', error); // Handle any errors
    });
}

