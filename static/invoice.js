$(document).ready(function() {    
    $('#invoiceTable').DataTable({
        "ajax": {
            "url": "/listInvoices",  
            "dataSrc": ""    
        },
        "columns": [
            { "data": "invoice" },            
            { "data": "customer_name" },
            { "data": "email" },
            { "data": "fullAddress" },
            { "data": "phone" },
            { "data": "items" },
            { "data": "payments" },
            { "data": "total" },            
            { "data": "status" },
        ],
        "scrollX": true, 
    });
});

function createInvoice(url, data) {
    // Send JSON data using fetch
    return fetch(url, {
        method: 'POST', // or 'PUT', depending on your server-side requirements
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data), // Convert the JavaScript object to JSON
    })
    .then(response => response.json()) // Parse the response as JSON
    .then(result => {
        console.log('Success:', result); // Handle the success response
        return result; // Return the result for further use
    })
    .catch(error => {
        console.error('Error:', error); // Handle any errors
        throw error; // Re-throw the error to allow handling outside
    });
}


