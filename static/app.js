async function fetchAsync(url) {
  let response = await fetch(url);
  let data = await response.json();
  return data;
}
document.getElementById("pullcatreport").addEventListener("click", pulcatreport);
document.getElementById("pullprodreport").addEventListener("click", pulprodreport);
function pulcatreport() {
  $table.bootstrapTable('destroy')
  $state = document.getElementById("state").value 
  $environment = document.getElementById("environment").value 
  $('#table').bootstrapTable({
    
    url: '/aplpull',
    pagination: true,
    search: true,
    showSearchClearButton: true,
    visibleSearch: false,
    queryParams:"apltype=catg&state="+$state+"&environment="+$environment,
    columns: [{
      sortable: true,
      field: 'CategoryCode',
      title: 'CategoryCode',
      align: 'left'
    }, {
      sortable: true,
      field: 'CategoryDescription',
      title: 'CategoryDescription',
      align: 'left'
    }, {
      sortable: true,
      field: 'SubCategoryCode',
      title: 'SubCategoryCode',
      align: 'left'
    }, {
      sortable: true,
      field: 'SubCategoryDescription',
      title: 'SubCategoryDescription',
      align: 'left',
    }, {
      sortable: true,
      field: 'BenefitUnitDescription',
      title: 'BenefitUnitDescription',
      align: 'left',
    }, {
      sortable: true,
      field: 'Search',
      title: 'Search',
      align: 'left',
      visible: false
    }],
    onLoadError: function (status, res) {
      let message;
      if (status === 404) {
        message = 'No report found for the selected criteria.';
      } else {
        message = 'An error occurred while loading the report.';
      }
      alert(`${message}\n\nServer Response: ${res.responseText}`);
    }
  });




}
function pulprodreport() {
  $table.bootstrapTable('destroy')
  $state = document.getElementById("state").value 
  $environment = document.getElementById("environment").value 
  //let data = { 'name': 'John', 'age': 30 };
  // fetch('/prod', {
  //   method: 'POST',
  //   body: JSON.stringify(data),
  //   headers: { 'Content-Type': 'application/json' }
  // })
  //   .then(response => response.json())
  //   .then(data => {
  //     console.log('Data received from Flask:', data);
  //   });

    $('#table').bootstrapTable({
      //url: 'https://xi2p82bdoc.execute-api.us-east-1.amazonaws.com/Prod/apiV1/aplprodlist',
      url: '/aplpull',      
      pagination: true,
      search: true,
      showSearchClearButton: true,
      visibleSearch: false,
      queryParams:"apltype=prod&state="+$state+"&environment="+$environment,
      columns: [{
        sortable: true,
        field: 'UPC_PLU',
        title: 'UPC_PLU',
        align: 'left'
      }, {
        sortable: true,
        field: 'ItemDescription',
        title: 'ItemDescription',
        align: 'left'
      }, {
        sortable: true,
        field: 'CategoryCode',
        title: 'CategoryCode',
        align: 'left',
      }, {
        sortable: true,
        field: 'CategoryDescription',
        title: 'CategoryDescription',
        align: 'left',
      }, {
        sortable: true,
        field: 'SubCategoryCode',
        title: 'SubCategoryCode',
        align: 'left',
      }, {
        sortable: true,
        field: 'SubCategoryDescription',
        title: 'SubCategoryDescription',
        align: 'left',
      }, {
        sortable: true,
        field: 'UnitOfMeasure',
        title: 'UnitOfMeasure',
        align: 'left',
      }, {
        sortable: true,
        field: 'PackageSize',
        title: 'PackageSize',
        align: 'left',
      }, {
        sortable: true,
        field: 'BenefitQuantity',
        title: 'BenefitQuantity',
        align: 'left',
      }, {
        sortable: true,
        field: 'BenefitUnitDescription',
        title: 'BenefitUnitDescription',
        align: 'left',
      }, {
        sortable: true,
        field: 'ItemPrice',
        title: 'ItemPrice',
        align: 'left',
      }, {
        sortable: true,
        field: 'PriceType',
        title: 'PriceType',
        align: 'left',
      }, {
        sortable: true,
        field: 'DateEffective',
        title: 'DateEffective',
        align: 'left',
      },  {
        sortable: true,
        field: 'UPC_UPLDataLength',
        title: 'UPC_UPLDataLength',
        align: 'left',
      }, {
        sortable: true,
        field: 'CategoryDescription',
        title: 'CategoryDescription',
        align: 'left',
      },
      {
        sortable: true,
        field: 'Search',
        title: 'Search',
        align: 'left',
        visible: false
      }],
      onLoadError: function (status, res) {
        let message;
        if (status === 404) {
          message = 'No report found for the selected criteria.';
        } else {
          message = 'An error occurred while loading the report.';
        }
        alert(`${message}\n\nServer Response: ${res.responseText}`);
      }
    });

}
var $table = $('#table')
var $button = $('#button')

$(function () {
  $button.click(function () {
    $table.bootstrapTable('resetSearch')
  })
})


const toastTrigger = document.getElementById('liveToastBtn')
const toastLiveExample = document.getElementById('liveToast')
if (toastTrigger) {
  toastTrigger.addEventListener('click', () => {
    const toast = new bootstrap.Toast(toastLiveExample)

    toast.show()
  })
}
$("#paymentpage").submit(function (e) {
  e.preventDefault();
  $("#notifypopup").hide();
  $("#loading").addClass("h-100 d-flex justify-content-center align-items-center");

  $.ajax({
    //url: 'https://localhost:64482/apiV1/ckapi', // local
    url: 'https://xi2p82bdoc.execute-api.us-east-1.amazonaws.com/Prod/apiV1/ckapi', // prod
    type: "POST",
    data: $('#paymentpage').serialize(),
    dataType: "json",
    success: function (data) {
      console.log(data);
      $("#loading").removeClass("h-100 d-flex justify-content-center align-items-center");


      let notify = "";
      if (data.xResult == "A") {
        document.getElementById("liveToast").className = "toast approved"; notify = "Thank you for your " + "$" + data.xAuthAmount + " Payment";
      }
      else if ((data.xResult == "E") | "D") {
        document.getElementById("liveToast").className = "toast dclnerr"; notify = "Please try again: " + data.xError;
      } else {
        document.getElementById("liveToast").className = "toast dclnerr"; notify = "Check the console";
      }
      document.getElementById("tstbody").innerHTML = notify;
      document.getElementById("tsttime").innerHTML = data.xDate;
      document.getElementById("tststatus").innerHTML = data.xStatus;
      console.log(notify);
      const toast = new bootstrap.Toast(toastLiveExample)

      toast.show()




    },
    error: function (data) {
      $("#loading").removeClass("h-100 d-flex justify-content-center align-items-center");
      console.log(data);
    }
  });
}
)

document.querySelector('#my-form').addEventListener('submit', function(event) {
  // prevent default form submission behavior
  event.preventDefault();
  
  // get form data
  const formData = new FormData(event.target);
  
  // send AJAX post request to Flask server
  fetch('/submit_form', {
    method: 'POST',
    body: JSON.stringify(Object.fromEntries(formData.entries())),
    headers: {'Content-Type': 'application/json'}
  })
  .then(response => response.json())
  .then(data => {
    // handle the response from the Flask server
    console.log(data);
  });
});