####################################################################
#     SERIES BOT- PAR Maxime                                       #
#      Version 0.01                                                #
#                                                                  #
#  bot en python qui rejoint un salon #series (peut etre changer)  #
#  et qui envoit des replique de series                            #
####################################################################
import irc.bot
from threading import Thread
from time import sleep
import random
from itertools import combinations
import sys

class BotDeSeries(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.admins = ["admin1", "admin2"]  # Liste des pseudos des administrateurs
        self.colors = {
            "Friends": "12",  # Bleu
            "Game of Thrones": "4",  # Rouge
            "Le Bureau des Légendes": "2",  # Bleu marine
            "Dix pour cent": "14",  # Gris foncé
            "H": "3",  # Vert
            "Les Revenants": "10",  # Cyan
            "Engrenages": "5",  # Marron
            "Baron Noir": "8"   # Jaune
        }
        self.donnees_series = {
            "Friends": [
                ("Ross", ["On était en pause!", "Tu es mon homard.", "Rien n'est jamais fini pour de bon, n'est-ce pas?"]),
                ("Chandler", ["Je pourrais porter plus de vêtements?", "Je ne suis pas très doué pour les conseils. Peut-être un commentaire sarcastique?", "Bing!"]),
                ("Monica", ["Bienvenue dans le monde réel! Ça fait mal, hein?", "Je sais faire cuire des bonbons!", "Je suis toujours la dernière à savoir!"]),
                ("Joey", ["Comment ça va ?", "Joey n’a pas faim!", "Pizza et bière, ça me va."]),
                ("Phoebe", ["Je sens que quelque chose de très bizarre est en train de se passer.", "Je n'ai pas de plan.", "Je joue parfois de la guitare."])
            ],
            "Game of Thrones": [
                ("Tyrion", ["Je bois et je sais des choses.", "Je suis le dieu du sein et du vin."]),
                ("Cersei", ["Quand tu joues au jeu des trônes, tu gagnes ou tu meurs.", "Jamais un roi n'est mort de boire du vin."]),
                ("Jon Snow", ["Je ne sais rien.", "Il n'y a rien de tel que la vue d'une femme nue."]),
                ("Daenerys", ["Je ne veux pas arrêter la roue, je veux briser la roue.", "Mes dragons mangent bien quand ils peuvent."]),
                ("Sansa", ["J'aimerais qu'il y ait quelque chose pour moi ici.", "Le Nord se souvient."])
            ],
            "Dix pour cent": [
                ("Andréa", ["Je vends du rêve, pas du mensonge.", "La vérité, c'est que dans ce métier personne ne sait jamais rien."]),
                ("Mathias", ["Dans ce métier, le plus difficile n'est pas de réussir mais de durer.", "On n'est pas dans le business de la sincérité."]),
                ("Hervé", ["Tout le monde sait que quand on peut avoir le beurre et l’argent du beurre...", "C'est un monde de requins."]),
                ("Camille", ["Parfois les rôles vous choisissent.", "La comédie, c'est souvent une affaire de timing."])
            ],
            "H": [
                ("Aymé", ["Moi, quand je dors, je ne bouge pas.", "Je suis hypermnésique, je me souviens de tout."]),
                ("Jamel", ["Docteur, vous êtes sûr que ça va faire mal?", "On est les champions!"]),
                ("Sabri", ["J'ai fait une connerie?", "C'est pas ma faute, chef!"])
            ],
            "Les Revenants": [
                ("Camille", ["Je ne suis pas morte, je suis là.", "Pourquoi tout le monde me regarde toujours comme ça?"]),
                ("Simon", ["Je ne sais pas ce qui m'est arrivé, je ne me souviens de rien.", "Je dois retrouver ma fille."]),
                ("Julie", ["On ne peut pas revenir en arrière.", "Je n'aurais jamais dû revenir."]),
                ("Victor", ["Pourquoi tout le monde me regarde toujours comme ça?", "J'entends des choses que les autres ne peuvent pas entendre."])
            ],
            "Engrenages": [
                ("Laure", ["C'est pas une vie que de vivre en se méfiant toujours.", "On n'est pas là pour se faire engueuler, on est là pour voir du rouge.", "La justice a ses raisons que la raison ignore."]),
                ("Gilou", ["On n'est pas là pour se faire engueuler, on est là pour voir du rouge.", "Tout est une question de timing."]),
                ("Joséphine", ["Parfois, on fait le mal pour faire le bien.", "Il n'y a pas de justice, il y a moi."]),
                ("Roban", ["La justice, c’est pas une question de loi, c’est une question de courage.", "On ne peut pas toujours être un héros."])
            ],
            "Baron Noir": [
                ("Philippe", ["En politique, ce qui est cru devient plus important que ce qui est vrai.", "La politique, c'est comme le judo : faut utiliser la force de l'adversaire.", "Tous les coups sont permis en politique."]),
                ("Amélie", ["Il faut parfois sacrifier l'arbre pour sauver la forêt.", "Les mensonges, c'est comme les empreintes digitales, ils nous suivent partout.", "On ne fait pas de politique avec de la morale, mais on n'en fait pas davantage sans."]),
                ("Rickwaert", ["La politique, c'est comme le judo : faut utiliser la force de l'adversaire.", "On joue gros, on gagne gros.", "Je ne recule devant rien pour gagner."]),
                ("Véronique", ["Les mensonges c'est comme les empreintes digitales, ils nous suivent partout.", "La vérité est une question de perspective."])
            ]
        }
        self.quotes_thread = Thread(target=self.send_quotes_periodically)
        self.quotes_thread.daemon = True
        self.quotes_thread.start()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel, "\x0302Bonjour ! Tapez !series pour voir la liste des séries.\x03")

    def on_pubmsg(self, c, e):
        nick = e.source.nick
        msg = e.arguments[0]
        if msg.strip() == "!restart":
            self.attempt_restart(c, nick)
        elif msg.strip() == "!series":
            self.list_series(c)
        elif msg.strip() == "!stop":
            self.attempt_stop(c, nick)

    def attempt_restart(self, connection, nick):
        if nick in self.admins:
            connection.privmsg(self.channel, f"\x0304Redémarrage du bot par {nick}...\x03")
            self.disconnect("Redémarrage demandé par l'administrateur.")
            self.reconnect()
        else:
            connection.privmsg(self.channel, f"\x0304Désolé, {nick}, vous n'avez pas l'autorisation de redémarrer le bot.\x03")

    def attempt_stop(self, connection, nick):
        if nick in self.admins:
            connection.privmsg(self.channel, f"\x0304Arrêt du bot par {nick}...\x03")
            self.disconnect("Arrêt demandé par l'administrateur.")
            sys.exit()
        else:
            connection.privmsg(self.channel, f"\x0304Désolé, {nick}, vous n'avez pas l'autorisation d'arrêter le bot.\x03")

    def list_series(self, connection):
        series_list = "\x0309Séries disponibles :\x03"
        for series, color in self.colors.items():
            series_list += f" \x03{color}{series}\x03 ---------------"
        connection.privmsg(self.channel, series_list)

    def send_quotes_periodically(self):
        while True:
            if self.connection.is_connected():
                series = random.choice(list(self.donnees_series.keys()))
                characters = self.donnees_series[series]
                
                for _ in range(2):  # Chaque personnage dira deux phrases
                    for character, quotes in characters:
                        quote = random.choice(quotes)
                        color = self.colors[series]
                        message = f"\x03{color}{series}\x03 - {character}: {quote}"
                        self.connection.privmsg(self.channel, message)
                    sleep(30)  # Pause entre chaque série de phrases d'un personnage
                sleep(60)  # Pause entre chaque itération (chaque série de répliques)
            else:
                print("Bot not connected, retrying in 60 seconds...")
                sleep(60)


    def reconnect(self):
        self.reconnect_delay = 30  
        while True:
            try:
                print("Reconnexion au serveur...")
                self.connect(self.server, self.port, self.nickname)
                self.start()
            except irc.client.ServerConnectionError:
                print("Échec de la reconnexion. Nouvelle tentative dans {} secondes...".format(self.reconnect_delay))
                sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 600)

def main():
    server = "irc.extra-cool.fr"
    port = 6667
    nickname = "BotDeSeries"
    channel = "#series"
    
    bot = BotDeSeries(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
