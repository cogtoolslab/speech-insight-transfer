document.querySelectorAll("[data-example]").forEach((card) => {
  const button = card.querySelector(".reveal-button");
  const problemImage = card.querySelector(".problem-image");
  const solutionImage = card.querySelector(".solution-image");

  if (!button || !problemImage || !solutionImage) {
    return;
  }

  button.addEventListener("click", () => {
    const isShowingSolution = button.getAttribute("aria-expanded") === "true";

    problemImage.hidden = !isShowingSolution;
    solutionImage.hidden = isShowingSolution;
    button.setAttribute("aria-expanded", String(!isShowingSolution));
    button.textContent = isShowingSolution ? "Show Solution" : "Show Problem";
  });
});
