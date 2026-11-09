
import re
from jiwer import wer as calculer_wer
from jiwer import process_words


def normaliser(texte):
    """Met le texte en minuscules et supprime la ponctuation."""
    texte = texte.lower()
    texte = texte.replace("€", " euros ")
    texte = re.sub(r"[^\w\s]", " ", texte)
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()


def wer(reference, transcription):
    """Calcule le Word Error Rate."""
    return calculer_wer(reference, transcription)


def detail(reference, transcription):
    """Retourne les détails du WER sous forme de dictionnaire."""
    resultat = process_words(reference, transcription)

    return {
        "wer": resultat.wer,
        "substitutions": resultat.substitutions,
        "deletions": resultat.deletions,
        "insertions": resultat.insertions,
        "hits": resultat.hits
    }


if __name__ == "__main__":
    reference = "Le prix est de 20 euros aujourd'hui."
    transcription = "Le prix est 20€ aujourd'hui"

    print("Référence :", reference)
    print("Transcription :", transcription)

    # WER brut
    brut = wer(reference, transcription)

    # WER après normalisation
    reference_norm = normaliser(reference)
    transcription_norm = normaliser(transcription)

    normalise = wer(reference_norm, transcription_norm)

    print(f"\nWER brut : {brut:.3f}")
    print(f"WER normalisé : {normalise:.3f}")

    # Affichage de l'alignement
    resultat = process_words(reference_norm, transcription_norm)

    print("\nAlignement des mots :")
    print(resultat)

    print("\nDétails :")
    print(detail(reference_norm, transcription_norm))
