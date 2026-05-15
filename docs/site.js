document.querySelectorAll("[data-example]").forEach((card) => {
  const button = card.querySelector(".reveal-button");
  const image = card.querySelector(".example-image");

  if (!button || !image) {
    return;
  }

  button.addEventListener("click", () => {
    const showingSolution = button.getAttribute("aria-expanded") === "true";

    if (showingSolution) {
      image.setAttribute("src", image.dataset.problem);
      button.setAttribute("aria-expanded", "false");
      button.textContent = "Show Solution";
    } else {
      image.setAttribute("src", image.dataset.solution);
      button.setAttribute("aria-expanded", "true");
      button.textContent = "Show Problem";
    }
  });
});
