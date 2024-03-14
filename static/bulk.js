$(document).ready(function () {


  $('#bulkform').submit(function (event) {
    event.preventDefault(); // prevent default form submission
    $("#submit_button").prop("disabled", true);
    var submitRequested = false; // Flag to track if submission has been requested
    // Assuming you have the CSV file input element with id 'bulkcsv'
    var csvfile = $('#bulkcsv')[0].files[0];

    if (csvfile && (csvfile.type === 'text/csv' || csvfile.name.endsWith('.csv'))) {
      var reader = new FileReader();

      reader.onload = function (e) {
        var csvContent = e.target.result;
        var lines = csvContent.split('\n');
        var headers = lines[0].split(',');

        // Check if 'xcardnum' column exists

        if (headers.some(header => header.toLowerCase() === 'xcardnum')) {

          $('#staticBackdrop').modal('show');

          // Handle 'ccdatacancel' button click
          $('#ccdatacancel').click(function () {
            $('#status').text("Canceled.");
            submitRequested = true; // Set the flag to indicate submission has been requested
            $("#submit_button").prop("disabled", false);
          });

          // Handle 'ccdatayes' button click
          $('#ccdatayes').click(function () {
            $('#status').text("Do not use this tool with raw card numbers.");
            submitRequested = true; // Set the flag to indicate submission has been requested
            $("#submit_button").prop("disabled", false);
          });

          // Handle 'ccdatano' button click
          $('#ccdatano').click(function () {
            if (!submitRequested) { // Check if submission has not been requested
              submitcsvdata(csvContent);
              submitRequested = true; // Set the flag to indicate submission has been requested
            }
          });
        } else {
          submitcsvdata(csvfile);
        }
      };
      reader.readAsText(csvfile);
    } else {
      $('#status').text("Please upload a CSV file.");
      $("#submit_button").prop("disabled", false);
    }


  });

  $("#refreshbutton").click(function () {
    try {
      getbatchresponsedata(responsegroupid);
    }
    catch (err) {
      console.log(err)
    }

  });
});








function submitcsvdata(csvfile) {
  var blob = new Blob([csvfile], { type: 'text/csv' });
  var formData = new FormData();
  formData.append('url', $('#urldata').val());
  formData.append('email', $('#email').val());
  formData.append('csvfile', blob, 'data.csv'); // Append the Blob object as a file to the form data
  $.ajax({
    type: 'POST',
    url: '/bulk_csv',
    data: formData,
    contentType: false,
    processData: false,
    success: function (response) {
      console.log(response)
      $('#response').html(response); // display response message
      $('#status').text(response);
      $('#bulkcsv').val(null);
      $("#submit_button").prop("disabled", false);
      responsejson = JSON.parse(response);
      responsegroupid = responsejson.groupid;
      console.log(responsegroupid)
      getbatchresponsedata(responsegroupid);
    },
    error: function (xhr, status, error) {
      // Handle error
      $('#status').text("Error: " + error);
      $("#submit_button").prop("disabled", false);
    }


  });
}

function getbatchresponsedata(groupid) {
  $.ajax({
    url: '/dynamobatchdata', // Replace with your Flask app's endpoint URL
    type: 'GET',
    data: {
      groupid: groupid // Replace paramName with the actual parameter name and paramValue with the value you want to send
    },
    success: function (response) {
      // Handle the response from the server
      console.log(JSON.parse(response));
      // Process the data or update the DOM accordingly
      addtotable(response)
    },
    error: function (error) {
      // Handle any errors that occur during the AJAX request
      console.log(error);
    }
  });
}


function addtotable(transactionlist) {
  try {
    // Check if transactionlist is a valid JSON string
    if (typeof transactionlist !== 'string') {
      throw new Error('Input is not a string.');
    }

    // Parse JSON data into an array of objects
    var data = JSON.parse(transactionlist);

    // Retrieve all unique field names from all objects
    var fieldNames = [];
    data.forEach(function (obj) {
      Object.keys(obj).forEach(function (key) {
        if (!fieldNames.includes(key)) {
          fieldNames.push(key);
        }
      });
    });

    // Create the table columns
    var columns = fieldNames.map(function (fieldName) {
      return {
        field: fieldName,
        title: fieldName.charAt(0).toUpperCase() + fieldName.slice(1) // Capitalize the field name
      };
    });

    // Set the table data
    $('#bulkresultstable').bootstrapTable('destroy');
    $('#bulkresultstable').bootstrapTable({
      columns: columns,
      data: data
    });

  }
  catch (err) {
    console.log(err);
  }
}

// Add export button click event outside the addtotable function
$('#exportButton').click(function () {
  var tableData = $('#bulkresultstable').bootstrapTable('getData');
  var fieldNames = $('#bulkresultstable').bootstrapTable('getOptions').columns[0].map(col => col.field);
  exportToCSV(tableData, fieldNames);
});

// Function to export table data to CSV
function exportToCSV(data, fields) {
  var csvContent = "data:text/csv;charset=utf-8,";

  // Add header row
  csvContent += fields.join(",") + "\n";

  // Add data rows
  data.forEach(function (obj) {
    var row = fields.map(function (field) {
      return obj[field] || "";
    });
    csvContent += row.join(",") + "\n";
  });

  // Create a temporary download link
  var downloadLink = document.createElement("a");
  downloadLink.setAttribute("download", "TransactionResults.csv");
  downloadLink.setAttribute("href", encodeURI(csvContent));

  // Trigger the download
  downloadLink.click();
}

