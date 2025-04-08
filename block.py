import transaction as t
import json
import datetime as dt


class Block:
    def __init__(self, nonce, transaction, founder, difficulty, previous_hash=0):
        """
            Une classe permettant de simuler un block d'une blockchain.
            :param nonce: Équivaut à l\'identifiant du mineur qui envoie l'argent.
            :param transaction: Équivaut à l\'identifiant du mineur qui reçoit l'argent.
            :param founder: Équivaut à la valeur monétaire du mineur de la transaction.
            :param difficulty: Équivaut à la difficultée qui a été nécessaire au calcul du nonce.
            :param previous_hash:
            :type nonce: str
            :type transaction: t
            :type founder: str
            :type difficulty: int
            :type previous_hash: str

            :Example:

            >>> import * from transaction
            >>> Block("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            >>>       6,
            >>>       Transaction("mineur1",
            >>>                   "mineur2",
            >>>                   50),
            >>>       "mineur1",
            >>>       "0")

            .. seealso:: str(), get_nonce(), to_json()\n

            Important
            ---------

            Cette classe est obligatoire pour le programme de simulation d'une blockchain.
        """
        super().__init__()
        self._nonce = nonce
        self._previous_hash = previous_hash
        self._bounty = 6
        self._transaction = transaction
        self._founder = founder
        self._difficulty = difficulty

    def __str__(self):
        """
            La méthode intégrée pour transtyper une variable en STRING.
            :return: La version STRING d'un block
            :rtype: str

            :Example:

            >>> block = Block(nonce="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            >>>               transaction={sender="mineur1", receiver="mineur2", quantity=50},
            >>>               founder="mineur1",
            >>>               difficulty=4,
            >>>               previous_hash="0")
            >>> print(block)
            Nonce: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"\tBounty: 6\tTransaction:|Sender: "mineur1"|Receiver: mineur2|Quantity:50\tFounder: mineur1\tPrevious Hash: 0
        """
        return f"\nNonce:\t\t\t{self._nonce}\nBounty:\t\t\t{self._bounty}\nTransaction:\n|\tSender:\t\t{self._transaction.get_sender()}\n|\tReceiver:\t{self._transaction.get_receiver()}\n|\tQuantity:\t{self._transaction.get_quantity()}\nFounder:\t\t{self._founder}\nPrevious Hash:\t{self._previous_hash}\n"

    def get_nonce(self):
        """
            Procédure pour obtenir le nonce d'un block.
            :return: Le nonce
            :rtype: str
        """
        return self._nonce

    def to_json(self):
        """
            Permet de convertir un block au format JSON
            :return: Retourne un bloc au format JSON
            :rtype: json
        """
        return {
            "nonce": self._nonce,
            "previous_hash": self._previous_hash,
            "bounty": 6,
            "transaction": {
                "sender": self._transaction.get_sender(),
                "receiver": self._transaction.get_receiver(),
                "quantity": self._transaction.get_quantity()
            },
            "founder": self._founder,
            "difficulty": self._difficulty,
            "date": dt.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
        }


