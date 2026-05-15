document.querySelectorAll("[data-example]").forEach((card) => {
  const button = card.querySelector(".reveal-button");
  const image = card.querySelector(".example-image");
  const label = card.querySelector(".solution-label");

  if (!button || !image || !label) {
    return;
  }

  button.addEventListener("click", () => {
    const showingSolution = button.getAttribute("aria-expanded") === "true";

    if (showingSolution) {
      image.setAttribute("src", image.dataset.problem);
      label.hidden = true;
      button.classList.add("show-solution");
      button.setAttribute("aria-expanded", "false");
      button.textContent = "Show Solution";
    } else {
      image.setAttribute("src", image.dataset.solution);
      label.hidden = false;
      button.classList.remove("show-solution");
      button.setAttribute("aria-expanded", "true");
      button.textContent = "Show Problem";
    }
  });
});

document.querySelectorAll(".reveal-button").forEach((button) => {
  button.classList.add("show-solution");
});
