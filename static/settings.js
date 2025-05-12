const savebtn = document.getElementById("savebtn");
const savebtnspin = document.getElementById("sbmtbtnspin");
const savebtncont = document.getElementById("sbmtbtncont");

const alertPlaceholder = document.getElementById('liveAlertPlaceholder');
const inputs = document.querySelectorAll('input');
const fields = ["key", "command","voidtype", "ebtcommand", "username","lbendpoint", "useremail", "fullname", "phone", "deviceSerialNumber", "deviceMake", "deviceFriendlyName", "deviceId", "threeds", "googlePay", "ebtOnline", "ccdevice", "allowDuplicate","emailInvoice","tapToPhone"];
const userName = document.getElementById("username");
const userEmail = document.getElementById("useremail");
let currentUserSettings = {};

function validateUsername(username) {
    // Check if username meets the criteria:
    // - At least 6 characters long
    // - Only alphanumeric, underscores, and hyphens
    // - No spaces
    // - Cannot start or end with an underscore or hyphen
    const regex = /^(?=.*[a-zA-Z0-9])[a-zA-Z0-9_-]{6,}$/;
    const isValid = regex.test(username) && !/^[-_]|[-_]$/.test(username);
    return isValid;
}

function validateEmail(useremail) {
    // Check if email is valid
    return /\S+@\S+\.\S+/.test(useremail);
}

const appendAlert = (message, type) => {
    alertPlaceholder.innerHTML = ''; // Clear existing alerts
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
        <div class="alert alert-${type} alert-dismissible m-0" role="alert">
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
["ccdevice", "threeds", "googlePay", "ebtOnline", "allowDuplicate", "emailInvoice", "tapToPhone"].forEach(id => {
    document.getElementById(id).addEventListener("change", () => {
        updateLabel(id, `${id}Label`);
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
        
    } else if (state === 'off') {
        toggle(savebtn, savebtnspin, savebtncont, "Please Wait", true);
       
    } else if (state === 'unsavedChanges') {
        
    }
};

function toggleEdit(inputId, buttonId) {
    const inputField = document.getElementById(inputId);
    const button = document.getElementById(buttonId);

    if (inputField.hasAttribute("readonly")) {
      inputField.removeAttribute("readonly");
      button.textContent = "Done";
    } else {
      inputField.setAttribute("readonly", true);
      button.textContent = "Edit";
    }
  }

  document.getElementById("editUsername").addEventListener("click", function () {
    toggleEdit("username", "editUsername");
  });

  document.getElementById("editEmail").addEventListener("click", function () {
    toggleEdit("useremail", "editEmail");
  });

// Function to save settings
const saveSettings = async () => {
    toggleButtonState('off');

    let formData = {};
    let validationFields = ["username", "useremail"];
    let isValid = true;

    // Validate username & email
    validationFields.forEach(field => {
        let value = document.getElementById(field)?.value || "";
        formData[field] = value;

        if (field === "username" && !validateUsername(value)) {
            isValid = false;
            appendAlert('Username must be at least 6 characters and can include letters, numbers, underscores, or hyphens—no special characters at the start or end.', 'danger');
        } else if (field === "useremail" && !validateEmail(value)) {
            isValid = false;
            appendAlert('Please enter a valid email address.', 'danger');
        }
    });

    if (!isValid) {
        toggleButtonState('on');
        return null;
    }

    if (userName.value !== currentUserSettings.username) {
        if (!confirm('You are about to change your username. This will log you out and you will need to log back in with your new username.')) {
            toggleButtonState('on');
            return null;
        }
    }

    // Collect all form fields
    formData = fields.reduce((data, field) => {
        if (["threeds", "ccdevice", "googlePay", "ebtOnline", "allowDuplicate", "emailInvoice", "tapToPhone"].includes(field)) {
            data[field] = document.getElementById(field)?.checked || false;
        } else {
            data[field] = document.getElementById(field)?.value || "";
        }
        return data;
    }, { tranzType: "S" });

    try {
        const response = await fetch('/save_settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const data = await response.json();
        const alertType = data.status === "success" ? 'success' : 'danger';
        appendAlert(JSON.stringify(data), alertType);

        return formData;  // ✅ Always return the same object you sent
    } catch (error) {
        console.error(error);
        toggleButtonState('on');
        return null;
    }
};



// Function to create device
const createDevice = (formData) => {
    toggleButtonState('off');

    // Use the provided data directly instead of reading DOM again
    const deviceData = {
        deviceSerialNumber: formData.deviceSerialNumber,
        deviceMake: formData.deviceMake,
        deviceFriendlyName: formData.deviceFriendlyName,
        tranzType: "createdevice"
    };

    fetch('/sendtocardknox', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deviceData)
    })
    .then(response => response.json())
    .then(data => {
        const { ckRequest, ckResponse } = data;
        if (ckResponse.xResult === "S") {
            document.getElementById('deviceId').value = ckResponse.xDeviceId;                
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
                currentUserSettings = data.settings;
                if (Array.isArray(fields)) {
                    fields.forEach(field => {
                        const value = data.settings[field];
                        const element = document.getElementById(field);

                        if (element) {
                            if (value !== undefined && value !== null) { // Ensure value is defined and not null
                                if (field === "key") {
                                    const currentKeyElement = document.getElementById("key");
                                    if (currentKeyElement) {
                                        currentKeyElement.placeholder = value;
                                    }
                                } else {
                                    if (element.type === "checkbox") {
                                        element.checked = value; // Set checked state
                                    } else {
                                        element.value = value; // Set value
                                    }
                                }
                            }
                        }
                        
                    });

                } else {
                    console.warn('Fields array is not defined or is not an array.');
                }

                // Update labels
                ["ccdevice", "threeds", "googlePay", "ebtOnline", "allowDuplicate", "emailInvoice","tapToPhone"].forEach(id => updateLabel(id, `${id}Label`));

                console.log('Settings loaded successfully!');
            } else {
                console.log('Error loading settings: ' + data.message);
                appendAlert('Failed to load settings. Please try again.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error fetching settings: ', error);
            appendAlert('Failed to load settings. Please try again.', 'danger');
        });
};


window.onload = function () {
    loadSettings();
};

savebtn.addEventListener("click", async function() {
    const formData = await saveSettings();  // Get the actual saved data object

    if (formData?.ccdevice) {
        createDevice(formData);
    }
});




document.getElementById('deleteUserBtn').addEventListener('click', () => {
    if (window.confirm("Are you sure you want to delete your account? This action is irreversible.")) {
      toggleButtonSpinner('deleteUserBtn'); 
      var user = { username: currentUserSettings.username };
      fetchResponse = fetchData('/delete_user', user)
      .then(data => {
        if (data.status === 'success') {            
            console.log(data.message);
            window.location.href = '/';            
        } else {            
            console.error('User deletion failed:', data.message || 'Unknown error');            
        }
    }) 
      
      toggleButtonSpinner('deleteUserBtn'); 
    }
  });



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
document.getElementById('profile-link').addEventListener('click', function (e) {
    e.preventDefault();
    showSection('profile-section');
    updateActiveLink('profile-link'); // Highlight the clicked link
});

document.getElementById('transaction-link').addEventListener('click', function (e) {
    e.preventDefault();
    showSection('transaction-section');
    updateActiveLink('transaction-link'); // Highlight the clicked link
});

document.getElementById('cloudim-link').addEventListener('click', function (e) {
    e.preventDefault();
    showSection('cloudim-section');
    updateActiveLink('cloudim-link'); // Highlight the clicked link
});

// Show the profile section by default
showSection('profile-section');
updateActiveLink('profile-link'); // Highlight the default section

function toggleButtonSpinner(buttonId) {
    var button = document.getElementById(buttonId);
    var spinner = document.getElementById(buttonId + 'Spinner');
    var span = document.getElementById(buttonId + 'Span');

    if (button && spinner && span) {
        button.disabled = !button.disabled;
        spinner.hidden = !spinner.hidden;
        span.hidden = !span.hidden;
    } else {
        console.error(`One or more elements for the buttonId '${buttonId}' are not found.`);
    }
}