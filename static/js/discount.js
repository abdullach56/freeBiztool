(() => {
  const originalEl = document.getElementById("originalPrice");
  const discountEl = document.getElementById("discountPercent");
  const discountAmountEl = document.getElementById("discountAmount");
  const finalPriceEl = document.getElementById("finalPrice");

  if (!originalEl) return;

  const formatInr = (value) => `INR ${value.toFixed(2)}`;

  const calculate = () => {
    const original = parseFloat(originalEl.value || "0");
    const discount = parseFloat(discountEl.value || "0");

    if (!Number.isFinite(original) || original < 0) return;

    const pct = Math.min(Math.max(discount, 0), 100);
    const discountAmount = original * (pct / 100);
    const finalPrice = original - discountAmount;

    discountAmountEl.textContent = formatInr(discountAmount);
    finalPriceEl.textContent = formatInr(finalPrice);
  };

  originalEl.addEventListener("input", calculate);
  discountEl.addEventListener("input", calculate);
  calculate();
})();
