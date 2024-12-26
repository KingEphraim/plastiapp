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



