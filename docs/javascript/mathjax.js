// Configuration de MathJax pour les délimiteurs employés par pymdownx.arithmatex
// en mode « generic » : $…$ en ligne, $$…$$ en bloc.
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"], ["$", "$"]],
    displayMath: [["\\[", "\\]"], ["$$", "$$"]],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

// Re-rendu des formules après une navigation instantanée de Material for MkDocs,
// qui remplace le contenu de la page sans recharger le document.
document$.subscribe(() => {
  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.startup.output.clearCache();
    window.MathJax.typesetClear();
    window.MathJax.texReset();
    window.MathJax.typesetPromise();
  }
});
