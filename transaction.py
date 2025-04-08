class Transaction:
    def __init__(self, sender, receiver, quantity):
        """
            Une classe permettant de simuler une transaction d'un block d'une blockchain.
            :param sender: Équivaut à l\'identifiant du mineur qui envoie l'argent.
            :param receiver: Équivaut à l\'identifiant du mineur qui reçoit l'argent.
            :param quantity: Équivaut à la valeur monétaire du mineur de la transaction.
            :type sender: str
            :type receiver: str
            :type quantity: int

            :Example:

            >>> Transaction(sender="mineur1", receiver="mineur2", quantity=50)

            .. seealso:: str(), get_sender(), get_receiver(), get_quantity()\n

            Important
            ---------

            Cette classe est obligatoire pour le programme de simulation d'une blockchain.
        """
        super().__init__()
        self._sender = sender
        self._receiver = receiver
        self._quantity = quantity

    def __str__(self):
        """
            La méthode intégrée pour transtyper une variable en STRING.
            :return: La version STRING d'une transaction
            :rtype: str

            :Example:

            >>> transaction = Transaction(sender="mineur1", receiver="mineur2", quantity=50)
            >>> print(transaction)
            Sender: mineur1\t\tReceiver: mineur2\tQuantity t50
        """
        return f"Sender:\t\t\t{self._sender}\nReceiver:\t\t\t{self._receiver}\nQuantity:\t\t\t{self._quantity}"

    def get_sender(self):
        """
            Procédure pour obtenir l'identifiant de l'envoyeur dans une transaction.
            :return: L'identifiant de l'envoyeur
            :rtype: str
        """
        return self._sender

    def get_receiver(self):
        """
            Procédure pour obtenir l'identifiant du receveur dans une transaction.
            :return: L'identifiant du receveur
            :rtype: str
        """
        return self._receiver

    def get_quantity(self):
        """
            Procédure pour obtenir la valeur monétaire échangée dans une transaction.
            :return: La valeur monétaire échangée
            :rtype: int
        """
        return self._quantity
