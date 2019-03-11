$(document).ready(function() {

  $('input[name="password"]').on('focusout', function(){
    if ($(this).val().trim().length < 8){
      $(this).addClass('invalid');
    } else {
      $(this).removeClass('invalid');
    }
  });

  $('input[name="confirm"]').on('focusout', function(){
    var form = $(this).parents('form')
    var password = form.find('input[name="password"]').val().trim();
    if ($(this).val().trim() !== password){
      $(this).addClass('invalid');
    } else {
      $(this).removeClass('invalid');
    }
  });

  $('input[name="email"]').on('keyup', function(){
    validate($(this));
  });

  $('input[name="password"]').on('keyup', function(){
    validate($(this));
    validate_password_strenght($(this).val())
  });

  $('input[name="confirm"]').on('keyup', function(){
    validate($(this));
  });


  function validate(selector){
    var form = selector.parents('form');
    var email = form.find('input[name="email"]').val().trim();
    var password = form.find('input[name="password"]').val().trim();
    var confirm_pass = form.find('input[name="confirm"]').val().trim();
    if (email !== "" && password.length >= 8 &&
      password === confirm_pass){
      form.find('#submitLogin').prop('disabled', false);
    } else {
      form.find('#submitLogin').prop('disabled', true);
    }
  }

  // When the user starts to type something inside the password field
  function validate_password_strenght(input) {
    var lowerCaseLetters = /[a-z]/g;
    var upperCaseLetters = /[A-Z]/g;
    var numbers = /[0-9]/g;
    var length = input.length
    if(input.match(lowerCaseLetters)) {
      $("#aLowercase").addClass("green");
      $("#aLowercase").removeClass("red");
    } else {
      $("#aLowercase").addClass("red");
      $("#aLowercase").removeClass("green");
    }
    if(input.match(upperCaseLetters)) {
      $("#aUppercase").addClass("green");
      $("#aUppercase").removeClass("red");
    } else {
      $("#aUppercase").addClass("red");
      $("#aUppercase").removeClass("green");
    }
    if(input.match(numbers)){
      $("#aNumber").addClass("green");
      $("#aNumber").removeClass("red");
    } else {
      $("#aNumber").addClass("red");
      $("#aNumber").removeClass("green");
    }
    if(length >= 8) {
      $("#eight").addClass("green");
      $("#eight").removeClass("red");
    } else {
      $("#eight").addClass("red");
      $("#eight").removeClass("green");
    }
  }
});
