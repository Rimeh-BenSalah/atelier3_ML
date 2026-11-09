
"""Classer une capture d'ecran avec un modele de vision.

Utilisation :
    python vision.py ../data/captures/I06.png
"""

import base64
import json
import os
import sys
from pathlib import Path

from groq import Groq
from evaluation import CATEGORIES

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
MODELE_VISION = "qwen/qwen3.8-27b"

CONSIGNE_IMAGE = """Un client du service client a envoyé cette capture d'écran pour illustrer son problème.
Classe-la dans exactement une catégorie parmi : facturation, technique, compte, commercial.

Définitions :
- facturation : un montant, une facture, un paiement, un remboursement.
- technique : un service qui ne fonctionne pas comme prévu.
- compte : l'accès au compte ou les données personnelles.
- commercial : le choix d'une offre, un abonnement, une résiliation.

Si la capture montre une erreur technique (code d'erreur, page qui ne charge pas,
application qui plante), choisis technique, même sur une page de paiement ou d'offre.

Réponds uniquement par un objet JSON de la forme {"categorie": "<une des quatre>"}."""


def data_url(chemin):
    """Transforme une image en texte base64."""
    octets = Path(chemin).read_bytes()

    type_mime = (
        "image/png"
        if str(chemin).lower().endswith(".png")
        else "image/jpeg"
    )

    image_encodee = base64.b64encode(octets).decode("ascii")

    return f"data:{type_mime};base64,{image_encodee}"


def classer_image(chemin, modele=MODELE_VISION, consigne=CONSIGNE_IMAGE):
    """Envoie la capture au modèle et renvoie une catégorie."""

    image = data_url(chemin)

    reponse = client.chat.completions.create(
        model=modele,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": consigne
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image
                        }
                    }
                ]
            }
        ]
    )

    brut = reponse.choices[0].message.content

    try:
        categorie = json.loads(brut).get("categorie", "")
    except (json.JSONDecodeError, AttributeError):
        return "invalide"

    categorie = str(categorie).strip().lower()

    if categorie in CATEGORIES:
        return categorie

    return "invalide"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage : python vision.py <capture.png>")

    try:
        print(classer_image(sys.argv[1]))
    except Exception as erreur:
        print(f"Erreur : {erreur}")
