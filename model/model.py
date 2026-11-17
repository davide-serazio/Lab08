from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultato = []

        for distributore in self._distributori:
            somma = 0
            numero_prezzi = 0

            for prezzo in distributore.get_prezzi():
                if prezzo.data.month == mese:
                    somma += prezzo.prezzo_litro
                    numero_prezzi += 1

            media = somma / numero_prezzi
            risultato.append((distributore.nome, media))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # Caso terminale: sono stati completati tutti e 7 i giorni.
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for distributore in self._distributori:
            id_distributore = distributore.id
            costo_giorno = prezzi_settimana[id_distributore][giorno - 1] * 100

            if ultimo_distributore is not None and ultimo_distributore != id_distributore:
                costo_giorno += 5

            sequenza_parziale.append(id_distributore)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_distributore,
                costo_corrente + costo_giorno,
                prezzi_settimana
            )

            # Backtracking: annulla la scelta del giorno corrente.
            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}

        for distributore in self._distributori:
            prezzi_settimana[distributore.id] = [0] * 7

            for prezzo in distributore.get_prezzi():
                if prezzo.data.month == mese and prezzo.data.day <= 7:
                    giorno = prezzo.data.day
                    prezzi_settimana[distributore.id][giorno - 1] = prezzo.prezzo_litro

        return prezzi_settimana