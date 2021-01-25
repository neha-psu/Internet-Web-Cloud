"""
A simple foodbank flask app.
ata is stored in a SQLite database that looks something like the following:

+---------+--------------+---------+--------+------+------+--------+------+--------+
| Name    | Email        | Phone   |Address | State| Zip  | Country|Amount| Message|
+=========+==============+===+=====+======--+------+------+--------+------+--------+
|  Neha Ag| neha@pdx.edu | 12345678| Port   | OR   | 97123|   US   |  100 |  Enjoy |
+---------+--------------+---------+--------+------+------+--------+------+--------+

This can be created with the following SQL (see bottom of this file):

    create table foodbank (name text, email text, phone int, address text, state text,\
         zip int, country text, amount int, message);

"""
from .Model import Model
import sqlite3
DB_FILE = 'entries.db'    # file for our Database

class model(Model):
    def __init__(self):
        # Make sure our database exists
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        try:
            cursor.execute("select count(rowid) from foodbank")
        except sqlite3.OperationalError:
            cursor.execute("create table foodbank (name text, email text, phone int, address text,\
             state text, zip int, country text, amount int, message)")
        cursor.close()

    def select(self):
        """
        Gets all rows from the database
        Each row contains: name, email, phone, address, state, zip, country, amount,  message
        :return: List of lists containing all rows of database
        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM foodbank")
        return cursor.fetchall()

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
        :return: True
        :raises: Database errors on connection and insertion
        """
        params = {'name':name, 'email':email, 'phone':phone,'address':address,'state':state,\
                'zip':zip,'country':country,'amount':amount,'message':message}
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("insert into foodbank (name, email, phone, address, state, zip, country, amount,  message)\
             VALUES (:name, :email, :phone, :address, :state, :zip, :country, :amount,  :message)", params)

        connection.commit()
        cursor.close()
        return True
