$(document).ready(function () {
  $('#my-form').submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: '/webhookpin',
      method: 'POST',
      data: $('#my-form').serialize(),
      success: function (response) {
        $('#response').html(response);
      },
      error: function () {
        $('#response').html('An error occurred');
      }
    });
  });
}); 