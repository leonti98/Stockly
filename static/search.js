let input = document.querySelector('input');
input.addEventListener('input', async function () {
  let response = await fetch('/search?q=' + input.value);
  let stocks = await response.json();
  let html = '';
  if (Array.isArray(stocks)) {
    // Check if stocks is an array
    stocks.forEach(function (stock) {
      // Iterate through each stock object
      let title = stock.stock_symbol.replace('<', '&lt;').replace('&', '&amp;');
      html +=
        '<button type="button" class="btn btn-primary btn-sm">' +
        title +
        '</button>';
    });
  }
  let options = document.querySelector('.options');
  options.innerHTML = html;
  let buttons = document.querySelectorAll('.btn-sm');
  buttons.forEach((button) => {
    button.addEventListener('click', function () {
      input.value = button.innerHTML;
      buttons.forEach((btn) => btn.remove());
    });
  });
});
