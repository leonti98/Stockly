const select = document.querySelector('select');
select.addEventListener('change', async function () {
  let response = await fetch('/availability?stock=' + select.value);
  let max_stocks = await response.json();
  const max_select = document.querySelector('#shares');
  max_select.setAttribute('max', max_stocks);
});
