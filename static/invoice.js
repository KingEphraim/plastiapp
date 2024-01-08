       // Fetch and display all invoices when the page loads
       document.addEventListener('DOMContentLoaded', function () {
        fetch('/invoices')
            .then(response => response.json())
            .then(data => displayInvoices(data.invoices));
    });

    function displayInvoices(invoices) {
      var invoicesList = document.getElementById('invoicesList');

      // Clear existing content
      invoicesList.innerHTML = '';

      // Display each invoice in the list
      invoices.forEach(function (invoice, index) {
          var listItem = document.createElement('li');
          listItem.innerHTML = `Customer: ${invoice.customer_name}, Amount: ${invoice.amount},Email: ${invoice.email}
              <button type="button" onclick="deleteInvoice(${index})">Delete</button>`;
          invoicesList.appendChild(listItem);
      });
  }

    function createInvoice() {
        var form = document.getElementById('invoiceForm');
        var formData = new FormData(form);

        fetch('/create_invoice', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Fetch and update the list of invoices
                fetch('/invoices')
                    .then(response => response.json())
                    .then(data => displayInvoices(data.invoices));
            }
        });
    }

    function deleteInvoice(index) {
      fetch('/delete_invoice/' + index, {
          method: 'DELETE',
      })
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              // Fetch and update the list of invoices
              fetch('/invoices')
                  .then(response => response.json())
                  .then(data => displayInvoices(data.invoices));
          }
      });
  }