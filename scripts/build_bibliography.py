#!/usr/bin/env python3
"""Publie la bibliographie du dépôt, dans les deux langues, depuis ``paper/refs.bib``.

La bibliographie était jusqu'ici enfermée dans les notes LaTeX : un lecteur du site ne pouvait
pas savoir sur quoi le travail s'appuie sans compiler un PDF. Ce script en fait une page, et la
**dérive** du fichier BibTeX plutôt que de la recopier — les deux ne peuvent donc pas diverger.
Un test vérifie que les pages publiées correspondent au fichier source.

Chaque référence est accompagnée de ce qu'elle sert **ici**, ce qui distingue une bibliographie
d'une liste de lectures : une référence sans usage identifiable n'a rien à y faire.

Usage :

    docker compose run --rm lab python scripts/build_bibliography.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BIB_PATH = Path(__file__).resolve().parents[1] / "paper" / "refs.bib"
DOCS = Path(__file__).resolve().parents[1] / "docs"

#: Thèmes, dans l'ordre de publication. Chaque entrée : clés BibTeX, titre FR, titre EN.
THEMES: list[tuple[tuple[str, ...], str, str]] = [
    (("shannon1948", "vonneumann1932", "jost2006"),
     "Entropie et information", "Entropy and information"),
    (("zeh1970", "zurek2003"),
     "Décohérence quantique — l'analogie de départ, réfutée depuis",
     "Quantum decoherence — the founding analogy, since refuted"),
    (("ising1925", "onsager1944", "galam2004", "castellano2009", "clifford1973", "holley1975",
      "deffuant2000", "kramers1940", "risken1989", "watts1998", "reynolds1987"),
     "Physique statistique de l'opinion", "Statistical mechanics of opinion"),
    (("pariser2011", "carbonell1998", "rao1982", "ohsaka2023", "steck2018", "vrijenhoek2022"),
     "Recommandation, diversité et normativité",
     "Recommendation, diversity and normativity"),
    (("joachims2017", "agarwal2019", "swaminathan2015", "vardasbi2020", "hager2024"),
     "Biais de position et évaluation contrefactuelle",
     "Position bias and counterfactual evaluation"),
    (("wu2020", "zou2022", "saito2020", "vandrunen2025"),
     "Jeux de données publics", "Public datasets"),
    (("dsa2022", "delegue2025"), "Droit européen", "European law"),
]

#: Ce que chaque référence sert **dans ce dépôt**, et où. Une référence sans usage n'a pas
#: sa place dans une bibliographie : elle appartiendrait à une liste de lectures.
USES: dict[str, tuple[str, str]] = {
    "shannon1948": ("Définit l'entropie dont l'indice est la version normalisée.",
                    "Defines the entropy of which the index is the normalised version."),
    "vonneumann1932": ("Entropie du sous-système réduit, sur laquelle reposait l'analogie.",
                       "Reduced-subsystem entropy, on which the analogy rested."),
    "jost2006": ("Justifie de publier l'indice en **nombre effectif de points de vue** plutôt "
                 "qu'en entropie normalisée.",
                 "Justifies publishing the index as an **effective number of viewpoints** "
                 "rather than a normalised entropy."),
    "zeh1970": ("Source de l'analogie décohérence / effondrement du consensus.",
                "Source of the decoherence / consensus-collapse analogy."),
    "zurek2003": ("Le résultat dont $\\tau_D \\propto \\tau_R/N$ était une lecture heuristique "
                  "et fausse.",
                  "The result of which $\\tau_D \\propto \\tau_R/N$ was a heuristic and "
                  "incorrect reading."),
    "ising1925": ("Modèle de la température sociale et de la transition de phase.",
                  "Model of social temperature and the phase transition."),
    "onsager1944": ("Température critique exacte, seule prédiction vérifiable du formalisme.",
                    "Exact critical temperature, the formalism's only checkable prediction."),
    "galam2004": ("Lignée sociophysique dont relève ce qui subsiste du modèle.",
                  "The sociophysics lineage to which what survives of the model belongs."),
    "castellano2009": ("Revue de référence des dynamiques d'opinion.",
                       "Reference survey of opinion dynamics."),
    "clifford1973": ("Voter Model, employé pour les lois d'échelle du consensus.",
                     "Voter model, used for consensus scaling laws."),
    "holley1975": ("Formalisation du Voter Model et de son temps de consensus.",
                   "Formalisation of the voter model and its consensus time."),
    "deffuant2000": ("Opinions continues : rappelle que les individus ne sont pas des spins.",
                     "Continuous opinions: a reminder that individuals are not spins."),
    "kramers1940": ("Franchissement de barrière par activation — l'analogue correct de "
                    "l'« effet tunnel social ».",
                    "Activated barrier crossing — the correct analogue of \"social tunnelling\"."),
    "risken1989": ("Équation de Fokker-Planck et ses solutions stationnaires.",
                   "The Fokker-Planck equation and its stationary solutions."),
    "watts1998": ("Réseaux « petit monde », dont l'argument d'origine tirait une conclusion "
                  "fausse.",
                  "Small-world networks, from which the original argument drew a false "
                  "conclusion."),
    "reynolds1987": ("Modèle à agents dont dérive le prototype archivé.",
                     "Agent model from which the archived prototype derives."),
    "pariser2011": ("Formulation populaire de la bulle de filtres.",
                    "Popular formulation of the filter bubble."),
    "carbonell1998": ("MMR : la ligne de base qui tient la frontière aussi bien que le filtre "
                      "proposé ici.",
                      "MMR: the baseline that holds the frontier as well as the filter "
                      "proposed here."),
    "rao1982": ("Entropie quadratique, premier remplaçant envisagé — et écarté.",
                "Quadratic entropy, the first replacement considered — and discarded."),
    "ohsaka2023": ("Établit les optima dégénérés de l'*intra-list distance*, retrouvés ici par "
                   "optimisation sous contrainte.",
                   "Establishes the degenerate optima of intra-list distance, recovered here "
                   "by constrained optimisation."),
    "steck2018": ("Recommandations calibrées : la cible comme distribution déclarée.",
                  "Calibrated recommendations: the target as a declared distribution."),
    "vrijenhoek2022": ("RADio : divergences conscientes du rang et diversité normative, dont "
                       "l'indice n'occupe qu'une dimension.",
                       "RADio: rank-aware divergences and normative diversity, of which the "
                       "index occupies only one dimension."),
    "joachims2017": ("Modèle de biais de position $e(R) = R^{-\\eta}$ et correction par "
                     "propension inverse.",
                     "Position-bias model $e(R) = R^{-\\eta}$ and inverse-propensity "
                     "correction."),
    "agarwal2019": ("Récolte d'interventions : estimer la sévérité sans expérience.",
                    "Intervention harvesting: estimating severity without an experiment."),
    "swaminathan2015": ("Estimateur auto-normalisé, employé dans les comparaisons.",
                        "The self-normalised estimator, used in the comparisons."),
    "vardasbi2020": ("Biais de confiance et modèle affine : démontre que l'IPS ne peut pas le "
                     "corriger, et fournit la contre-épreuve du notebook 20.",
                     "Trust bias and the affine model: proves IPS cannot correct it, and "
                     "provides notebook 20's counter-test."),
    "hager2024": ("Sur le jeu même où ce dépôt mesure $\\hat\\eta = 1{,}10$ : corriger le biais "
                  "de position n'améliore pas le classement.",
                  "On the very dataset where this repository measures $\\hat\\eta = 1.10$: "
                  "correcting position bias does not improve ranking."),
    "wu2020": ("MIND, dont ce dépôt établit que l'ordre enregistré est mélangé.",
               "MIND, whose recorded order this repository shows to be shuffled."),
    "zou2022": ("Baidu-ULTR, le contrôle positif du test d'échangeabilité.",
                "Baidu-ULTR, the exchangeability test's positive control."),
    "saito2020": ("Open Bandit Dataset : propensions vraies et seau aléatoire, seule "
                  "confrontation à une vérité terrain.",
                  "Open Bandit Dataset: true propensities and a random bucket, the only "
                  "confrontation with a ground truth."),
    "vandrunen2025": ("Établit avant nous que les jeux publics sont le goulot d'étranglement, "
                      "et le droit européen la voie d'accès.",
                      "Establishes before us that public datasets are the bottleneck, and "
                      "European law the route to access."),
    "dsa2022": ("Cadre réglementaire : risques systémiques (art. 34) et accès aux données "
                "(art. 40).",
                "Regulatory framework: systemic risks (Art. 34) and data access (Art. 40)."),
    "delegue2025": ("Procédure opérationnelle de la demande d'accès aux données.",
                    "Operational procedure for the data access request."),
}

#: Liens vérifiés. Une référence sans lien connu n'en reçoit pas : inventer un DOI serait pire
#: que de n'en donner aucun.
LINKS: dict[str, str] = {
    "carbonell1998": "https://doi.org/10.1145/290941.291025",
    "steck2018": "https://doi.org/10.1145/3240323.3240372",
    "ohsaka2023": "https://arxiv.org/abs/2305.13801",
    "vrijenhoek2022": "https://arxiv.org/abs/2209.13520",
    "joachims2017": "https://doi.org/10.1145/3018661.3018699",
    "swaminathan2015": "https://papers.nips.cc/paper/2015/hash/39027dfad5138c9ca0c474d71db915c3-Abstract.html",
    "vardasbi2020": "https://arxiv.org/abs/2008.10242",
    "hager2024": "https://arxiv.org/abs/2404.02543",
    "wu2020": "https://aclanthology.org/2020.acl-main.331/",
    "zou2022": "https://arxiv.org/abs/2207.03051",
    "saito2020": "https://arxiv.org/abs/2008.07146",
    "vandrunen2025": "https://arxiv.org/abs/2510.05952",
    "dsa2022": "https://eur-lex.europa.eu/eli/reg/2022/2065/oj",
    "delegue2025": "https://eur-lex.europa.eu/eli/reg_del/2025/2050/oj",
}


def parse_bib(text: str) -> dict[str, dict[str, str]]:
    """Lit un fichier BibTeX simple : une entrée par ``@type{clé, champ = {valeur}, …}``."""
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"@(\w+)\{([^,]+),", text):
        key = match.group(2).strip()
        start = match.end()
        depth, index = 1, match.start(0) + len(match.group(0)) - 1
        while depth and index < len(text):
            index += 1
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
        body = text[start:index]
        fields = {name.strip().lower(): re.sub(r"\s+", " ", value).strip()
                  for name, value in re.findall(r"(\w+)\s*=\s*\{(.*?)\}\s*(?:,|$)", body, re.S)}
        fields["type"] = match.group(1).lower()
        entries[key] = fields
    return entries


def clean(value: str) -> str:
    """Retire les accolades de protection BibTeX et les commandes les plus courantes."""
    value = value.replace("\\textsuperscript{er}", "er").replace("--", "–")
    value = re.sub(r"\{\\'([a-z])\}", lambda m: {"e": "é", "a": "á", "o": "ó"}[m.group(1)], value)
    return value.replace("{", "").replace("}", "")


def format_entry(key: str, fields: dict[str, str]) -> str:
    authors = clean(fields.get("author", "")).replace(" and ", " ; ")
    title = clean(fields.get("title", ""))
    year = fields.get("year", "")
    venue = clean(fields.get("journal") or fields.get("booktitle") or
                  fields.get("howpublished") or "")
    pieces = [f"**{authors}** ({year}). *{title}*"]
    if venue:
        pieces.append(venue)
    if "volume" in fields:
        pieces.append(f"vol. {fields['volume']}" + (f"({fields['number']})"
                                                    if "number" in fields else ""))
    if "pages" in fields:
        pieces.append(f"p. {clean(fields['pages'])}")
    reference = ", ".join(pieces) + "."
    if key in LINKS:
        reference += f" [→]({LINKS[key]})"
    return reference


HEADERS = {
    "fr": """# Bibliographie

Toutes les références sur lesquelles ce travail s'appuie, avec **ce que chacune y sert**. Une
référence sans usage identifiable n'appartient pas à une bibliographie mais à une liste de
lectures.

Cette page est **dérivée** de `paper/refs.bib`, le fichier que compilent les deux notes : les
deux ne peuvent pas diverger, et un test le vérifie. Elle se régénère par
`docker compose run --rm lab python scripts/build_bibliography.py`.
""",
    "en": """# Bibliography

Every reference this work rests on, together with **what each is used for here**. A reference
with no identifiable use belongs to a reading list, not to a bibliography.

This page is **derived** from `paper/refs.bib`, the file both notes compile: the two cannot
diverge, and a test checks it. Regenerate with
`docker compose run --rm lab python scripts/build_bibliography.py`.
""",
}

FOOTERS = {
    "fr": """
---

*Source : `paper/refs.bib` · les deux notes de synthèse citent ces mêmes entrées ·
[audit critique](limites.md) · [appel à relecture](relecture.md)*
""",
    "en": """
---

*Source: `paper/refs.bib` · both synthesis notes cite these same entries ·
[critical audit](limites.en.md) · [call for review](relecture.md)*
""",
}


def render(entries: dict[str, dict[str, str]], language: str) -> str:
    lines = [HEADERS[language]]
    seen: set[str] = set()
    for keys, title_fr, title_en in THEMES:
        lines.append(f"\n## {title_fr if language == 'fr' else title_en}\n")
        for key in keys:
            if key not in entries:
                raise KeyError(f"référence absente de refs.bib : {key}")
            seen.add(key)
            use = USES[key][0 if language == "fr" else 1]
            lines.append(f"- {format_entry(key, entries[key])}  \n  {use}")
        lines.append("")
    missing = set(entries) - seen
    if missing:
        raise KeyError(f"références non classées : {sorted(missing)}")
    lines.append(FOOTERS[language])
    return "\n".join(lines)


def build() -> dict[Path, str]:
    """Rend les deux pages, sans les écrire — c'est ce que le test compare."""
    entries = parse_bib(BIB_PATH.read_text(encoding="utf-8"))
    return {DOCS / "bibliographie.md": render(entries, "fr"),
            DOCS / "bibliographie.en.md": render(entries, "en")}


def main() -> int:
    for path, content in build().items():
        path.write_text(content, encoding="utf-8")
        print(f"Écrit : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
