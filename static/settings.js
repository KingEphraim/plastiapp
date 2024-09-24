const savebtn = document.getElementById("savebtn");
const savebtnspin = document.getElementById("sbmtbtnspin");
const savebtncont = document.getElementById("sbmtbtncont");
const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
const appendAlert = (message, type) => {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('')

    alertPlaceholder.insertBefore(wrapper, alertPlaceholder.firstChild)
    savebtntoggle('on');
}
function savebtntoggle(state) {



    if (state === 'on') {
        savebtn.disabled = false;
        savebtnspin.hidden = true;
        savebtncont.textContent = "Pay Now";
        // Perform actions when the switch is turned on
        console.log('Switch is ON');
        // Add more code as needed
    } else if (state === 'off') {
        savebtn.disabled = true;
        savebtnspin.hidden = false;
        savebtncont.textContent = "Please Wait";

        // Perform actions when the switch is turned off
        console.log('Switch is OFF');
        // Add more code as needed
    } else {
        // Handle invalid state
        console.error('Invalid state. Please provide "on" or "off".');
    }
}

savebtn.addEventListener("click", () => {
    savebtntoggle('off');


    var formData = {};
    var fields = ["key", "email","phone"];

    fields.forEach(function (field) {
        formData[field] = document.getElementById(field).value;
    });

    formData['tranzType'] = "S";
    // Convert JSON to string for display or further processing
    var formDataJSON = JSON.stringify(formData);

    sendtoserver(formDataJSON)



});


function sendtoserver(serverdata) {

    fetch('/sendtocardknox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: serverdata
    })
        .then(response => response.json())
        .then(data => {
            if (data.xResult == "A") {
                appendAlert(JSON.stringify(data), 'success');
            } else if (data.xResult == "V") {
                verify3DS(data)
                appendAlert(JSON.stringify(data), 'info');
            }
            else {
                appendAlert(JSON.stringify(data), 'danger');
            }
        })
        .catch(error => console.error(error));
}
