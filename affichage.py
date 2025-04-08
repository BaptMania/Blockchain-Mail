import json
import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Autorise toutes les origines pour les requêtes CORS
socketio = SocketIO(app, cors_allowed_origins="*")


def blockchain_research():
    """
        Fonction permettant de récupérer tous les block des différentes blockchains existantes
        :return: Retourne les blockchains de chaque mineur
        :rtype: dict
    """
    directory = "Miner_Zone/"
    if os.path.exists(directory):
        #   On récupère les dossiers de chaque mineur existant
        #       On récupère chaque fichier et dossier du répertoire Miner_Zone
        l_directories_and_files_in_directory = os.listdir(directory)
        #       On ne récupère que les dossiers du répertoire Miner_Zone
        l_directories_in_directory = [miner_directory for miner_directory in l_directories_and_files_in_directory if os.path.isdir(os.path.join(directory, miner_directory))]
        #       On ne récupère que les dossiers qui ont des fichiers à l'intérieur (donc des mineurs avec une blockchain)
        l_miners_directories = [json_block for json_block in l_directories_in_directory if len(os.listdir(directory + json_block)) > 0]
        #       On crée un dictionnaire contenant chaque mineur pour pouvoir associer chaque blockchain à son mineur
        dict_miners_with_blockchain = {miner: [] for miner in l_miners_directories}
        #   On récupère les données JSON de chaque block trouvé dans le dossier de chaque mineur
        for miner_directory in l_miners_directories:
            l_miners_json_blocks = os.listdir(directory + miner_directory)
            for miner_block in l_miners_json_blocks:
                with open(os.path.join(directory, miner_directory, miner_block), 'r') as json_block:
                    try:
                        block = json.load(json_block)
                        block["miner"] = miner_directory

                        dict_miners_with_blockchain[miner_directory].append(block)
                    except json.JSONDecodeError as error:
                        print(f"Erreur de décodage JSON : {error}")
        return dict_miners_with_blockchain


@app.route('/')
def index():
    """
        Fonction permettant de rendre sous un certain template l'interface.
        :return: Le template de l'interface index.html
        :rtype: str
    """
    return render_template('interface.html')


@app.route('/l_blocks', methods=['GET'])
def get_rectangles_and_text():
    """
        Fonction permettant d'envoyer à l'interface WEB les informations des différentes blockchains
        :return jsonify(l_blocks): Retourne les informations des blockchains
        :return jsonify({"error": "Une erreur s'est produite lors de la récupération des données."}), 500: Renvoi un code d'erreur s'il y a un problème
        :rtype: Response
        :rtype: Response
    """
    try:
        l_interface_blocks = []

        dict_miners_blockchain = blockchain_research()
        #   Préparation de l'envoi des blocks sous le format nécessaire
        for miner, l_blocks in dict_miners_blockchain.items():
            for block in l_blocks:
                print("Block:", block)
                l_interface_blocks.append({
                    "miner": block.get("miner", ""),
                    "left": 50 * len(l_interface_blocks) + 50,
                    "top": 50 * len(l_interface_blocks) + 50,
                    "nonce": block.get("nonce", ""),
                    "previous_hash": block.get("previous_hash", ""),
                    "bounty": block.get("bounty", ""),
                    "founder": block.get("founder", "")
                })

        print('Données envoyées avec succès:', l_interface_blocks)

        return jsonify(l_interface_blocks)

    except Exception as e:
        print('Erreur lors de l\'envoi des données:', str(e))
        return jsonify({"error": "Une erreur s'est produite lors de la récupération des données."}), 500


def run():
    """
        Procédure permettant d'exécuter la partie serveur de l'interface.
        :return: Rien si tout se passe bien
        :rtype: None
    """
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run()
