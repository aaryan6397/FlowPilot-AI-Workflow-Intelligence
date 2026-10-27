const menuButton = document.getElementById('menuButton');
const sidebar = document.getElementById('sidebar');
if (menuButton && sidebar) menuButton.addEventListener('click', () => sidebar.classList.toggle('open'));
document.querySelectorAll('[data-confirm]').forEach((form) => form.addEventListener('submit', (event) => {
  if (!window.confirm(form.dataset.confirm)) event.preventDefault();
}));
window.setTimeout(() => document.querySelectorAll('.flash').forEach((flash) => flash.remove()), 5000);
