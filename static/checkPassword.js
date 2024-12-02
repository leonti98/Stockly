const newPassword = document.getElementById('password');
const btn = document.getElementById('submit');
btn.setAttribute('disabled', '');
newPassword.addEventListener('input', function () {
  password = newPassword.value;
  // Initialize variables
  let strength = 0;
  let tips = '';

  // Check password length
  if (password.length < 8) {
    tips += 'Make the password longer. ';
  } else {
    strength += 1;
  }

  // Check for mixed case
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
    strength += 1;
  } else {
    tips += 'Use both lowercase and uppercase letters. ';
  }

  // Check for numbers
  if (password.match(/\d/)) {
    strength += 1;
  } else {
    tips += 'Include at least one number. ';
  }

  // Check for special characters
  if (password.match(/[^a-zA-Z\d]/)) {
    strength += 1;
  } else {
    tips += 'Include at least one special character. ';
  }

  strengthText = document.getElementById('stength');

  // Return results
  if (strength < 2) {
    strengthText.innerText = 'Easy. ' + tips;
    btn.setAttribute('disabled', '');
  } else if (strength === 2) {
    strengthText.innerText = 'Medium. ' + tips;
    btn.removeAttribute('disabled', '');
  } else if (strength === 3) {
    strengthText.innerText = 'difficult. ' + tips;
    btn.removeAttribute('disabled', '');
  } else {
    strengthText.innerText = 'Extremely difficult. ' + tips;
  }
});
