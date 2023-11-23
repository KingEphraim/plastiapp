const button = document.getElementById("sbmtbtn");
button.addEventListener("click", () => {
  


  fetch('/sendtocardknox', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'John Doe',
      email: 'johndoe@example.com'
    })
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));

});