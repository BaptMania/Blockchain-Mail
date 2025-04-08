import json
import random as r
import miner as m


def run():
    """
        Procédure permettant d'exécuter un mineur.
        Ce code est mis en procédure pour pouvoir être exécuté en même temps que le code de l'affichage dans le fichier program.py
        :return: None si tout s'est déroulé sans accroc
        :rtype: None
    """
    #   Choix aléatoire de l'argent initial du mineur
    quantity = r.randint(100, 10000)
    #   Création du mineur
    miner = m.Miner(identifier="bc2.info0903",
                    mail="bc2.info0903@gmail.com",
                    balance=quantity)

    #   Recherche et ajout des mineurs connus depuis le fichier contenant les mails des autres mineurs
    json_miners = json.load(open("listMail.json", "r"))
    for json_miner in json_miners:
        miner + json_miner["mail"][:-10]

    #   Éxécution du mineur
    miner.start()
    #   En attente de l'arrêt du mineur
    miner.join()


if __name__ == "__main__":
    run()


