(() => {
  document.querySelectorAll("[data-toggle-class]").forEach((button) => {
    button.addEventListener("click", () => {
      const classId = button.dataset.toggleClass;
      const form = document.getElementById(`class-add-${classId}`);
      if (!form) return;
      form.classList.toggle("hidden");
    });
  });
})();
