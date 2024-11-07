const savebtn = document.getElementById("savebtn");
const savebtnspin = document.getElementById("sbmtbtnspin");
const savebtncont = document.getElementById("sbmtbtncont");
const createdevicebtn = document.getElementById("createdevicebtn");
const createdevicebtnspin = document.getElementById("createdevicebtnspin");
const createdevicebtncont = document.getElementById("createdevicebtncont");
const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
const inputs = document.querySelectorAll('input');
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
    createdevicebtntoggle('on');
}

// Function to update the label based on the checkbox state
function updateLabel(checkboxId, labelId) {
    const checkbox = document.getElementById(checkboxId);
    const label = document.getElementById(labelId);
    label.textContent = checkbox.checked ? "Enabled" : "Disabled";
}

// Add event listeners for both checkboxes
document.getElementById("ccdevice").addEventListener("change", function() {
    updateLabel("ccdevice", "ccdeviceLabel");
});

document.getElementById("threeds").addEventListener("change", function() {
    updateLabel("threeds", "threedsLabel");
});





inputs.forEach(input => {
    input.addEventListener('input', () => {
        
        createdevicebtntoggle('unsavedChanges');   
        
    });
});

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

function createdevicebtntoggle(state) {
    if (state === 'on') {
        createdevicebtn.disabled = false;
        createdevicebtnspin.hidden = true;
        createdevicebtncont.textContent = "Add device";
        console.log('Switch is ON');
    } 
    else if (state === 'off') {
        createdevicebtn.disabled = true;
        createdevicebtnspin.hidden = false;
        createdevicebtncont.textContent = "Please Wait";
        console.log('Switch is OFF');
    } 
    else if (state === 'unsavedChanges') {
        createdevicebtn.disabled = true;
        createdevicebtnspin.hidden = false;
        createdevicebtncont.textContent = "There are unsaved changes";
        console.log('Switch is OFF');
    }else {
        console.error('Invalid state. Please provide "on" or "off".');
    }
}

savebtn.addEventListener("click", () => {
    savebtntoggle('off');

    var formData = {};
    var fields = ["key","command", "email", "phone","deviceSerialNumber","deviceMake","deviceFriendlyName","deviceId", "threeds", "ccdevice"]; 

    fields.forEach(function (field) {
        if (field === "threeds" || field === "ccdevice") { // Check for both "threeds" and "ccdevice"
            formData[field] = document.getElementById(field).checked; // Get checkbox status (true/false)
        } else {
            formData[field] = document.getElementById(field).value;
        }
    });

    formData['tranzType'] = "S";
    var formDataJSON = JSON.stringify(formData);

    sendtoserver(formDataJSON);
});


createdevicebtn.addEventListener("click", () => {
    createdevicebtntoggle('off');   
    
    var formData = {};
    var fields = ["deviceSerialNumber", "deviceMake", "deviceFriendlyName"];

    fields.forEach(field => {
        formData[field] = document.getElementById(field).value;
    });

    formData['tranzType'] = "createdevice";
    var formDataJSON = JSON.stringify(formData);

    fetch('/sendtocardknox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: formDataJSON
    })
        .then(response => response.json())
        .then(data => {
            if (data.xResult === "S") {
                document.getElementById('deviceId').value = data.xDeviceId;
                savebtn.click();                
                // Successful case
                appendAlert(`Device created successfully! ID: ${data.xDeviceId}`, 'success');
                
            } else if (data.xResult === "E") {
                // Error case
                appendAlert(`Error: ${data.xError} (Ref: ${data.xRefnum})`, 'danger');
                // Additional logic for error handling can go here
            } else {
                // Handle unexpected cases
                appendAlert(`Unexpected response: ${JSON.stringify(data)}`, 'warning');
            }
        })
        .catch(error => {
            console.error(error);
            appendAlert(`An error occurred: ${error.message}`, 'danger');
        });
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
            document.getElementById('command').value = data.settings.command || '';
            document.getElementById('phone').value = data.settings.phone || '';
            document.getElementById('deviceSerialNumber').value = data.settings.deviceSerialNumber || '';
            document.getElementById('deviceMake').value = data.settings.deviceMake || '';
            document.getElementById('deviceFriendlyName').value = data.settings.deviceFriendlyName || '';
            document.getElementById('deviceId').value = data.settings.deviceId || '';
            document.getElementById('threeds').checked = data.settings.threeds || false; 
            document.getElementById('ccdevice').checked = data.settings.ccdevice || false; 
            updateLabel("ccdevice", "ccdeviceLabel");
            updateLabel("threeds", "threedsLabel");
            console.log('Settings loaded successfully!', 'success');
        } else {
            console.log(data.message);
        }
    })
    .catch(error => {
        console.error(error);
        appendAlert('Failed to load settings. Please try again.', 'danger');
    });
}


window.onload = function() {
    loadSettings();
    
};

// Function to hide all sections
function hideSections() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
      section.style.display = 'none';
    });
}

// Function to show the clicked section
function showSection(sectionId) {
    hideSections();
    const section = document.getElementById(sectionId);
    if (section) {
      section.style.display = 'block';
      updateSectionName(sectionId); // Update the section name when a section is shown
    }
}

// Function to update the active link
function updateActiveLink(activeLinkId) {
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
      link.classList.remove('active'); // Remove 'active' class from all links
    });
    const activeLink = document.getElementById(activeLinkId);
    if (activeLink) {
      activeLink.classList.add('active'); // Add 'active' class to the clicked link
    }
}

// Function to update the section name
function updateSectionName(sectionId) {
    const sectionNames = {
      'profile-section': 'Profile',
      'transaction-section': 'Transactions',
      'cloudim-section': 'CloudIM'
    };

    let sectionName = sectionNames[sectionId] || 'Unknown Section';
    const sectionNameElement = document.getElementById('section-name'); // Get the <h4> element

    // Update the text of the <h4> element
    if (sectionNameElement) {
      sectionNameElement.textContent = `${sectionName}`;
    }
}

// Add click event listeners to sidebar links
document.getElementById('profile-link').addEventListener('click', function(e) {
    e.preventDefault();
    showSection('profile-section');
    updateActiveLink('profile-link'); // Highlight the clicked link
});

document.getElementById('transaction-link').addEventListener('click', function(e) {
    e.preventDefault();
    showSection('transaction-section');
    updateActiveLink('transaction-link'); // Highlight the clicked link
});

document.getElementById('cloudim-link').addEventListener('click', function(e) {
    e.preventDefault();
    showSection('cloudim-section');
    updateActiveLink('cloudim-link'); // Highlight the clicked link
});

// Show the profile section by default
showSection('profile-section');
updateActiveLink('profile-link'); // Highlight the default section
