
"""Analyse la propagation des erreurs entre texte et voix.

Utilisation :
    python propagation.py whisper-large-v3-turbo
    python propagation.py whisper-large-v3-turbo auto
"""

import json
import sys
from pathlib import Path


RESULTATS = Path("resultats")


def propagation(vrais, texte, voix):
    """Répartit les tickets dans les quatre catégories."""

    if not (len(vrais) == len(texte) == len(voix)):
        raise ValueError("Les trois listes doivent avoir la même longueur.")

    cases = {
        "conserve": [],
        "perdu": [],
        "gagne": [],
        "deux_faux": []
    }

    for i in range(len(vrais)):
        texte_correct = texte[i] == vrais[i]
        voix_correcte = voix[i] == vrais[i]

        if texte_correct and voix_correcte:
            cases["conserve"].append(i)
        elif texte_correct and not voix_correcte:
            cases["perdu"].append(i)
        elif not texte_correct and voix_correcte:
            cases["gagne"].append(i)
        else:
            cases["deux_faux"].append(i)

    return cases


def charger_resultat(chemin):
    """Charge un fichier de résultats JSON."""

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}\n"
            "Lance d'abord les évaluations demandées."
        )

    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def afficher_tickets(titre, indices, ids, vrais, pred_texte,
                     pred_voix, textes, transcriptions):
    print(f"\n=== {titre} ({len(indices)} tickets) ===")

    if not indices:
        print("Aucun ticket dans cette catégorie.")
        return

    for i in indices:
        print(f"\nTicket : {ids[i]}")
        print(f"Catégorie réelle       : {vrais[i]}")
        print(f"Prédiction texte       : {pred_texte[i]}")
        print(f"Prédiction voix        : {pred_voix[i]}")
        print(f"Texte original         : {textes[i]}")
        print(f"Transcription Whisper  : {transcriptions[i]}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    modele = sys.argv[1]
    langue = sys.argv[2] if len(sys.argv) > 2 else "fr"

    etiquette = f"voix__{modele}__{langue}"

    fichier_texte = RESULTATS / "texte.json"
    fichier_voix = RESULTATS / f"{etiquette}.json"

    try:
        resultat_texte = charger_resultat(fichier_texte)
        resultat_voix = charger_resultat(fichier_voix)
    except FileNotFoundError as erreur:
        print(f"\nERREUR : {erreur}")
        return

    ids_texte = resultat_texte["ids"]
    ids_voix = resultat_voix["ids"]

    if ids_texte != ids_voix:
        print("ERREUR : les tickets des deux évaluations ne correspondent pas.")
        return

    vrais = resultat_texte["vrais"]
    pred_texte = resultat_texte["predits"]
    pred_voix = resultat_voix["predits"]
    textes = resultat_texte["textes"]
    transcriptions = resultat_voix["textes"]

    cases = propagation(vrais, pred_texte, pred_voix)

    print("\n======================================")
    print(" ANALYSE DE LA PROPAGATION DES ERREURS")
    print("======================================")
    print(f"Modèle Whisper : {modele}")
    print(f"Langue         : {langue}")
    print(f"Nombre de tickets : {len(ids_texte)}")

    noms = {
        "conserve": "CONSERVÉS",
        "perdu": "PERDUS À CAUSE DE LA VOIX",
        "gagne": "GAGNÉS GRÂCE À LA VOIX",
        "deux_faux": "DEUX PRÉDICTIONS FAUSSES"
    }

    print("\n=== BILAN ===")
    for cle, titre in noms.items():
        print(f"{titre:<32}: {len(cases[cle])}")

    afficher_tickets(
        "TICKETS PERDUS À CAUSE DE LA VOIX",
        cases["perdu"], ids_texte, vrais, pred_texte,
        pred_voix, textes, transcriptions
    )

    afficher_tickets(
        "TICKETS GAGNÉS GRÂCE À LA VOIX",
        cases["gagne"], ids_texte, vrais, pred_texte,
        pred_voix, textes, transcriptions
    )

    afficher_tickets(
        "TICKETS OÙ LES DEUX PRÉDICTIONS SONT FAUSSES",
        cases["deux_faux"], ids_texte, vrais, pred_texte,
        pred_voix, textes, transcriptions
    )

    print("\nAnalyse terminée.")


if __name__ == "__main__":
    main()
