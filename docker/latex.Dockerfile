# Compilation de la note scientifique (FR et EN) en PDF.
# L'image "medium" contient latexmk, babel-french, amsmath, biblatex et les polices
# nécessaires, sans le poids de la distribution complète.
FROM texlive/texlive:latest-medium

WORKDIR /paper
