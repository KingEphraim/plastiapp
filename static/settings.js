const savebtn = document.getElementById("savebtn");
const savebtnspin = document.getElementById("sbmtbtnspin");
const savebtncont = document.getElementById("sbmtbtncont");
const createdevicebtn = document.getElementById("createdevicebtn");
const createdevicebtnspin = document.getElementById("createdevicebtnspin");
const createdevicebtncont = document.getElementById("createdevicebtncont");
const alertPlaceholder = document.getElementById('liveAlertPlaceholder');
const inputs = document.querySelectorAll('input');
const fields = ["key", "command", "ebtcommand", "email", "phone", "deviceSerialNumber", "deviceMake", "deviceFriendlyName", "deviceId", "threeds", "googlePay", "ebtOnline", "ccdevice"];

const appendAlert = (message, type) => {
    alertPlaceholder.innerHTML = ''; // Clear existing alerts
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
        <div class="alert alert-${type} alert-dismissible" role="alert">
            <div>${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
    alertPlaceholder.appendChild(wrapper);
    toggleButtonState('on');
};

const updateLabel = (checkboxId, labelId) => {
    const checkbox = document.getElementById(checkboxId);
    const label = document.getElementById(labelId);
    label.textContent = checkbox.checked ? "Enabled" : "Disabled";
};

// Event listener for checkbox state updates
["ccdevice", "threeds", "googlePay", "ebtOnline"].forEach(id => {
    document.getElementById(id).addEventListener("change", () => {
        updateLabel(id, `${id}Label`);
    });
});

inputs.forEach(input => {
    input.addEventListener('input', () => {
        toggleButtonState('unsavedChanges');
    });
});

// Toggle function for buttons
const toggleButtonState = (state) => {
    const toggle = (button, spin, cont, text, disabled) => {
        button.disabled = disabled;
        spin.hidden = !disabled;
        cont.textContent = text;
    };
    if (state === 'on') {
        toggle(savebtn, savebtnspin, savebtncont, "Save Settings", false);
        toggle(createdevicebtn, createdevicebtnspin, createdevicebtncont, "Add device", false);
    } else if (state === 'off') {
        toggle(savebtn, savebtnspin, savebtncont, "Please Wait", true);
        toggle(createdevicebtn, createdevicebtnspin, createdevicebtncont, "Please Wait", true);
    } else if (state === 'unsavedChanges') {
        toggle(createdevicebtn, createdevicebtnspin, createdevicebtncont, "There are unsaved changes", true);
    }
};

// Function to save settings
const saveSettings = () => {
    toggleButtonState('off');
    const formData = fields.reduce((data, field) => {
        if (["threeds", "ccdevice", "googlePay", "ebtOnline"].includes(field)) {
            data[field] = document.getElementById(field).checked;
        } else {
            data[field] = document.getElementById(field).value;
        }
        return data;
    }, { tranzType: "S" });

    sendToServer(JSON.stringify(formData));
};

// Function to create device
const createDevice = () => {
    toggleButtonState('off');
    const formData = ["deviceSerialNumber", "deviceMake", "deviceFriendlyName"].reduce((data, field) => {
        data[field] = document.getElementById(field).value;
        return data;
    }, { tranzType: "createdevice" });

    fetch('/sendtocardknox', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            const { ckRequest, ckResponse } = data;
            if (ckResponse.xResult === "S") {
                document.getElementById('deviceId').value = ckResponse.xDeviceId;
                savebtn.click();
                appendAlert(`Device created successfully! ID: ${ckResponse.xDeviceId}`, 'success');
            } else if (ckResponse.xResult === "E") {
                appendAlert(`Error: ${ckResponse.xError} (Ref: ${ckResponse.xRefnum})`, 'danger');
            } else {
                appendAlert(`Unexpected response: ${JSON.stringify(ckResponse)}`, 'warning');
            }
        })
        .catch(error => {
            console.error(error);
            appendAlert(`An error occurred: ${error.message}`, 'danger');
        });
};

// Function to send data to the server
const sendToServer = (data) => {
    fetch('/save_settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: data
    })
        .then(response => response.json())
        .then(data => {
            const alertType = data.status === "success" ? 'success' : 'danger';
            appendAlert(JSON.stringify(data), alertType);
        })
        .catch(error => console.error(error));
};

// Function to load settings
const loadSettings = () => {
    fetch('/load_settings', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                fields.forEach(field => {
                    const value = data.settings[field];
                    const element = document.getElementById(field);
                    if (element) {
                        if (element.type === "checkbox") {
                            element.checked = value || false;
                        } else {
                            element.value = value || '';
                        }
                    }
                });
                ["ccdevice", "threeds", "googlePay", "ebtOnline"].forEach(id => updateLabel(id, `${id}Label`));
                console.log('Settings loaded successfully!');
            } else {
                console.log(data.message);
            }
        })
        .catch(error => {
            console.error(error);
            appendAlert('Failed to load settings. Please try again.', 'danger');
        });
};

window.onload = function () {
    loadSettings();
};

savebtn.addEventListener("click", saveSettings);
createdevicebtn.addEventListener("click", createDevice);


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
