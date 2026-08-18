"""Validation de l'annotation manuelle du registre.

Aucun test n'accède au réseau. Ce qui est vérifié ici, c'est la **mécanique du codage** :
le rejet des étiquettes hors grille, l'exclusion des sujets codés « ni l'un ni l'autre »,
et surtout le fait qu'une annotation ne se relise que sous la grille qui l'a produite. Un
corpus réétiqueté silencieusement par une grille différente serait indétectable à l'œil.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ide.annotation import (
    ACCUSATION,
    ANNOTATIONS_PATH,
    CONFIDENCES,
    CONTAMINATED,
    DISCOVERY,
    EXTRACTS_PATH,
    KINDS,
    NEITHER,
    REGISTERS,
    REPLICATION_PATH,
    RUBRIC_VERSION,
    Annotation,
    annotated_entries,
    cohen_kappa,
    confusion_matrix,
    consensus_registers,
    digest_extracts,
    fleiss_kappa,
    load_annotations,
    load_extracts,
    load_replication,
    save_annotations,
    save_extracts,
)
from ide.catalogue import load_catalogue
from ide.corpus import CorpusEntry


def _entry(label: str, category: str) -> CorpusEntry:
    return CorpusEntry(
        project="en.wikipedia", article=label.replace(" ", "_"), label=label, category=category
    )


class TestAnnotation:
    def test_rejects_a_register_outside_the_rubric(self) -> None:
        with pytest.raises(ValueError, match="registre"):
            Annotation("X", "scandale", "event")

    def test_rejects_an_unknown_kind(self) -> None:
        with pytest.raises(ValueError, match="type"):
            Annotation("X", ACCUSATION, "affaire")

    def test_rejects_an_unknown_confidence(self) -> None:
        with pytest.raises(ValueError, match="confiance"):
            Annotation("X", ACCUSATION, "event", confidence="peut-être")

    def test_the_third_register_is_what_the_annotation_adds(self) -> None:
        """Sans « ni l'un ni l'autre », l'annotation ne corrigerait aucun bruit."""
        assert NEITHER in REGISTERS
        assert set(REGISTERS) == {ACCUSATION, DISCOVERY, NEITHER}


class TestRoundTrip:
    def test_annotations_survive_a_write_and_read(self, tmp_path: Path) -> None:
        annotations = [
            Annotation("A", ACCUSATION, "event", note="scandale"),
            Annotation("B", DISCOVERY, "object", confidence="unsure"),
        ]
        path = tmp_path / "annotations.json"

        save_annotations(annotations, "abc", path=path)
        reloaded = load_annotations(path=path)

        assert set(reloaded) == {"A", "B"}
        assert reloaded["B"].confidence == "unsure"
        assert reloaded["A"].note == "scandale"

    def test_a_foreign_rubric_is_refused(self, tmp_path: Path) -> None:
        """Deux grilles ne se mélangent pas : le codage n'aurait plus de définition."""
        path = tmp_path / "annotations.json"
        save_annotations([Annotation("A", ACCUSATION, "event")], "abc", path=path)
        payload = json.loads(path.read_text())
        payload["rubric_version"] = "0.9"
        path.write_text(json.dumps(payload))

        with pytest.raises(ValueError, match="grille"):
            load_annotations(path=path)

    def test_the_extract_digest_is_recorded(self, tmp_path: Path) -> None:
        """On doit pouvoir savoir de quel texte exact un codage provient."""
        extracts = tmp_path / "extracts.json"
        save_extracts({"A": "un chapeau"}, path=extracts)

        assert digest_extracts(path=extracts) == digest_extracts(path=extracts)
        assert load_extracts(path=extracts) == {"A": "un chapeau"}

    def test_missing_files_are_not_regenerated(self, tmp_path: Path) -> None:
        """Une annotation manuelle ne se recalcule pas à la volée."""
        with pytest.raises(FileNotFoundError):
            load_annotations(path=tmp_path / "absent.json")
        with pytest.raises(FileNotFoundError):
            load_extracts(path=tmp_path / "absent.json")


class TestRelabelling:
    def test_the_hand_label_replaces_the_category_label(self) -> None:
        entries = [_entry("A", "accusation")]
        annotations = {"A": Annotation("A", DISCOVERY, "person")}

        assert annotated_entries(entries, annotations)[0].category == DISCOVERY

    def test_subjects_coded_neither_are_removed(self) -> None:
        entries = [_entry("A", "accusation"), _entry("B", "accusation")]
        annotations = {
            "A": Annotation("A", ACCUSATION, "event"),
            "B": Annotation("B", NEITHER, "work", note="fiction"),
        }

        assert [e.label for e in annotated_entries(entries, annotations)] == ["A"]

    def test_the_comparable_registers_keep_their_invariant(self) -> None:
        """`CorpusEntry` n'admet que les deux registres comparables ; « neither » n'en est pas."""
        with pytest.raises(ValueError, match="catégorie"):
            _entry("B", NEITHER)

    def test_an_unannotated_subject_is_dropped(self) -> None:
        entries = [_entry("A", "accusation"), _entry("B", "discovery")]

        assert annotated_entries(entries, {"A": Annotation("A", ACCUSATION, "event")}) != []
        assert len(annotated_entries(entries, {"A": Annotation("A", ACCUSATION, "event")})) == 1

    def test_the_confusion_matrix_counts_the_labelling_noise(self) -> None:
        entries = [_entry("A", "accusation"), _entry("B", "accusation")]
        annotations = {
            "A": Annotation("A", ACCUSATION, "event"),
            "B": Annotation("B", NEITHER, "work"),
        }

        matrix = confusion_matrix(entries, annotations)

        assert matrix["accusation"][ACCUSATION] == 1
        assert matrix["accusation"][NEITHER] == 1


@pytest.mark.skipif(not ANNOTATIONS_PATH.exists(), reason="annotations non encore produites")
class TestDeliveredAnnotations:
    """Contrôles sur le fichier réellement livré."""

    def test_every_catalogued_subject_is_annotated(self) -> None:
        """Annoter un sous-ensemble choisi rouvrirait le biais que l'annotation corrige."""
        entries, _ = load_catalogue()
        annotations = load_annotations()

        missing = [entry.label for entry in entries if entry.label not in annotations]

        assert missing == [], f"{len(missing)} sujets non annotés"

    def test_the_recorded_digest_matches_the_extracts(self) -> None:
        payload = json.loads(ANNOTATIONS_PATH.read_text())

        assert payload["extracts_sha256"] == digest_extracts(EXTRACTS_PATH)

    def test_both_registers_and_the_discard_are_represented(self) -> None:
        counts = {register: 0 for register in REGISTERS}
        for annotation in load_annotations().values():
            counts[annotation.register] += 1

        assert all(count > 0 for count in counts.values()), counts

    def test_uncertain_annotations_carry_a_note(self) -> None:
        """Un cas limite sans justification ne se relit pas."""
        unjustified = [
            annotation.title
            for annotation in load_annotations().values()
            if annotation.confidence == "unsure" and not annotation.note
        ]

        assert unjustified == []

    def test_declared_contamination_is_annotated_like_the_rest(self) -> None:
        """Les sujets dont le résultat était connu ne sont pas écartés, mais tracés."""
        annotations = load_annotations()
        known = [title for title in CONTAMINATED if title in annotations]

        assert known, "aucun sujet contaminé retrouvé — la liste est-elle à jour ?"

    def test_the_kinds_used_belong_to_the_rubric(self) -> None:
        used = {annotation.kind for annotation in load_annotations().values()}

        assert used <= set(KINDS)

    def test_the_published_labelling_noise_is_the_measured_one(self) -> None:
        """Les chiffres publiés dans `docs/annotation.md` doivent rester ceux du manifeste.

        C'est un garde-fou contre une régénération silencieuse : le taux de bruit
        d'étiquetage est le résultat central de la page, et rien dans une liste de 440
        annotations ne signalerait qu'il a bougé.
        """
        entries, _ = load_catalogue()
        annotations = load_annotations()

        neither = sum(1 for a in annotations.values() if a.register == NEITHER)
        agreement = sum(1 for e in entries if annotations[e.label].register == e.category)

        assert neither == 175, "40 % de sujets hors registre — chiffre publié"
        assert agreement == 262, "59,5 % d'accord catégorie/annotation — chiffre publié"

    def test_the_category_almost_never_assigns_the_wrong_register(self) -> None:
        """Le bruit dilue sans biaiser : c'est ce qui rend le résultat nul interprétable."""
        entries, _ = load_catalogue()
        annotations = load_annotations()

        reversed_register = [
            e.label for e in entries
            if annotations[e.label].register not in (e.category, NEITHER)
        ]

        assert len(reversed_register) <= 5, reversed_register

    def test_the_rubric_version_is_the_current_one(self) -> None:
        payload = json.loads(ANNOTATIONS_PATH.read_text())

        assert payload["rubric_version"] == RUBRIC_VERSION
        assert set(CONFIDENCES) == {"sure", "unsure"}


class TestAgreement:
    """Accord entre codeurs, corrigé du hasard."""

    def test_perfect_agreement_gives_one(self) -> None:
        labels = [ACCUSATION, DISCOVERY, NEITHER, ACCUSATION]

        assert cohen_kappa(labels, list(labels)) == pytest.approx(1.0)

    def test_chance_level_agreement_gives_about_zero(self) -> None:
        """Deux codeurs qui tirent indépendamment doivent tomber près de zéro, pas près de 1.

        C'est ce que la correction du hasard achète : sur un corpus déséquilibré, l'accord
        brut reste élevé sans qu'aucune compétence soit en jeu.
        """
        first = [ACCUSATION] * 80 + [DISCOVERY] * 20
        second = [ACCUSATION] * 80 + [DISCOVERY] * 20
        second = second[16:] + second[:16]

        assert abs(cohen_kappa(first, second)) < 0.15

    def test_systematic_disagreement_goes_negative(self) -> None:
        first = [ACCUSATION, DISCOVERY] * 20
        second = [DISCOVERY, ACCUSATION] * 20

        assert cohen_kappa(first, second) < 0.0

    def test_mismatched_lengths_are_refused(self) -> None:
        with pytest.raises(ValueError, match="mêmes sujets"):
            cohen_kappa([ACCUSATION], [ACCUSATION, DISCOVERY])

    def test_a_single_label_is_a_degenerate_agreement(self) -> None:
        with pytest.raises(ValueError, match="dégénéré"):
            cohen_kappa([ACCUSATION] * 5, [ACCUSATION] * 5)

    def test_fleiss_matches_cohen_on_two_coders(self) -> None:
        """Les deux mesures ne coïncident pas exactement, mais doivent rester voisines."""
        first = [ACCUSATION, DISCOVERY, NEITHER, ACCUSATION, NEITHER, DISCOVERY] * 8
        second = [ACCUSATION, DISCOVERY, NEITHER, NEITHER, NEITHER, DISCOVERY] * 8

        assert fleiss_kappa([first, second]) == pytest.approx(cohen_kappa(first, second), abs=0.1)

    def test_fleiss_needs_at_least_two_coders(self) -> None:
        with pytest.raises(ValueError, match="deux codeurs"):
            fleiss_kappa([[ACCUSATION, DISCOVERY]])

    def test_the_consensus_follows_the_majority(self) -> None:
        codings = [
            {"A": Annotation("A", ACCUSATION, "event")},
            {"A": Annotation("A", ACCUSATION, "event")},
            {"A": Annotation("A", NEITHER, "work")},
        ]

        assert consensus_registers(codings) == {"A": ACCUSATION}

    def test_the_consensus_keeps_only_shared_subjects(self) -> None:
        codings = [
            {"A": Annotation("A", ACCUSATION, "event"), "B": Annotation("B", NEITHER, "work")},
            {"A": Annotation("A", ACCUSATION, "event")},
        ]

        assert set(consensus_registers(codings)) == {"A"}


@pytest.mark.skipif(not REPLICATION_PATH.exists(), reason="recodages non encore produits")
class TestDeliveredReplication:
    def test_every_coder_covers_the_whole_catalogue(self) -> None:
        entries, _ = load_catalogue()
        titles = {entry.label for entry in entries}

        for coder, coding in load_replication().items():
            assert set(coding) == titles, coder

    def test_the_recorded_digest_matches_the_extracts(self) -> None:
        """Les recodages doivent porter sur le même matériau que le codage initial."""
        payload = json.loads(REPLICATION_PATH.read_text())

        assert payload["extracts_sha256"] == digest_extracts(EXTRACTS_PATH)

    def test_agreement_on_the_register_is_the_published_one(self) -> None:
        annotations = load_annotations()
        replication = load_replication()
        titles = sorted(annotations)
        first = [annotations[t].register for t in titles]

        for coding in replication.values():
            kappa = cohen_kappa(first, [coding[t].register for t in titles])
            assert 0.85 <= kappa <= 0.95, kappa

    def test_the_three_way_agreement_is_the_published_one(self) -> None:
        annotations = load_annotations()
        replication = load_replication()
        titles = sorted(annotations)
        codings = [[annotations[t].register for t in titles]]
        codings += [[coding[t].register for t in titles] for coding in replication.values()]

        assert fleiss_kappa(codings) == pytest.approx(0.921, abs=0.01)

    def test_disagreements_almost_never_swap_the_two_compared_registers(self) -> None:
        """Le résultat structurel : l'ambiguïté porte sur l'appartenance, non sur le registre.

        Un désaccord entre `accusation` et `discovery` changerait le sens de la comparaison.
        Un désaccord avec `neither` n'en change que l'effectif.
        """
        annotations = load_annotations()
        codings = [{t: a.register for t, a in annotations.items()}]
        codings += [{t: a.register for t, a in c.items()} for c in load_replication().values()]

        swaps = sum(
            1 for title in annotations
            if {coding[title] for coding in codings} == {ACCUSATION, DISCOVERY}
            or {coding[title] for coding in codings} >= {ACCUSATION, DISCOVERY}
        )

        assert swaps <= 3, swaps
