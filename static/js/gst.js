(() => {
  const amountEl = document.getElementById("amount");
  const rateEl = document.getElementById("gstRate");
  const modeEls = document.querySelectorAll("input[name='mode']");
  const cgstEl = document.getElementById("cgst");
  const sgstEl = document.getElementById("sgst");
  const totalEl = document.getElementById("total");

  if (!amountEl) return;

  const formatInr = (value) => `INR ${value.toFixed(2)}`;

  const calculate = () => {
    const amount = parseFloat(amountEl.value || "0");
    const rate = parseFloat(rateEl.value || "0");
    const mode = [...modeEls].find((el) => el.checked)?.value || "add";

    if (!Number.isFinite(amount) || amount < 0) return;

    let base = amount;
    let gstAmount = 0;
    let total = amount;

    if (mode === "add") {
      gstAmount = base * (rate / 100);
      total = base + gstAmount;
    } else {
      base = amount / (1 + rate / 100);
      gstAmount = amount - base;
      total = amount;
    }

    const cgst = gstAmount / 2;
    const sgst = gstAmount / 2;

    cgstEl.textContent = formatInr(cgst);
    sgstEl.textContent = formatInr(sgst);
    totalEl.textContent = formatInr(total);
  };

  amountEl.addEventListener("input", calculate);
  rateEl.addEventListener("change", calculate);
  modeEls.forEach((el) => el.addEventListener("change", calculate));
  calculate();
})();
