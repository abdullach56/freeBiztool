(() => {
  const form = document.getElementById("invoiceForm");
  if (!form) return;

  const itemsBody = document.getElementById("itemsBody");
  const addItemBtn = document.getElementById("addItemBtn");
  const downloadPdfBtn = document.getElementById("downloadPdfBtn");
  const subtotalEl = document.getElementById("subtotal");
  const invoiceGstEl = document.getElementById("invoiceGst");
  const grandTotalEl = document.getElementById("grandTotal");

  const formatInr = (value) => `INR ${value.toFixed(2)}`;

  const newItemRow = () => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input type="text" class="item-name" placeholder="Item name" required></td>
      <td><input type="number" class="item-qty" min="0" step="0.01" value="1" required></td>
      <td><input type="number" class="item-price" min="0" step="0.01" value="0" required></td>
      <td>
        <select class="item-gst">
          <option value="5">5%</option>
          <option value="12">12%</option>
          <option value="18" selected>18%</option>
          <option value="28">28%</option>
        </select>
      </td>
      <td class="item-total">INR 0.00</td>
      <td><button type="button" class="icon-btn remove-item" aria-label="Remove item">X</button></td>
    `;
    return tr;
  };

  const getItems = () => {
    const rows = [...itemsBody.querySelectorAll("tr")];
    return rows.map((row) => {
      const name = row.querySelector(".item-name").value.trim();
      const quantity = parseFloat(row.querySelector(".item-qty").value || "0");
      const price = parseFloat(row.querySelector(".item-price").value || "0");
      const gstRate = parseFloat(row.querySelector(".item-gst").value || "0");

      const safeQuantity = Number.isFinite(quantity) ? quantity : 0;
      const safePrice = Number.isFinite(price) ? price : 0;
      const safeRate = Number.isFinite(gstRate) ? gstRate : 0;

      const lineSub = safeQuantity * safePrice;
      const lineGst = lineSub * (safeRate / 100);
      const lineTotal = lineSub + lineGst;

      row.querySelector(".item-total").textContent = formatInr(lineTotal);

      return { name: name || "Item", quantity: safeQuantity, price: safePrice, gstRate: safeRate, lineSub, lineGst };
    });
  };

  const recalculate = () => {
    const items = getItems();
    const subtotal = items.reduce((sum, item) => sum + item.lineSub, 0);
    const totalGst = items.reduce((sum, item) => sum + item.lineGst, 0);
    const grandTotal = subtotal + totalGst;

    subtotalEl.textContent = formatInr(subtotal);
    invoiceGstEl.textContent = formatInr(totalGst);
    grandTotalEl.textContent = formatInr(grandTotal);

    return items;
  };

  const addItem = () => {
    itemsBody.appendChild(newItemRow());
    recalculate();
  };

  const collectPayload = () => {
    const items = recalculate();

    return {
      seller: {
        businessName: document.getElementById("sellerBusinessName").value.trim(),
        address: document.getElementById("sellerAddress").value.trim(),
        gstNumber: document.getElementById("sellerGst").value.trim(),
        phone: document.getElementById("sellerPhone").value.trim(),
      },
      customer: {
        name: document.getElementById("customerName").value.trim(),
        address: document.getElementById("customerAddress").value.trim(),
        gstNumber: document.getElementById("customerGst").value.trim(),
      },
      items,
    };
  };

  addItemBtn.addEventListener("click", addItem);

  itemsBody.addEventListener("input", recalculate);
  itemsBody.addEventListener("change", recalculate);

  itemsBody.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.classList.contains("remove-item")) {
      target.closest("tr")?.remove();
      if (!itemsBody.querySelector("tr")) addItem();
      recalculate();
    }
  });

  downloadPdfBtn.addEventListener("click", async () => {
    if (!form.reportValidity()) return;

    const payload = collectPayload();

    try {
      downloadPdfBtn.disabled = true;
      downloadPdfBtn.textContent = "Generating PDF...";

      const response = await fetch("/api/invoice-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Could not generate invoice PDF.");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "invoice.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert(error instanceof Error ? error.message : "Failed to download PDF.");
    } finally {
      downloadPdfBtn.disabled = false;
      downloadPdfBtn.textContent = "Download Invoice as PDF";
    }
  });

  addItem();
})();
