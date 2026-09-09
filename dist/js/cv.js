const printButton = document.getElementById('print-cv');
if (printButton) {
  printButton.hidden = false;
  printButton.addEventListener('click', () => window.print());
}
