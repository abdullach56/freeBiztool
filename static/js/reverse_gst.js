(() => {
  const grossEl = document.getElementById("grossAmount");
  const rateEl = document.getElementById("reverseRate");
  const taxableEl = document.getElementById("taxable");
  const totalGstEl = document.getElementById("totalGst");
  const netAmountEl = document.getElementById("netAmount");

  if (!grossEl) return;

  const formatInr = (value) => `INR ${value.toFixed(2)}`;

  const calculate = () => {
    const gross = parseFloat(grossEl.value || "0");
    const rate = parseFloat(rateEl.value || "0");

    if (!Number.isFinite(gross) || gross < 0) return;

    const taxable = gross / (1 + rate / 100);
    const gst = gross - taxable;

    taxableEl.textContent = formatInr(taxable);
    totalGstEl.textContent = formatInr(gst);
    netAmountEl.textContent = formatInr(gross);
  };

  grossEl.addEventListener("input", calculate);
  rateEl.addEventListener("change", calculate);
  calculate();
})();
