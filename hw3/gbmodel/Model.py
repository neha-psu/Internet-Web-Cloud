class Model():
    def select(self):
        """
        Gets all entries from the database
        :return: Tuple containing all rows of database
        """
        pass

    def insert(self, name, email, phone, address, state, zip, country, amount,  message):
        """
        Inserts entry into database
        :param name: String
        :param email: String
        :param phone: Integer
        :param address: String
        :param state: String
        :param zip: Integer
        :param country: String
        :param amount: Integer
        :param message: String
        :return: none
        :raises: Database errors on connection and insertion
        """
        pass
