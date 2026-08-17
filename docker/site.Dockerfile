# Site de documentation bilingue publié sur GitHub Pages.
# Base Debian plutôt que l'image alpine officielle de mkdocs-material : mkdocs-jupyter
# tire nbconvert et ses dépendances, qui disposent de wheels prêtes à l'emploi ici.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# mkdocs-material est borné : la version 10 suivra MkDocs 2.0, qui supprime le système
# de plugins dont dépendent ici l'internationalisation et le rendu des notebooks.
RUN pip install --no-cache-dir \
        "mkdocs-material>=9.5,<10" \
        "mkdocs-static-i18n>=1.2,<2" \
        "mkdocs-jupyter>=0.24,<1" \
        "pymdown-extensions>=10.8"

WORKDIR /docs
EXPOSE 8000
