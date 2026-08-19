# Laboratoire numérique : noyau scientifique, tests et notebooks.
# Les sources ne sont PAS copiées dans l'image : elles sont montées à l'exécution
# et exposées via PYTHONPATH, pour qu'une modification de code ne force pas un rebuild.
FROM python:3.12-slim

# MPLBACKEND n'est volontairement pas forcé à « Agg » : sous ipykernel, matplotlib
# sélectionne alors le backend « inline », ce qui intègre les figures dans les
# sorties des notebooks — sans quoi le site publié afficherait du code sans
# graphique. Hors notebook, matplotlib retombe de lui-même sur Agg en l'absence
# d'affichage.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/work/src \
    MPLCONFIGDIR=/tmp/matplotlib

RUN pip install --no-cache-dir \
        "numpy>=1.26" \
        "scipy>=1.11" \
        "matplotlib>=3.8" \
        "pandas>=2.1" \
        "pyarrow>=16.0" \
        "jupyterlab>=4.0" \
        "nbconvert>=7.10" \
        "pytest>=8.0" \
        "ruff>=0.6"

WORKDIR /work
