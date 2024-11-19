const contactBtn = document.getElementById('contactBtn');
const form = document.getElementById('contactUsForm');
const toastElement = document.getElementById('toast');
const toastMessageElement = document.getElementById('toastMessage');
form.addEventListener('submit', function (event) {
    event.preventDefault();
    console.log('Form submission prevented.');
});
// Function to get input values as JSON
const getInputDataAsJson = (...inputIds) => inputIds.reduce((data, id) => {
    const element = document.getElementById(id);
    if (element && ['INPUT', 'TEXTAREA'].includes(element.tagName)) {
        data[id] = element.value;
    } else if (element) {
        console.warn(`Element with ID "${id}" is not an input or textarea.`);
    } else {
        console.warn(`Element with ID "${id}" not found.`);
    }
    return data;
}, {});


function clearContactForm() {
    // Select the form element
    const form = document.getElementById('contactUsForm');
    
    // Reset the form fields
    form.reset();
  }

// Send JSON data to the server using a POST request
const sendJsonToServer = async (url, jsonData) => {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jsonData)
        });
        if (!response.ok) throw new Error(`Server responded with status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error:', error.message);
        return { success: false, error: error.message };
    }
};

contactBtn.addEventListener('click', () => {
    console.log("contactBtn clicked");

    // Get input data
    const inputData = getInputDataAsJson('name', 'email', 'message');

    // Check if any of the inputs are empty
    if (!inputData.name || !inputData.email || !inputData.message) {
        console.warn('All fields are required.');
        // Optionally, do something else if fields are empty, like showing an error message

        return; // Exit early if fields are empty
    }
    
    // Proceed with sending data if all fields are filled
    sendJsonToServer('/contact', inputData)
        .then(response => {
            if (response.success !== false) {
                console.log('Data sent successfully:', response);
                clearContactForm();
                toastMessageElement.innerText = 'Thank you for reaching out to us! We appreciate your feedback.';
                const toast = new bootstrap.Toast(toastElement);
                toast.show();
            } else {
                console.warn('Server error:', response.error);
                toastMessageElement.innerText = 'Something went wrong';
                const toast = new bootstrap.Toast(toastElement);
                toast.show();
            }
        });
});

