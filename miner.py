import datetime
import datetime as dt
import hashlib
from threading import Thread
import os
import json
import block as b
import transaction as t
import blockchain
import smtplib
import email
import imaplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

#   Identifiants permettant de se connecter à son adresse mail pour pouvoir broadcast les blocks trouvés
PRIVATE_MAIL = json.load(open("private.json", "r"))
#   Liste des mails des mineurs connus
LIST_MAIL = json.load(open("listMail.json", "r"))


def envoi_mail(
        blockchain_json: json,
        private_mail: dict,
        list_mail: list
) -> None:
    """
        Procédure qui permet d'envoyer un mail à tous les utilisateurs de la blockchain
        :param blockchain_json : Blockchain au format JSON
        :param private_mail : Dictionnaire contenant le mail et mot de passe de l'expéditeur
        :param list_mail : Dictionnaire contenant la liste des mails des utilisateurs de la blockchain
        :type blockchain_json: json
        :type private_mail: dict
        :type list_mail: list
        :return: None si tout s'est bien déroulé
        :rtype: None
    """
    subject = "[Blockchain] Nouveau block"
    message = "J'ai trouvé un nouveau block, merci d'en prendre compte dans votre blockchain"

    # Connexion au serveur SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(private_mail["mail"], private_mail["password"])  # À modifier / déplacer => self.mail, self.password

    #   Création d'une mailList sans l'expéditeur
    mailList = []
    for mail in list(list_mail):
        if mail["mail"] != private_mail["mail"]:
            mailList.append(mail["mail"])

    # Créer un message MIME
    msg = MIMEMultipart('mixed')
    msg['from'] = private_mail["mail"]

    msg['To'] = ", ".join(mailList)  # ", ".join(mailList) => "mail1, mail2, mail3
    #   Opération nécessaire pour l'envoi de mail à plusieurs destinataires
    #   Permet de générer moins de traffic sur le serveur SMTP

    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    attachment = MIMEText(json.dumps(blockchain_json), 'json')
    attachment.add_header('Content-Disposition', 'attachment', filename=f"blockchain.json")
    msg.attach(attachment)

    #   Envoi de l'email
    server.sendmail(private_mail["mail"], mailList, msg.as_string())
    print(f"Mail envoyé à {mailList.__str__()}")
    server.quit()


def broadcast_blockchain(
        json_blockchain: list,
        identifiers: dict,
        known_miners: list
) -> None:
    """
        Procédure qui permet d'envoyer la blockchain par mail à tous les mineurs connus
        :param json_blockchain: La blockchain à envoyer (c'est censé être un JSON mais c'est une liste de blocks au format JSON).
        :param identifiers: Dictionnaire contenant les identifiants pour pouvoir envoyer un mail
        :param known_miners: Liste des mineurs connus
        :type json_blockchain: list
        :type identifiers: dict
        :type known_miners: list
        :return: None si tout s'est bien déroulé
        :rtype: None

        :Example:

        >>> import * from block
        >>> import * from transaction
        >>> mineur1 = Miner("mineur1", "mineur1@gmail.com", 50)
        >>> mineur1.broadcast_blockchain([
        >>>                                 {"nonce": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "previous_hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "bounty": 0, "transaction": {"sender": "mineur1", "receiver": "mineur2", "quantity": 0}, "founder": "mineur1", "date": "10/01/2024 10:34:12"},
        >>>                                 {"nonce": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "previous_hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "bounty": 0, "transaction": {"sender": "mineur1", "receiver": "mineur2", "quantity": 0}, "founder": "mineur1", "date": "10/01/2024 10:34:12"}
        >>>                              ],
        >>>                              {'mail': 'mineur1@gmail.com', 'password': 'abcd efgh ijkl mnop'},
        >>>                              ["mineur2"])
    """
    envoi_mail(json_blockchain, identifiers, known_miners)


class Miner(Thread):
    def __init__(
            self,
            identifier: str,
            mail: str,
            balance: int = 0
    ) -> None:
        """
            Une classe permettant de simuler un mineur recherchant des blocks pour alimenter sa blockchain.
            :param identifier: Équivaut à l\'identifiant du mineur. On considère que c\'est le corps de son adresse mail pour éviter les doublons ;
            :param mail: Équivaut à l\'adresse email du mineur ;
            :param balance: Équivaut à la valeur monétaire du mineur.
            :type identifier: str
            :type mail: str
            :type balance: int

            :Example:

            >>> Miner(identifier="exemple", mail="exemple@gmail.com", balance=50)

            .. seealso:: add(miner), run(), create_repositories(), create_nonce(block_info), mine_next_block(transaction), validate_block()\n

            Important
            ---------

            Cette classe est obligatoire pour le programme de simulation d'une blockchain.
        """
        super().__init__()
        self.id = identifier
        self.blockchain = blockchain.BlockChain()
        self.l_contact_miners = []
        self.balance = balance
        self.waiting_block = []
        self.l_transactions_to_add = []
        self.mail = mail
        self.previous_hash = "0"
        self.difficulty = 1
        self.time_last_block_mined = 0
        self.time_new_block_mined = 0

    def __add__(
            self,
            miner: str
    ) -> None:
        """
            Remaniement de la fonction intégrée de sommation ('a + b'). Permet d'ajouter un mineur b à la des mineurs connus du mineur a.
            :param miner: C'est l'identifiant du mineur à ajouter à la liste des mineurs connus.
            :type miner: str

            :Example:

            >>> miner1 = Miner(identifier="miner1", mail="miner1@gmail.com", balance=50)
            >>> miner2 = Miner(identifier="miner2", mail="miner2@gmail.com", balance=50)
            >>> miner1 += miner2
            >>> print(miner1.l_contact_miners)
            ["miner2"]
        """
        self.l_contact_miners.append(miner)

    def run(self) -> bool:
        """
            Fonction qui permet de faire fonctionner le mineur
            :return: True si le programme a bien fonctionné
            :rtype: bool
        """
        self.create_repositories()
        #   On retire l'identifiant du mineur dans sa liste de mineur connu
        try:
            self.l_contact_miners.remove(self.id)
        except ValueError:
            pass
        #   On génère une petite liste de transactions à réaliser pour commencer la blockchain
        for _ in range(10):
            if self.balance > 0:
                quantity = random.randint(0, self.balance)
                self.balance -= quantity
                transaction = t.Transaction(sender=self.id, receiver=self.l_contact_miners[random.randint(0, len(self.l_contact_miners) - 1)], quantity=quantity)
                self.l_transactions_to_add.append(transaction)
        #   Le mineur cherche des blocks en fonction des transactions qu'il a en mémoire
        print(self.id + " balance : " + str(self.get_balance()))
        while len(self.l_transactions_to_add) > 0:
            #   On essaie d'ajouter une nouvelle transaction à la liste des transactions du mineur
            add_transaction = random.randint(0, 10)
            if add_transaction > 8:
                quantity = random.randint(0, self.balance)
                self.balance -= quantity
                self.l_transactions_to_add.append(t.Transaction(sender=self.id, receiver=self.l_contact_miners[random.randint(0, len(self.l_contact_miners) - 1)], quantity=quantity))
                print("Ajout d'une transaction")
            #   On mine un nouveau block
            self.mine_next_block(transaction=self.l_transactions_to_add[0])
            if len(self.waiting_block) > 0:
                self.blockchain + self.waiting_block[len(self.waiting_block) - 1]
                self.waiting_block[len(self.waiting_block) - 1] = None
                broadcast_blockchain(self.blockchain.to_json(), PRIVATE_MAIL, LIST_MAIL)
                self.l_transactions_to_add = self.l_transactions_to_add[1:]
            self.read_email()
            self.validate_block()
            print(self.id + " balance : " + str(self.get_balance()))
        return True

    def create_repositories(self) -> None:
        """
            Procédure créant tous les dossiers nécessaires pour le bon déroulement de l'exécution d'un mineur
            :return: None si tout s'est bien déroulé
            :rtype: None
        """
        print("Création des répertoires importants.\n")
        miners_directory = "Miner_Zone/"
        if not os.path.exists(miners_directory):
            try:
                os.makedirs(miners_directory, exist_ok=False)
            except FileExistsError as directory_exist_error:
                print(f"Le dossier existe déjà : {directory_exist_error}")
        try:
            os.chdir(miners_directory)
        except FileNotFoundError as directory_not_found_error:
            print(f"Erreur, le dossier n'existe pas : {directory_not_found_error}")
            os.makedirs(miners_directory)
        if not os.path.exists(self.id):
            try:
                os.makedirs(self.id, exist_ok=False)
            except FileExistsError as directory_exist_error:
                print(f"Le dossier existe déjà : {directory_exist_error}")
        for miner in self.l_contact_miners:
            try:
                os.makedirs(miner)
            except FileExistsError as directory_exist_error:
                print(f"Le dossier existe déjà : {directory_exist_error}")

    #   On fera un "hachage" simple à réaliser
    def create_nonce(
            self,
            block_info: str
    ) -> str:
        """
            Fonction pour générer le nonce d'un block en fonction des informations de la transaction
            :param block_info: Contient toutes les informations à transformer en hash
            :type block_info: str
            :return: Retourne le nonce généré à partir de SHA256, devant contenir quatre 0 à la fin du hash
            :rtype: str
        """
        string_b = f"{block_info}"
        nonce = hashlib.sha256(string_b.encode()).hexdigest()
        objective = '0' * self.difficulty
        #   On regarde si les 4 derniers nombres sont bien des 0 sinon on réessaie
        #   On ne fait pas les 4 premiers du fait que les calculs soient bien plus longs
        while nonce[-self.difficulty:] != objective:
            block_info += "1"
            string_b = f"{block_info}"
            nonce = hashlib.sha256(string_b.encode()).hexdigest()
        return nonce

    def mine_next_block(
            self,
            transaction: t.Transaction
    ) -> None:
        """
            Procédure pour miner un nouveau block
            :param transaction: la transaction à mettre dans le block
            :type transaction: t.Transaction
            :return: None si tout s'est bien déroulé
            :rtype: None
        """
        self.time_last_block_mined = datetime.datetime.now()
        nonce = self.create_nonce(str(self.previous_hash) + str(transaction.get_sender()) + str(transaction.get_receiver()) + str(self.difficulty) + str(transaction))
        #   On regarde si on block a été broadcast
        if len(self.waiting_block) > 0 and self.waiting_block[len(self.waiting_block) - 1] is not None:
            #   On vérifie le block -- idéalement et dans un futur proche, la blockchain entière
            while nonce != self.waiting_block[len(self.waiting_block) - 1].get_nonce():
                nonce = self.create_nonce(str(self.previous_hash) + transaction.get_sender() + transaction.get_receiver() + str(self.difficulty) + str(transaction))
        #   Sinon, on génère un block à partir de la dernière transaction
        else:
            self.waiting_block.append(b.Block(nonce=nonce,
                                              transaction=transaction,
                                              founder=self.id,
                                              difficulty=self.difficulty,
                                              previous_hash=self.previous_hash))
            if len(self.waiting_block) > 0:
                print(self.waiting_block[len(self.waiting_block) - 1])
            self.previous_hash = nonce
            self.time_new_block_mined = datetime.datetime.now()
            #   On récupère le temps nécessité pour avoir miné ce block
            time = (self.time_new_block_mined - self.time_last_block_mined).total_seconds()
            if time < 5:
                if self.difficulty < 4:
                    self.difficulty += 1
            elif time > 15:
                if self.difficulty > 2:
                    self.difficulty -= 1
            #   On transforme le block en fichier JSON
            try:
                with open(str(dt.datetime.now().strftime(self.id + "/%d_%m_%Y-%H_%M_%S")) + ".json", "w") as json_file:
                    json.dump(self.waiting_block[len(self.waiting_block) - 1].to_json(), json_file)
                broadcast_blockchain(self.blockchain.to_json(), PRIVATE_MAIL, LIST_MAIL)
                # envoi_mail(self.blockchain.to_json(), private_mail, list_mail)
            except PermissionError as p_error:
                print(f"Le block existe déjà {p_error}")

    def validate_block(self) -> None:
        """
            Procédure qui permet de valider un block (procédure à modifier)
            :param block_to_validate: le block qu'il faut valider
            :type block_to_validate: b
            :return: None si tout s'est bien déroulé
            :rtype: None
        """
        for miner in self.l_contact_miners:
            if miner != self.id:
                json_blocks = os.listdir(miner + "/")
                if len(json_blocks) > 0:
                    for json_block in json_blocks:
                        print("Block à valider")
                        with open(miner + "/" + json_block, "r") as json_file:
                            block = json.load(json_file)
                            nonce = ""
                            difficulty = self.difficulty
                            self.difficulty = block["difficulty"]
                            transaction = t.Transaction(block["transaction"]["sender"], block["transaction"]["receiver"], block["transaction"]["quantity"])
                            # while nonce != block["nonce"]: Ne fonctionne pas
                            nonce = self.create_nonce(str(block["previous_hash"]) + str(transaction.get_sender()) + str(transaction.get_receiver()) + str(block["difficulty"]) + str(transaction))
                            self.difficulty = difficulty
                            print("Block validé")
                            print(nonce)
                            print(block["nonce"])

    def get_miner_id(self) -> str:
        """
            Fonction permettant de récupérer l'identifiant d'un mineur
            :return: L'identifiant du mineur
            :rtype: str
        """
        return self.id

    def reduce_balance(
            self,
            quantity: int
    ) -> None:
        """
            Procédure permettant de diminuer l'argent du mineur (probablement vouée à être supprimée)
            :param quantity: La quantité d'argent à soustraire
            :type quantity: int
            :return: None si tout s'est bien déroulé
            :rtype: None
        """
        self.balance -= quantity

    def read_email(self) -> None:
        """
            Procédure qui permet de recevoir les mails et de récupérer les fichiers JSON comportant les blockchains (à retravailler pour que ça fonctionne comme souhaité)
            :return: None si tout s'est bien déroulé
            :rtype: None
        """
        imap_server = 'imap.gmail.com'
        try:
            # Connexion au serveur IMAP
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(PRIVATE_MAIL["mail"], PRIVATE_MAIL["password"])

            # Sélectionner la boîte de réception
            mail.select('inbox')

            # Récupérer les emails non lus
            status, data = mail.search(None, '(SUBJECT "[Blockchain] Nouveau block")')
            mail_ids = data[0].split()
            # Récupérer les emails
            for e_id in mail_ids:
                _, data = mail.fetch(e_id, '(RFC822)')
                raw_email = data[0][1]

                msg = email.message_from_string(raw_email.decode("utf-8"))
                # print("msg", msg)
                message = str(msg)
                indice = message.find("Return-Path: ")
                if indice != -1:
                    block_mail = message[indice + 14:message.find(">", indice) - 10]
                    if block_mail not in self.l_contact_miners:
                        self.l_contact_miners.append(block_mail)
                    download_folder = block_mail + "/"
                    # Parcourt des différentes parties du mail
                    filename = "blockchain.json"
                    for part in msg.walk():
                        if part.get_content_subtype() == 'json':
                            filename = part.get_filename()
                            if filename:
                                download_path = os.path.join(download_folder, filename)
                                with open(download_path, 'wb') as fp:
                                    fp.write(part.get_payload(decode=True))
                    try:
                        #   On récupère la blockchain du mineur
                        with open(block_mail + "/" + filename, 'r') as json_block:
                            blocks = json.load(json_block)
                            #   On transforme chaque block de la blockchain en fichier JSON
                            for block in blocks:
                                with open(block_mail + "/" + block["date"] + ".json", "w") as json_file:
                                    json.dump(block, json_file)
                    except json.JSONDecodeError as error:
                        print(f"Erreur de décodage JSON : {error}")
                    if os.path.exists(block_mail + "/" + filename):
                        os.remove(block_mail + "/" + filename)
        except Exception as error:
            print(f"Erreur : {error}")
            traceback.print_exc()

    def get_balance(self) -> int:
        """
            Procédure qui permet de calculer l'argent restant d'un mineur.
            :return: L'argent restant du mineur
            :rtype: int
        """
        balance = self.balance
        l_contact_miners = self.l_contact_miners
        l_contact_miners.append(self.id)
        for miner in l_contact_miners:
            json_blocks = os.listdir(miner + "/")
            if len(json_blocks) > 0:
                for json_block in json_blocks:
                    with open(miner + "/" + json_block, "r") as json_file:
                        block = json.load(json_file)
                        if block["transaction"]["sender"] == self.id:
                            balance -= block["transaction"]["quantity"]
                        if block["transaction"]["receiver"] == self.id:
                            balance += block["transaction"]["quantity"]
        return balance
