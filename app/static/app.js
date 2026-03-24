(() => {
  const addForm = document.getElementById("add-item-form");
  const addItemInput = document.getElementById("add-item-id");

  if (!addForm || !addItemInput) {
    return;
  }

  document.querySelectorAll(".class-add-btn").forEach((button) => {
    button.addEventListener("click", () => {
      let items = [];
      try {
        items = JSON.parse(button.dataset.items || "[]");
      } catch {
        items = [];
      }

      if (!items.length) {
        window.alert("No catalog items available for this class.");
        return;
      }

      const names = items.map((item, index) => `${index + 1}. ${item.product_name}`).join("\n");
      const picked = window.prompt(`Add medication from ${button.dataset.class}:\n${names}\n\nEnter number:`);
      if (!picked) {
        return;
      }

      const selectedIndex = Number(picked) - 1;
      if (Number.isNaN(selectedIndex) || selectedIndex < 0 || selectedIndex >= items.length) {
        window.alert("Invalid selection number.");
        return;
      }

      addItemInput.value = String(items[selectedIndex].id);
      addForm.submit();
    });
  });
})();
