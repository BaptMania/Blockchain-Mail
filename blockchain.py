class BlockChain:
    def __init__(self):
        """
            Une classe permettant de simuler une blockchain.

            :Example:

            >>> BlockChain()

            .. seealso:: add_block(block), add(block), len(), to_json()\n

            Important
            ---------

            Cette classe est obligatoire pour le programme de simulation d'une blockchain.
        """
        super().__init__()
        self._blocks = []
        self.block_number = 0

    def add_block(self, block):
        """
            Ajoute un block à la blockchain
            :param block: Le block à ajouter à la blockchain
            :type block: Block
        """
        self._blocks.append(block)

    def __add__(self, block):
        """
            Permet l'utilisation de l'opérateur '+' sur la blockchain pour ajouter un nouveau block.
            :param block: Le block à ajouter à la blockchain
            :type block: Block
        """
        self.add_block(block)

    def __len__(self):
        """
            Permet l'utilisation de la fonction len() sur la blockchain
            :return: Retourne le nombre de blocks dans la blockchain
            :rtype: int
        """
        return len(self._blocks)

    def to_json(self):
        """
            Permet de convertir la blockchain au format JSON
            :return: Retourne la blockchain au format JSON
            :rtype: json
        """
        return [block.to_json() for block in self._blocks]
