const savebtn = document.getElementById("savebtn");
const savebtnspin = document.getElementById("sbmtbtnspin");
const savebtncont = document.getElementById("sbmtbtncont");
const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
const appendAlert = (message, type) => {
    // Clear the existing alerts
    alertPlaceholder.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('');

    alertPlaceholder.appendChild(wrapper); // Use appendChild to add the new alert
    savebtntoggle('on');
}
// Function to toggle the Save button state
function savebtntoggle(state) {
    if (state === 'on') {
        savebtn.disabled = false;
        savebtnspin.hidden = true;
        savebtncont.textContent = "Save Settings";
        console.log('Switch is ON');
    } else if (state === 'off') {
        savebtn.disabled = true;
        savebtnspin.hidden = false;
        savebtncont.textContent = "Please Wait";
        console.log('Switch is OFF');
    } else {
        console.error('Invalid state. Please provide "on" or "off".');
    }
}

// Save button event listener
savebtn.addEventListener("click", () => {
    savebtntoggle('off');

    var formData = {};
    var fields = ["key", "email", "phone"];

    fields.forEach(function (field) {
        formData[field] = document.getElementById(field).value;
    });

    formData['tranzType'] = "S";
    var formDataJSON = JSON.stringify(formData);

    sendtoserver(formDataJSON);
});

// Function to send data to the server
function sendtoserver(serverdata) {
    fetch('/save_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: serverdata
    })
        .then(response => response.json())
        .then(data => {
            if (data.status == "success") {
                appendAlert(JSON.stringify(data), 'success');
            }else {
                appendAlert(JSON.stringify(data), 'danger');
            }
        })
        .catch(error => console.error(error));
}

// Function to load settings from the server
function loadSettings() {
    fetch('/load_settings', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Populate the form fields with loaded settings
            document.getElementById('email').value = data.settings.useremail || '';
            document.getElementById('key').value = data.settings.key || '';
            document.getElementById('phone').value = data.settings.phone || '';

            appendAlert('Settings loaded successfully!', 'success');
        } else {
            appendAlert(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error(error);
        appendAlert('Failed to load settings. Please try again.', 'danger');
    });
}

// Automatically load settings when the page loads
window.onload = function() {
    loadSettings();
};
