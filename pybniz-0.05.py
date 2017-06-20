#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Pybniz
======

[Description en français ci-dessous]

Pybniz is a GUI frontend to launch many IBNIZ with differents sizes and 
positions, and include a tiny set editor and manager.

Pybniz allows to create IBNIZ sets and to launch multiples IBNIZ at differents
positions and sizes.

Pybniz comes with its own version of IBNIZ which had been modified for allow
new parameters (see ./ibniz -h) compiled for Linux only. In case of ibniz 
don't work, you can download the source on Github (see below) and recompile it.

The sets are writed in the folder 'sets/' in text format, the name of the file
is used for name the set. The first line '\ xyt:' is used for memorize the
position and the size of the window.

Prerequisites:
SDL1.2 library and Tkinter Python module:
- on Debian : sudo apt-get install libsdl1.2* python-tk

Last version of Pybniz    : https://github.com/alex-guy/Pybniz
Modified version of IBNIZ : https://github.com/alex-guy/IBNIZ

Author: Alexandre GUY <alex@euronode.com>
License: GPLv3

-- FR

Pybniz est une interface pour lancer plusieurs IBNIZ avec des tailles et des 
positions différentes, il inclut un éditeur et un gestionnaire minimaliste 
de sets.

Pybniz permet de créer des sets IBNIZ et de lancer IBNIZ en lui indiquant
la position de la fenetre et sa taille.

Pybniz embarque sa propre version de IBNIZ qui a été modifiée pour accepter 
de nouveaux paramètres (voir ./ibniz -h), et ne fonctionne de ce fait que 
sous Linux. Si IBNIZ ne fonctionne pas, tu peux télécharger les sources sur 
Github (voir ci-dessous) et les recompiler.

Les sets sont enregistrés dans le sous-répertoire 'sets/' en format texte, 
le nom du fichier est utilisé pour nommer le set. La première ligne '\ xyt:' 
est utilisée pour mémoriser la position et la taille de la fenêtre.

Pré-requis:
la librairie SDL1.2 et le module Python Tkinter:
- sur Debian : sudo apt-get install libsdl1.2* python-tk

Dernière version de Pybniz : https://github.com/alex-guy/Pybniz
Version modifiée de IBNIZ  : https://github.com/alex-guy/IBNIZ

Auteur: Alexandre GUY <alex@euronode.com>
Licence: GPLv3
"""

from Tkinter import *
from os.path import exists
from os import mkdir, listdir, chmod
from subprocess import Popen, check_output
from sys import platform
from re import search, sub, MULTILINE

VERSION = "0.05"
IBNIZPATH="./ibniz"
DEBUG = False
XMAX = 1600
YMAX = 1200
TAILLEMAX = 1000

class Pybniz(object):
    """La classe Pybniz démarre l'interface graphique, fournit les méthodes
de manipulations des sets, et lance IBNIZ avec les bonnes options"""

    def __init__(self):
        """Charge la liste des sets et configure la fenetre graphique"""
        self.listesets = []
        if not exists("sets"):
            mkdir("sets")
            with open('sets/demo','w') as fic:
                fic.write('d*')
        self.chargeListeSets()
        root = Tk()
        root.title("Pybniz "+VERSION)
        root.geometry("400x800")
        self.pybnizUI = PybnizUI(master=root, pybniz=self)
        self.pybnizUI.mainloop()

    def chargeListeSets(self):
        """Charge la liste des sets depuis le répertoire sets/"""
        self.listesets = sorted([v.replace('_', ' ') for v in listdir("sets")])

    def chargeSet(self, nomset):
        """Charge un set"""
        nomset = nomset.replace(' ', '_')
        with open('sets/'+nomset,'r') as fic:
            return fic.read()

    def sauveSet(self, nomset, texte, posx, posy, taille):
        """Sauve un set en enregistrant la position et la taille de la fenêtre"""
        if DEBUG: print "Sauvegarde du set", nomset, posx, posy, taille, texte
        nomset = nomset.replace(' ', '_')
        texte = texte.rstrip()
        result = search(r'\ xyt: ([0-9]+) ([0-9]+) ([0-9]+)',texte, MULTILINE)
        xyt = "%d %d %d" % (posx, posy, taille)
        if result:
            texte = sub(r'xyt: ([0-9]+) ([0-9]+) ([0-9]+)','xyt: '+xyt,texte)
        else:
            texte = r'\ xyt: ' + xyt + '\n\n' + texte
        if DEBUG: print "texte:", texte
        with open('sets/'+nomset,'w') as fic:
            return fic.write(texte)

    def ajouterSet(self, nomset):
        """Ajoute un nouveau set"""
        if DEBUG: print "Ajout du set", nomset
        if nomset not in self.listesets:
            self.listesets.append(nomset)

    def lanceIBNIZ(self, nomset, texte,posx, posy, taille):
        """Lance IBNIZ en indiquant le set, la position et la taille de la fenêtre"""
        if DEBUG: print "Lancement de IBNIZ avec le code", texte
        arguments = [IBNIZPATH,]
        if posx != 0 or posy != 0:
            if DEBUG: print "Nouvelle position:", posx, posy
            arguments.extend(['-x', str(posx), '-y', str(posy)])
        if taille != 512:
            if DEBUG: print "Nouvelle taille:", taille
            arguments.extend(['-s', str(taille)])
        arguments.extend(['-r', '-c', texte])
        process = Popen(arguments)


class PybnizUI(Frame):
    """La classe PybnizUI contient l'interface graphique et le code pour gérer les évènements"""

    def __init__(self, master=None, pybniz=None):
        """Appel de la méthode qui dessine l'interface graphique"""
        Frame.__init__(self, master, bg='grey')
        self.pybniz = pybniz
        self.pack()
        self.creerInterface()

    def creerInterface(self):
        """Dessine l'interface graphique"""
        # Le titre
        self.labelTitre = Label(self, text="Pybniz", padx=10, pady=10, font="Helvetica 24 bold", bg='grey')
        self.labelTitre.pack(pady=10)
        # Le label Nouveau Set
        self.LabelSet = Label(self, text="Nouveau Set", bg='grey')
        self.LabelSet.pack(pady=2)
        # Le nom du set
        self.nomset = StringVar()
        self.EntryNomSet = Entry(self, textvariable=self.nomset)
        self.EntryNomSet.pack(pady=2, padx=10, fill='x')
        # Le bouton ajouter
        self.boutonAjouter = Button(self, text="Ajouter un Set", command=self.clickAjouterSet, fg="blue")
        self.boutonAjouter.pack(pady=2)
        # Le label Sets
        self.LabelSets = Label(self, text="Sets", bg='grey')
        self.LabelSets.pack(pady=2)
        # La liste des Sets
        self.choix = StringVar()
        self.choix.set(self.pybniz.listesets[0])
        self.ListeSets = OptionMenu(self, self.choix, command=self.clickSet, *self.pybniz.listesets)
        self.ListeSets.pack(pady=2, padx=10, fill='x')
        # La zone d'affichage
        self.zoneAffichage=Text(self,font="Courier 16 bold",height=11,width=30)
        self.zoneAffichage.pack(pady=5, padx=10)
        self.zoneAffichage.bind("<FocusOut>", self.quitteZoneAffichage)
        # Le label Position
        self.LabelPosition = Label(self, text="Position (X et Y)", bg='grey')
        self.LabelPosition.pack(pady=2)
        # posx
        self.posx = IntVar()
        self.posx.set(0)
        #self.EntryPositionX = Entry(self, textvariable=self.posx)
        self.EntryPositionX = Scale(self, orient='horizontal', from_=0, to_=XMAX, variable=self.posx)
        self.EntryPositionX.pack(pady=2, padx=10, fill='x')
        # posy
        self.posy = IntVar()
        self.posy.set(0)
        #self.EntryPositionY = Entry(self, textvariable=self.posy)
        self.EntryPositionY = Scale(self, orient='horizontal', from_=0, to_=YMAX, variable=self.posy)
        self.EntryPositionY.pack(pady=2, padx=10, fill='x')
        # Le label Taille
        self.LabelTaille = Label(self, text="Taille", bg='grey')
        self.LabelTaille.pack(pady=2)
        # taille
        self.taille = IntVar()
        self.taille.set(512)
        #self.EntryLongueur = Entry(self, textvariable=self.taille)
        self.EntryLongueur = Scale(self, orient='horizontal', from_=0, to_=TAILLEMAX, variable=self.taille,resolution=1)
        self.EntryLongueur.pack(pady=2, padx=10, fill='x')
        # Le bouton envoyer
        self.boutonJouerEnBoucle = Button(self, text="*** ENVOYER ***", command=self.clickEnvoyer, font="Helvetica 16 bold", fg="red")
        self.boutonJouerEnBoucle.pack(pady=5)
        # Le bouton quitter
        self.boutonQuitter = Button(self, text="Quitter", command=self.clickQuitter)
        self.boutonQuitter.pack(pady=5)
        # Chargement du premier set
        texte = self.pybniz.chargeSet(self.pybniz.listesets[0])
        self.setXYT(texte)
        self.zoneAffichage.insert("1.0", texte)

    def setXYT(self, texte):
        """Change la position des ascenceurs horizontaux en fonction des variables X Y et T indiquées dans le set"""
        result = search(r'\ xyt: ([0-9]+) ([0-9]+) ([0-9]+)',texte, MULTILINE)
        if result and len(result.groups()) == 3:
            x, y, t = result.groups()
            if DEBUG: print "x:%s y:%s t:%s" % (x,y,t)
            self.posx.set(x)
            self.posy.set(y)
            self.taille.set(t)

    def clickAjouterSet(self):
        """Gère l'évènement du bouton Ajouter un set"""
        nomset = self.nomset.get()
        if nomset and nomset not in self.pybniz.listesets:
            self.pybniz.ajouterSet(nomset)
            if DEBUG: print self.pybniz.listesets
            self.choix.set(nomset)
            self.ListeSets["menu"].delete(0, END)
            for nomset in self.pybniz.listesets:
                self.ListeSets["menu"].add_command(label=nomset, command=lambda value=nomset: self.clickSet(value))
            # Marche pas, dommage ...
            # self.ListeSets = OptionMenu(self, self.choix, *self.pybniz.listesets)
            self.nomset.set("")
            self.zoneAffichage.delete("1.0", END)
            self.zoneAffichage.focus_set()

    def clickSet(self, nomset):
        """Gère l'évènement de sélection d'un set"""
        self.choix.set(nomset)
        if DEBUG: print 'Set:', nomset
        self.zoneAffichage.delete("1.0", END)
        texte = self.pybniz.chargeSet(nomset)
        self.setXYT(texte)
        if texte:
            self.zoneAffichage.insert(END, texte)

    def quitteZoneAffichage(self, e):
        """Gère l'évènement de sortie de la zone d'édition par l'appel de la méthode qui enregistre le set"""
        nomset = self.choix.get()
        texte = self.zoneAffichage.get("1.0", END)
        self.pybniz.sauveSet(nomset, texte, self.posx.get(), self.posy.get(), self.taille.get())
    
    def clickEnvoyer(self):
        """Gère l'évènement du bouton Envoyer par le lancement de IBNIZ"""
        texte = self.zoneAffichage.get("1.0", END)
        nomset = self.choix.get()
        posx = self.posx.get()
        posy = self.posy.get()
        taille = self.taille.get()
        if texte:
            self.pybniz.lanceIBNIZ(nomset, texte, posx, posy, taille)

    def clickQuitter(self):
        """Gère l'évènement du bouton Quitter par la sauvegarde du set et l'arrêt du programme"""
        texte = self.zoneAffichage.get("1.0", END)
        nomset = self.choix.get()
        self.pybniz.sauveSet(nomset, texte, self.posx.get(), self.posy.get(), self.taille.get())
        self.quit()


def encode():
    """Lit l'exécutable IBNIZ et l'enregistre dans un fichier encodé en base 64. Cette fonction est uniquement utilisée pour packager une nouvelle version de l'exécutable IBNIZ"""
    with open('src_IBNIZ/ibniz','r') as fic:
        ibniz_b64 = fic.read().encode('base64')
    with open('ibniz.b64','w') as fic:
        fic.write(ibniz_b64)

def decode():
    """Decode la chaine base 64 contenant l'exécutable IBNIZ. Cette fonction est appellée au premier lancement lorsque l'exécutable IBNIZ n'est pas présent dans le répertoire courant"""
    ibniz_b64 = """
f0VMRgEBAQAAAAAAAAAAAAIAAwABAAAAAJUECDQAAAAgdQAAAAAAADQAIAAJACgAHAAbAAYAAAA0
AAAANIAECDSABAggAQAAIAEAAAUAAAAEAAAAAwAAAFQBAABUgQQIVIEECBMAAAATAAAABAAAAAEA
AAABAAAAAAAAAACABAgAgAQIvG4AALxuAAAFAAAAABAAAAEAAAD8bgAA/P4ECPz+BAgMBQAAhJZA
AAYAAAAAEAAAAgAAABBvAAAQ/wQIEP8ECOAAAADgAAAABgAAAAQAAAAEAAAAaAEAAGiBBAhogQQI
RAAAAEQAAAAEAAAABAAAAFDldGQEWwAABNsECATbBAhEAgAARAIAAAQAAAAEAAAAUeV0ZAAAAAAA
AAAAAAAAAAAAAAAAAAAABgAAAAQAAABS5XRk/G4AAPz+BAj8/gQIBAEAAAQBAAAEAAAAAQAAAC9s
aWIvbGQtbGludXguc28uMgAABAAAABAAAAABAAAAR05VAAAAAAACAAAABgAAABgAAAAEAAAAFAAA
AAMAAABHTlUAe6QIyM0mFHB84zhKt+89i6R75DEDAAAAPwAAAAIAAAAGAAAAiAAgAYDlYAs/AAAA
QQAAAEYAAAC645J8Q0XV7KxL48A48osc2HFYHGZVYRC5jfEO69PvDgAAAAAAAAAAAAAAAAAAAACv
AQAAAAAAAAAAAAASAAAAEQAAAAAAAAAAAAAAEgAAAIoBAAAAAAAAAAAAABIAAADAAgAAAAAAAAAA
AAASAAAAxgAAAAAAAAAAAAAAEgAAAAkCAAAAAAAAAAAAABIAAADHAgAAAAAAAAAAAAASAAAA4QAA
AAAAAAAAAAAAEgAAABcAAAAAAAAAAAAAACAAAAAmAAAAAAAAAAAAAAAgAAAAYQIAAAAAAAAAAAAA
EgAAAAcBAAAAAAAAAAAAABIAAACBAgAAAAAAAAAAAAASAAAAnwIAAAAAAAAAAAAAEgAAANEBAAAA
AAAAAAAAABIAAAAVAgAAAAAAAAAAAAASAAAA1AAAAAAAAAAAAAAAEgAAALkCAAAAAAAAAAAAABIA
AAAaAQAAAAAAAAAAAAASAAAAJAMAAAAAAAAAAAAAEgAAAFoBAAAAAAAAAAAAABIAAAAXAwAAAAAA
AAAAAAASAAAANgMAAAAAAAAAAAAAEgAAABEDAAAAAAAAAAAAABIAAAA6AAAAAAAAAAAAAAASAAAA
PAIAAAAAAAAAAAAAEgAAAEcBAAAAAAAAAAAAABIAAADcAgAAAAAAAAAAAAASAAAAgwAAAAAAAAAA
AAAAEgAAAHMCAAAAAAAAAAAAABIAAABKAAAAAAAAAAAAAAASAAAAtAIAAAAAAAAAAAAAEgAAAFoC
AAAAAAAAAAAAABIAAACXAAAAAAAAAAAAAAASAAAAdAEAAAAAAAAAAAAAEgAAAP4CAAAAAAAAAAAA
ABIAAAAoAQAAAAAAAAAAAAASAAAA1QIAAAAAAAAAAAAAEgAAAPECAAAAAAAAAAAAABIAAADzAAAA
AAAAAAAAAAASAAAAVQAAAAAAAAAAAAAAEgAAAOMCAAAAAAAAAAAAABIAAADjAQAAAAAAAAAAAAAS
AAAAXAAAAAAAAAAAAAAAEgAAALcAAAAAAAAAAAAAABIAAACOAgAAAAAAAAAAAAASAAAAMgIAAAAA
AAAAAAAAEgAAAJoBAAAAAAAAAAAAABIAAAA4AQAAAAAAAAAAAAASAAAAZwAAAAAAAAAAAAAAEgAA
AIkCAAAAAAAAAAAAABIAAABQAQAAAAAAAAAAAAASAAAAawEAAAAAAAAAAAAAEgAAAAMDAAAAAAAA
AAAAABIAAAB5AgAAAAAAAAAAAAASAAAAcwAAAAAAAAAAAAAAEgAAAPgCAAAAAAAAAAAAABIAAAA4
AgAAAAAAAAAAAAASAAAArQIAAAAAAAAAAAAAEgAAAG4CAAAAAAAAAAAAABIAAAD2AQAAAAAAAAAA
AAASAAAApQAAAAAAAAAAAAAAEgAAAE4DAACAlUUIAAAAABAA8f87AwAACAQFCAAAAAAQAPH/SwIA
AKzNBAgEAAAAEQAPAOoCAAAIBAUIBAAAABEAGQBCAwAACAQFCAAAAAAQAPH/pwIAAAwEBQgEAAAA
EQAZAJEAAADcjAQIAAAAABIACwC/AQAAjM0ECAAAAAASAA4AAGxpYlNETC0xLjIuc28uMABYRnJl
ZQBfX2dtb25fc3RhcnRfXwBfSnZfUmVnaXN0ZXJDbGFzc2VzAFhEZWxldGVQcm9wZXJ0eQBYTmV4
dEV2ZW50AFhGbHVzaABYU2VuZEV2ZW50AFhJbnRlcm5BdG9tAFhDaGFuZ2VQcm9wZXJ0eQBTRExf
T3BlbkF1ZGlvAF9pbml0AFNETF9HZXRXTUluZm8AU0RMX0VuYWJsZVVOSUNPREUAU0RMX1BhdXNl
QXVkaW8AU0RMX1dhaXRFdmVudABTRExfR2V0VGlja3MAU0RMX1dNX1NldENhcHRpb24AU0RMX0Vu
YWJsZUtleVJlcGVhdABTRExfRnJlZVlVVk92ZXJsYXkAU0RMX1BvbGxFdmVudABTRExfR2V0TW9k
U3RhdGUAU0RMX0V2ZW50U3RhdGUAU0RMX0luaXQAU0RMX0RlbGF5AFNETF9TZXRWaWRlb01vZGUA
U0RMX1F1aXQAU0RMX0Rpc3BsYXlZVVZPdmVybGF5AFNETF9HZXRLZXlTdGF0ZQBTRExfQ3JlYXRl
WVVWT3ZlcmxheQBTRExfRnJlZVN1cmZhY2UAX2ZpbmkAbGliWDExLnNvLjYAWENvbnZlcnRTZWxl
Y3Rpb24AWFNldFNlbGVjdGlvbk93bmVyAFhHZXRTZWxlY3Rpb25Pd25lcgBYU3RvcmVCeXRlcwBY
R2V0V2luZG93UHJvcGVydHkAbGlibS5zby42AGF0YW4yAHNpbgBzcXJ0AGxpYmMuc28uNgBfSU9f
c3RkaW5fdXNlZABzdHJjcHkAX19wcmludGZfY2hrAGV4aXQAZm9wZW4Ac3RybmNtcABzdHJuY3B5
AHB1dHMAX19zdGFja19jaGtfZmFpbABwdXRjaGFyAHN0ZGluAHN0cmR1cABmZW9mAG1lbXNldABt
ZW1jbXAAX19mcHJpbnRmX2NoawBwdXRlbnYAZmNsb3NlAG1hbGxvYwBzdGRlcnIAZndyaXRlAGZy
ZWFkAGF0b2kAX19zcHJpbnRmX2NoawBzY2FuZgBfX3N0cmNhdF9jaGsAX19saWJjX3N0YXJ0X21h
aW4AZnJlZQBfZWRhdGEAX19ic3Nfc3RhcnQAX2VuZABHTElCQ18yLjAAR0xJQkNfMi40AEdMSUJD
XzIuMQBHTElCQ18yLjMuNAAAAAAAAAAAAAACAAAAAAADAAAAAAAAAAMAAAACAAIAAAAAAAAAAgAA
AAIAAAADAAIAAgAAAAQAAAAFAAAABQAAAAIAAgAAAAAAAgAAAAIAAgAAAAAAAgAAAAAAAAAGAAQA
AAAAAAAAAgAAAAAAAwACAAAAAgAEAAIAAgAAAAAAAQABAAEAAgABAAIAAQABAAEAAQAoAgAAEAAA
ACAAAAAQaWkNAAAEAFMDAAAAAAAAAQAEAEECAAAQAAAAAAAAABRpaQ0AAAYAXQMAABAAAAARaWkN
AAAFAGcDAAAQAAAAdBlpCQAAAwBxAwAAEAAAABBpaQ0AAAIAUwMAAAAAAADw/wQIBgkAAAgEBQgF
QgAADAQFCAVEAAAAAAUIBwEAAAQABQgHAgAACAAFCAcDAAAMAAUIBwQAABAABQgHBQAAFAAFCAcG
AAAYAAUIBwcAABwABQgHCAAAIAAFCAcJAAAkAAUIBwsAACgABQgHDAAALAAFCAcNAAAwAAUIBw4A
ADQABQgHDwAAOAAFCAcQAAA8AAUIBxEAAEAABQgHEgAARAAFCAcTAABIAAUIBxQAAEwABQgHFQAA
UAAFCAcWAABUAAUIBxcAAFgABQgHGAAAXAAFCAcZAABgAAUIBxoAAGQABQgHGwAAaAAFCAccAABs
AAUIBx0AAHAABQgHHgAAdAAFCAcfAAB4AAUIByAAAHwABQgHIQAAgAAFCAciAACEAAUIByMAAIgA
BQgHJAAAjAAFCAclAACQAAUIByYAAJQABQgHJwAAmAAFCAcoAACcAAUIBykAAKAABQgHKgAApAAF
CAcrAACoAAUIBywAAKwABQgHLQAAsAAFCAcuAAC0AAUIBy8AALgABQgHMAAAvAAFCAcxAADAAAUI
BzIAAMQABQgHMwAAyAAFCAc0AADMAAUIBzUAANAABQgHNgAA1AAFCAc3AADYAAUIBzgAANwABQgH
OQAA4AAFCAc6AADkAAUIBzsAAOgABQgHPAAA7AAFCAc9AADwAAUIBz4AAFOD7AjoAAAAAFuBww9z
AACLg/z///+FwHQF6KUAAADokAgAAOhbQAAAg8QIW8MAAAAAAAD/Nfj/BAj/Jfz/BAgAAAAA/yUA
AAUIaAAAAADp4P////8lBAAFCGgIAAAA6dD/////JQgABQhoEAAAAOnA/////yUMAAUIaBgAAADp
sP////8lEAAFCGggAAAA6aD/////JRQABQhoKAAAAOmQ/////yUYAAUIaDAAAADpgP////8lHAAF
CGg4AAAA6XD/////JSAABQhoQAAAAOlg/////yUkAAUIaEgAAADpUP////8lKAAFCGhQAAAA6UD/
////JSwABQhoWAAAAOkw/////yUwAAUIaGAAAADpIP////8lNAAFCGhoAAAA6RD/////JTgABQho
cAAAAOkA/////yU8AAUIaHgAAADp8P7///8lQAAFCGiAAAAA6eD+////JUQABQhoiAAAAOnQ/v//
/yVIAAUIaJAAAADpwP7///8lTAAFCGiYAAAA6bD+////JVAABQhooAAAAOmg/v///yVUAAUIaKgA
AADpkP7///8lWAAFCGiwAAAA6YD+////JVwABQhouAAAAOlw/v///yVgAAUIaMAAAADpYP7///8l
ZAAFCGjIAAAA6VD+////JWgABQho0AAAAOlA/v///yVsAAUIaNgAAADpMP7///8lcAAFCGjgAAAA
6SD+////JXQABQho6AAAAOkQ/v///yV4AAUIaPAAAADpAP7///8lfAAFCGj4AAAA6fD9////JYAA
BQhoAAEAAOng/f///yWEAAUIaAgBAADp0P3///8liAAFCGgQAQAA6cD9////JYwABQhoGAEAAOmw
/f///yWQAAUIaCABAADpoP3///8llAAFCGgoAQAA6ZD9////JZgABQhoMAEAAOmA/f///yWcAAUI
aDgBAADpcP3///8loAAFCGhAAQAA6WD9////JaQABQhoSAEAAOlQ/f///yWoAAUIaFABAADpQP3/
//8lrAAFCGhYAQAA6TD9////JbAABQhoYAEAAOkg/f///yW0AAUIaGgBAADpEP3///8luAAFCGhw
AQAA6QD9////JbwABQhoeAEAAOnw/P///yXAAAUIaIABAADp4Pz///8lxAAFCGiIAQAA6dD8////
JcgABQhokAEAAOnA/P///yXMAAUIaJgBAADpsPz///8l0AAFCGigAQAA6aD8////JdQABQhoqAEA
AOmQ/P///yXYAAUIaLABAADpgPz///8l3AAFCGi4AQAA6XD8////JeAABQhowAEAAOlg/P///yXk
AAUIaMgBAADpUPz///8l6AAFCGjQAQAA6UD8////JewABQho2AEAAOkw/P///yXwAAUIaOABAADp
IPz//41MJASD5PD/cfxVieVXVr7/////U1GB7LgAAgCLWQSLPfgDBQhloRQAAACJReQxwMYFVJVF
CADGBVWVRQgAg8MExgVWlUUIAIn4xgVXlUUIAMYFSZVFCAHHhUD//f+/zgQIx4VE//3/v84ECMeF
SP/9/7/OBAjHhUz//f/BzgQI6RMCAACAPy2J+Q+FIwEAAOsBQYoRgPotdPiA+nAPhLYAAAB/LoD6
ZQ+EnwAAAH8UgPpND4SsAAAAgPpjD4XTAQAA63KA+mh0QoD6brIA6bgBAACA+nZ0RH8XgPpyD4TB
AAAAgPpzD4WpAQAA6YcAAACA+niNSwQPhIwAAACA+nkPhY8BAADpiQAAAFBX/zUABAUIagHopvv/
/+sOg+wM/zX8AwUI6Bb+///HBCQAAAAA6Jr+//+J8YtDBI1TBP7BidMPhU0BAADpQwEAAMYFVJVF
CAHpPAEAAMYFVpVFCAHpMAEAAMYFV5VFCAHGBVWVRQgB6R0BAACLUwSDwwSJlUz//f/pDAEAAItb
BImdSP/9/+sJi1sEiZ1E//3/icvp8QAAAMeFQP/9/73OBAjp4gAAAFBQaMLNBAhX6DD8//+DxBCF
wImFVP/9/3UfV2jFzgQIagH/NQgEBQjosPr//8cEJAEAAADpRf///4PsDFcx/2jbzgQIaAEAAgBq
AY2Nf//9/1HoZv3//7oAAAIAg8QgKcKJhVD//f+JlTz//f/rKf+1VP/9/4uFUP/9/42Nf//9//+1
PP/9/wH4agEByFDoWv3//4PEEAHHg+wM/7VU//3/6Lf7//+DxBCFwHTCjUXog+wMAceLhVD//f+N
lX///f/GhDiX//3/AFLoPv3//4nxg8QQsgH+wQ9E8usFvgEAAACDwwSLO4X/D4Xj/f//g+wMicdq
MOgS+///WVuNXYBo5s4ECFPoYvv//4PEDGpk/7VI//3/U+ih+v//g8QMamRo/M4ECFPokfr//4PE
DGpk/7VE//3/U+iA+v//iRwk6Hj7//9Y/7VM//3/6Ez7//+DxBCBvUD//f+9zgQIoxiVRQh1BGog
6wJqEGoAUFDoOfr//4PEEKP4lEUI/zX4lEUIaFlVWTJoAAEAAGgAAQAA6Mf7//9ZW2i3zgQIaLfO
BAij/JRFCOhB+f//WFqNhWT//f/HhWT//f9ErAAAagBQZseFaP/9/xCAxoVq//3/AWbHhWz//f8A
AseFdP/9/7SVBAjoRPr//4k8JOgcHQAAifCDxBD+yA+UBSSVRQh1B8YFSZVFCADoPwMAAKMslUUI
oyiVRQjoER0AAKAklUUIg+wMg/ABD77AUOhbBwAAiTwk6M4SAADocPv//4PEEItV5GUzFRQAAAB0
Bejs+v//jWXwWVteX12NYfzDMe1eieGD5PBQVFJoUM0ECGjgzAQIUVZo8JAECOgf+f//9JCQkJCQ
kJCQkJCQkJCQVYnlU4PsBIA9EAQFCAB1P6EUBAUIuwj/BAiB6wT/BAjB+wKD6wE52HMejbYAAAAA
g8ABoxQEBQj/FIUE/wQIoRQEBQg52HLoxgUQBAUIAYPEBFtdw410JgCNvCcAAAAAVYnlg+wYoQz/
BAiFwHQSuAAAAACFwHQJxwQkDP8ECP/QycOQVYsVMJVFCInli0UQV1aJ1lOLXQzR+InB6x6J90nB
7xCBxqlkAQCLPL3EBDkIZoHHAIBmiTuDwwKFyXXeacCpZAEAAdA5wqMwlUUIdgqBBTSVRQgAAEAA
W15fXcNVMcCJ5VdWU1KLdQyLTQgPthwGMdKJRfCLfRD2w4APRH0UAduJ+IgEEYPCAoP6EHXni0Xw
gcEAAgAAQIP4CHXPWFteX13DVYnlV1ZTg+wUoeiURQiDPdyURQgAix3klEUIiUXsodCURQiJReSJ
ReB0EKHUlEUIiUXkodiURQiJReDHRegAAAAAx0XwAAAAAItF7A++MItF4IPmfzlF7Hcji0XkOUXs
chuF23kGidj32OsMg/sbfhW4GwAAACnYiUXo6wkx0rj///8A6we6////ADHAg/sbdzNSg/4gUKH8
lEUIufwABQiNPPX8/wQID03PUYtQFInYweAIA0XwweAEAwJQ6Pj+//+DxBD/RfCDffAffghDx0Xw
AAAAAIP+CnUKQ8dF8AAAAADrBIX2dAj/RezpWP///4tF6AEF5JRFCI1l9FteX13DVYnlV4t9CFYx
9lOLXRDB4wgDXQzB4wTrNw++0rj8AAUIg/ogagCNDNX8/wQID03BR2j///8AUKH8lEUIi1AUjQQe
g8YQAwJQ6Gv+//+DxBCKF4TSdcONZfRbXl9dw1WJ5YPsIKEclUUIZolF8KEglUUIZolF8qEYlUUI
ZolF9GaJRfaNRfBQ/zX8lEUI6Eb3//+DxBDJw4A9VZVFCABVieV1Bl3pD/b//2sF7JRFCDK5AwAA
AF2Z9/nDVYnlg+wIoSyVRQiAPSSVRQgBdQXoxP///ysFKJVFCMnDVYnlg+wI6NT///+5MgAAADHS
yY0EQPfxw1WJ5VOD7CRloRQAAACJRfQxwI1d3OjN////g+wMJf//AABQaMTNBAhqGGoBU+ji9///
g8QcahxqAFPozf7//4PEEIA9JJVFCAAPhIIAAADZBUyVRQjZ7tnJ2+nd2XY0gD1KlUUIAVIZwIPA
IVBRUd0cJGjLzQQIahhqAVPok/f//4PEHGoeagBT6H7+//+DxBDrAt3Y2QVQlUUI2e7Zydvp3dl2
KoPsEN0cJGjYzQQIahhqAY1d3FPoV/f//4PEHGofagBT6EL+//+DxBDrAt3YD78FuAQFCLkrAAAA
hcB5BPfYsS2D+A+6DwAAAA9O0KGgBAUIU1JRJf//AQBQaOLNBAhqGI1d3GoBU+gE9///g8Qcahxq
DVPo7/3//4PEDLqyzQQIgD2FBAUIALiwzQQIah1qDQ9EwlDozv3//6GoBAUIWlkPt9BSwegQUGj2
zQQIahhqAVPouPb//4PEHGodahVT6KP9//8PvwW6BAUIg8QQuSsAAACFwHkE99ixLYP4D1K6DwAA
AA9O0KGkBAUIUlGNXdwl//8BAFBoAM4ECGoYagFT6Gn2//+DxBxqHmoNU+hU/f//g8QQuLvNBAiA
PUiVRQgAdRSAPYYEBQgAuL/NBAi6ts0ECA9EwlJqH2oNUOgk/f//oawEBQhZW41d3A+30FLB6BBQ
aPbNBAhqGGoBU+gL9v//g8Qcah9qFVPo9vz//4PEEItF9GUzBRQAAAB0Behq9f//i138ycNVieVX
VlOD7ByLFfyURQgPvgWIBAUIi1IUweAQjQSFwAQ9CI1IBAUEAAQAixqJReTrP4tE0QQPt3zRAYnG
weAIgeYAAAD/JQAA/wAJ+AnwNQCAAICJBJNCgfqAAAAAddKBwQAEAACBwwACAAA7TeR0BDHS672A
PUmVRQgAdAroWPv//+hJ/f//g8QcW15fXemn/P//gD1KlUUIAFWJ5VZTdViAPSSVRQgBuMgAAAB1
PugD/f//izUolUUIicPo1fz//4nxKcGNQwG7AwAAAGvAMpn3+41EAQGFwH4Ng/gSuhEAAAAPTcLr
BbgBAAAAg+wMUOjO9P//g8QQjWX4W15dw1WJ5VdWU4PsHOjG8///g+wMagCJw+iq8f//idqDxBCB
4sAAAACJ2YP6ARnSgeEADwAA99KD4kCD+QEZ/4PjA/fXg+cgg/sBGfb31oPmEIC4EQEAAAEZ2/fT
g+MIgLgSAQAAARnJ99GD4QSAuBQBAAABiU3gGcn30YPhAoC4EwEAAAAPlcAPtsAJwqGUBAUICfoJ
8gnaC1XgJf///4AJysHiGAnCiRWUBAUIjWX0W15fXcOAPVWVRQgAVYnli0UIdQZd6Y3z//+i9JRF
CF3DVYsVMJVFCInlVos1pAQFCFOLHTSVRQjB6gqNDBqLFZAEBQjB4gqNBDLB4AY5wXYdhfZ0GYnY
wegQg+DAg8BAo5AEBQjGBYcEBQgB6w+BwQAABAA5wQ+XBYcEBQhbXl3DVYnlg+wIgz3ABAUIAHQx
ZoM9ugQFCAB/J4PsDGoBxgVIlUUIAccFwAQFCAAAAABmxwW6BAUIAADoR////4PEEKG8BAUIhcAP
hIgAAACKFYUEBQiE0nUYa8D+D78VuAQFCAHQSHUhxgWFBAUIAesY/sp1FA+/FbgEBQiNBEJIdQfG
BYUEBQgAgD2FBAUIAXVFD78FugQFCIsVwAQFCI0EUEh1MujOFgAAxgWFBAUIAGbHBbgEBQgAAMcF
vAQFCAAAAABmxwW6BAUIAADHBcAEBQgAAAAAycNVieVTUItdCOhh+v//xgMAOwUYBAUID4yKAAAA
gz0cBAUIAHQcxgMCoRwEBQiJQwihIAQFCIlDDKEkBAUIZolDEIPsDP81DAQFCOgw8f//g8QQhcB1
MoPsDIsdGAQFCGggBAUIaCQEBQhoHAQFCGgYBAUIaBTOBAjogvD//4PEIAEdGAQFCOsexwUgBAUI
AAAAAMcFHAQFCAAAAADHBRgEBQgAAAAAi138ycNVieVXVlOB7NwFAACAPQQEBQgAdCZQUGoBajxo
4AEAAGiAAgAAaCDOBAhqAehT7///g8QgxgUEBAUIAIPsDLsQAAAAaFzOBAjot/H//+j9+///g8QQ
63SD7AxqAOhT7///g8QQTnXwidox9tH6weIJofyURQiNPBaD7AyDxgKLQBQDOA++B4mVJPr//1Do
Iu///w++B4kEJOgX7///g8QQgf4AAgAAi5Uk+v//dcJmvkAAg+wMagDo+O7//4PEEE518EOB+/AB
AAB0ar5AAAAA64WD7AxogAAAAOjV7v//g8QQTnXtMfah/JRFCInyg+wM0fpGAdqLQBSLAA++RJAB
UOiu7v//g8QQgf4AAQAAddZmviAAg+wMaIAAAADoku7//4PEEE517YPrgIH7AHwAAHUH62+7AAQA
AL4gAAAA65GD7AxogAAAAOhm7v//g8QQTnXtMfah/JRFCInyg+wM0fpGAdqLQBSLAA++RJADUOg/
7v//g8QQgf4AAQAAddZmviAAg+wMaIAAAADoI+7//4PEEE517YPrgIH7AHwAAHUH6wy7AAQAAL4g
AAAA65GAPfSURQgAjZUq+v//dRNQaL4FAABSagDou/X//4PEEOsLub4FAAAxwInX86r/NQgEBQiN
hSr6//9qAWi+BQAAUOhO7///g8QQjWX0W15fXcP/BeyURQiAPVeVRQgAVYnlxwXwlEUIAAAAAHQG
Xend/f//XcNVixXolEUIieWLRQjrAUg50HYGgHj/CnX1XcNVieWLRQjrAUCAOAB0BoB4/wp19F3D
VTHAieWDyf9XVlOD7ByLfQiLHeiURQjyrvfRjXH/id/rAUeKF4TSdAWA+gp19FBW/3UIiFXkU+iy
7///g8QQilXkhcB1KCnfg+wMKfcB3o1XAVKJVeTow+7//4tV5IPEEInRicfzpMZEEP8A6wuE0nQF
jV8B66cxwI1l9FteX13DVYPK/4nlMcBXidFWi3UIU4n38q6LPeiURQj30Y1Z/4nR8q6JyvfS6wiK
DBAB2IgMEEqh6JRFCIXSee6Jx4nZ86Sh6JRFCFteX6PQlEUIXcNVieWKVQhdjUK/PAUPlsCD6jCA
+gkPlsIJ0A+2wMNVieWKVQhdgPoKD5TAgPogD5TCCdAPtsDDVYnlU1GLXQjrAUs7HeiURQhyQYA9
4JRFCAB1OIoTgPoudQaAewEudeEPvsJQiFX46JT///9ailX4hcB0F4D6RnUFxgMw68OA+jl1BcYD
QesDQogTi138ycNVieVTUYtdCOsBSzsd6JRFCHJBgD3glEUIAHU4ihOA+i51BoB7AS514Q++wlCI
VfjoO////1qKVfiFwHQXgPowdQXGA0brw4D6QXUFxgM56wNKiBOLXfzJw6HYlEUIVYnlxwXclEUI
AAAAAKPUlEUIXcNVieWAfQwAU4tdCHUH6NX////rM4M93JRFCAB1FKHQlEUIo9iURQij1JRFCKPc
lEUIOx3clEUIdwiJHdSURQhyBokd2JRFCIkd0JRFCFtdw1WJ5VZT6I3///+LNeiURQjrB0uJHdCU
RQiLHdCURQg583YXD74DUOig/v//WYXAdOHrB0uJHdCURQiLHdCURQg583YOD74DUOh//v//WoXA
deGNZfhbXl3DVYnlU+g1////6wdDiR3QlEUIix3QlEUIigOEwHQXD77AUOhM/v//WoXAdN/rB0OJ
HdCURQiLHdCURQiKA4TAdBcPvsBQ6Cn+//9ZhcB13+sHQ4kd0JRFCIsd0JRFCIoDhMB0Dg++wFDo
Bv7//1qFwHTfOx3olEUIdgdLiR3QlEUIi138ycOh0JRFCDsF6JRFCFWJ5YpVCHQND77SSFJQ6LP+
//9ZWMnDodCURQhVieWKVQiAOAB0DQ++0kBSUOiU/v//WFrJw1WJ5VdWU1GLFdCURQgPvl0IUolV
8Ohy/P//i1XwXonXKceJxoP/H34GU4PqIOsgoeiURQg5xnYgjVb/UolV8OhI/P//WotV8CnGOf5/
BFNS6whTAcdX6wJTUOgx/v//WVuNZfRbXl9dw1WJ5VdWU1CLHdCURQiKRQhTiEXz6Ar8//+JHCSJ
xugb/P//WjnYdQ2AOAB0CEBQ6Ar8//9fjVDgD7598znTcw5Xg8MgU+jd/f//WVvrKlcp81Do0P3/
/+sJV0BQS+jF/f//WKHQlEUIWooQgPoKdAiE0nQEhdt14YB98wB0CqHQlEUIo9iURQiNZfRbXl9d
w1Wh1JRFCInlVos12JRFCFOJ8SnBjVkBhdt+O4A94JRFCAB1MosV0JRFCDnydgQp2usLOcKLFdCU
RQgPR9CJFdCURQiKVAgBiBBAhNJ19VteXeko/f//W15dw6HUlEUIOQXYlEUIVYnli1UIdgZd6Y3/
//+h0JRFCDsF6JRFCHQUAdCj0JRFCOsGilABiBBAgDgAdfVdw1WJ5VdWU4PsKGhizgQI6Bv7//+D
xBCFwInHdR6D7Axoas4ECOiG+///xwQkfs4ECOgn6///g8QQicdTU2iKzgQIV+hF6f//g8QQizXo
lEUIhcCJwnVVg+wMaIzOBAjoTPv//+tgQ4oDPAp0BITAdfVRPApqBg+UwGhizgQID7bAVgHDiVXk
6HHn//+DxBCLVeSFwHQUUonYagEp8FBW6Hnp//+LVeSDxBCJ3oA+AHQEifPrsoPsDFLor+j//4k8
JOhX6P//g8QQjWX0W15fXcOAPeCURQgAVYnlU4tdCHVeg/sNuAoAAAAPRNiNQ+CD+F52BYP7CnVG
gz3clEUIAHQF6GT+//+h0JRFCOsBQIA4AHX6ixXolEUIgcIAAAIAOdByCOsZihCIUAFIixXQlEUI
OdBz8IgaQokV0JRFCFtdw1WJ5VdWU4PsDIsd2JRFCCsd1JRFCEN4EYM93JRFCAC4AAAAAA9E2OsC
MduD7Az/NTAEBQjoouf//41DAYkEJOjH6P//izXUlEUIidmDxBCjMAQFCInH86TGBBgAjWX0W15f
Xen3HwAAVYnlU1Doox8AAIsdMAQFCIXbdRLrFoPsDA++wFBD6AT///+DxBCKA4TAdeqLXfzJw1WJ
5YPsCOhc////yel//f//VbkHAAAAieW6NAQFCFdWg+wgZaEUAAAAiUX0McC40JRFCInGjX3Y86WJ
x4nWsQfzpY112InXsQfzpYtF9GUzBRQAAAB0BehW6P//g8QgXl9dw1Wh6JRFCInlgD3glEUIAF0P
RQVMBAUIw1WJ5VdWU4PsTOh88P//iUXAUFBqCmj0AQAA6Ljn///HBCQBAAAA6Azp///HBCQAAAIA
6MDn//+DxAxo//8BAP91CFCj6JRFCOja5f//6EH6//+h6JRFCMcF5JRFCAAAAADGBeCURQgAxgVE
BAUIAaPQlEUIofQDBQijTAQFCKM8BAUIozgEBQijNAQFCFhaagFqDejP5///g8QQMdvo6O///zlF
wInGdQaAfdQAdA/oHvL//8YFmAQFCAOJdcAPvgWIBAUIOQUoBAUIdBn/BUSVRQiAPVWVRQgAoygE
BQh0Beie9///oTiVRQiNUHg51nJjifIpwonQMdKJRbiJVbzfbbjYNdzYBAiJNTiVRQjZXcTZRcTf
LTyVRQjZBeDYBAjYyscFPJVFCAAAAADHBUCVRQgAAAAA3vnZHUyVRQjaPUSVRQjHBUSVRQgAAAAA
2R1QlUUIgD0klUUIAHVjgD1WlUUIAHUUg+wMjU3UUehE5P//g8QQ6fAAAACD7AyNfdRXxkXUAOj8
5P//g8QQgH3UAHUMg+wMV+g79P//g8QQgH3UAA+FwQAAAIA9VZVFCAAPhLQAAADoyPb//+mqAAAA
g+wMjVXUUsZF1ADotuT//4PEEIA9VpVFCAB0FYB91AB1D4PsDI1N1FHo6fP//4PEEIB91AB1c4Xb
dC7o5/3//4PsDFDo/QcAAIPEEIA9SJVFCAB0FIPsDGoAxgVIlUUIAOhe8v//g8QQ6NgOAACZAQU8
lUUIERVAlUUIgD1VlUUIAHQXofCURQhAqf8PAACj8JRFCHUF6Cj2///ooPL//+g78v//6TD+//+K
RdQ8DA+EswQAADwCD4VTAwAAgD1UlUUIAIt13It94HRE6LTt//+F9onCdQyLReQPt8hmhcAPRfFQ
UA+3ReRXiVW0UInQKwUsBAUIVlBoqs4ECGoB6ELj//+LVbSDxCCJFSwEBQjo/fD//4P+Gw+ESgQA
AIP+CXUMgDVJlUUIAemt/f//gf4aAQAAdW8PvgUklUUIg+wMUOh98f//oCSVRQiDxBCD8AGEwKIk
lUUIdQ/oJe3//6MslUUI6XL9//+LNSiVRQjoEO3//ys1LJVFCMcFOJVFCAAAAADHBVCVRQgAAAAA
xwVMlUUIAAAAAAHGiTUolUUI6Tb9//+B/hsBAAB1VujS7P//hdujLJVFCKMolUUIdBHoYfz//4Ps
DFDodwYAAIPEEOiPBgAAoCSVRQiD7AzHBTSVRQgAAAAAxwUwlUUIAAAAAIPwAQ++wFDoxfD//+nT
/P//gD1JlUUIAA+Ey/z//4H+EQEAAHUc98fAAAAAD4SdAAAAg+wM/zXQlEUI6O31///rIoH+EgEA
AHUn98fAAAAAD4SSAAAAg+wM/zXQlEUI6CL2//+DxBC7AQAAAOl4/P//gf4UAQAAdRL3x8AAAAB0
JOjC9v//6V78//+B/hMBAAB1NPfHwAAAAHQb6AH3///pRPz//4PsDIPnA1fodvf//+m3AgAAg+wM
g+cDV+iH9///6aYCAACB/hEBAAB1EYPsDIPnA1fojff//+mNAgAAgf4SAQAAdRGD7AyD5wNX6N33
///pdAIAAIP+CHUHg+wMav/rCoP+f3UPg+wMagDop/j//+lL////gf4lAQAAdQrovPr//+m++///
g/5zdRaB58AAAAAPhMQAAADotvj//+mj+///g/5jdAWD/mt1FoHnwAAAAA+EpAAAAOjX+f//6YP7
//+D/nZ1FoHnwAAAAA+EiQAAAOgk+v//6Wj7//+D/nh1EoHnwAAAAHRy6D76///pUfv//4P+YXVK
gefAAAAAdFuDPdyURQgAdAroLPX//+kx+///ixXolEUIMcCDyf+JFdSURQiJ1/Ku99GNRAr/o9iU
RQih0JRFCKPclEUI6QL7//+D/mJ1FIHnwAAAAHQMgDVKlUUIAenp+v//i0XkZoXAD4Td+v//g+wM
D7fAUOiv+P//6Uf+//88A3UK6Pnt///pvvr//zwEdWYPt03aizUYlUUIweEIiciZ9/6JwQ+3RdjB
4AiZ9/6JwoPqAA+Ikfr//4nPg+8AD4iG+v//Pf8AAAAPj3v6//+B+f8AAAAPj2/6//+LFZQEBQjB
4QhmMdIJwgnKiRWUBAUI6VT6//88BXUPgQ2UBAUIAAAAgOlB+v//PAZ1D4EllAQFCP///3/pLvr/
/zwQD4WWAAAAi3XcvwIAAACLRdiJ8TnwD07Ig+wMKciZ9///NfiURQiJDRiVRQijHJVFCInwKciZ
9/+jIJVFCOjE3v//ahBqAP913P912Ojl3///g8QU/zX8lEUIo/iURQjoQt////81+JRFCGhZVVky
aAABAABoAAEAAOho4f//g8QYaLfOBAhot84ECKP8lEUI6OHe///oAun//+sUPA0PhYj5//+D7AyN
RdRQ6HIYAACDxBDpdPn//41l9FteX13DkJCQkJCQD74FhAQFCIsVkAQFCIMEhbAEBQgBoVgEBQiF
wHUJg8JAiRWQBAUIg8ABiw1UBAUIIwVcBAUIweIKAcLB4gajWAQFCIkUgcOJ9o28JwAAAABTg+wI
ixVYBAUID74FhAQFCInTgwSFsAQFCAGB4///AAB0LaGMBAUIiw1UBAUIg8IBIxVcBAUIweAQCdiJ
FVgEBQiJBJGDxAhbw422AAAAAIHiAAABAA+UBYgEBQjrBpDoeuv//+iZ6P//OwWMBAUIdO7ojOj/
/4sVWAQFCKOMBAUI66SNtgAAAACNvwAAAABTg+wIixVYBAUID74FhAQFCA++DYgEBQgPt9qDBIWw
BAUIAYnQwegQOcF0bKGMBAUIiw1UBAUIg8IBIxVcBAUIweAQiRVYBAUIiQSRoVgEBQiNlBsAAP//
geP/AAAAweMJgesAAAEAg8ABIwVcBAUIo1gEBQiJFIGhWAQFCIPAASMFXAQFCKNYBAUIiRyBg8QI
W8OQjXQmAIHiAAABAA+UBYgEBQjrBpDoour//+jB5///OwWMBAUIdO7otOf//4sVWAQFCKOMBAUI
6WL///+Qg+wUixXMBEUIi0QkGIlcJAQx24l0JAiJfCQMhcCJbCQQfkqLNcgERQiF9n5AvwEAAACJ
wdPnsyCD7wEpw4nVg+UfiTwkid8p73g9idHB+QWLHI3QBEUIifnT6yMcJAHQicLB+h/3/okVzARF
CInYi3QkCItcJASLfCQMi2wkEIPEFMOQjXQmAInVwf0Fixyt1ARFCI1PINPrifmLPK3QBEUI99nT
5wn7Ixwk67GNdgBmxwW6BAUIAABmxwW4BAUIAADHBcAEBQgAAAAAxwW8BAUIAAAAAMcFtAQFCAAA
AADHBbAEBQgAAAAAxwWkBAUIAAAAAMcFoAQFCAAAAADHBawEBQgAAAAAxwWoBAUIAAAAAMONtgAA
AACNvCcAAAAAg+wci0QkIIkEJOhBFgAAxgWYBAUIAYPEHMONtgAAAABVV1ZTg+wcxwVUBAUIxAQ9
CMcFXAQFCP//AQDHBVgEBQgAAAAAxwVgBAUIxAQ4CMcFaAQFCP8/AADHBWQEBQgAAAAAxwVsBAUI
xAQ5CMcFdAQFCP//AADHBXAEBQgBAAAAxwV4BAUIxAQ3CMcFgAQFCP8/AADHBXwEBQgAAAAAxwVQ
BAUI0ERFCMYFhAQFCADGBYUEBQgAxgWGBAUIAMYFiAQFCAHHBcwERQgAAAAAxwWUBAUIAAAAAMYF
iQQFCADonuX//4styARFCGbHBboEBQgAAGbHBbgEBQgAAMcFwAQFCAAAAACD/QDHBbwEBQgAAAAA
o4wEBQijkAQFCMcFtAQFCAAAAADHBbAEBQgAAAAAxwWkBAUIAAAAAMcFoAQFCAAAAADHBawEBQgA
AAAAxwWoBAUIAAAAAA+E0QAAAMcFzARFCAAAAAB+XzHSMdvrLo22AAAAAInQwfgFizSF0ARFCI1C
IInCwfofiTSdxAQFCIPDAff9gfsAABAAdEWJ0IPgH3TRide5IAAAAMH/BSnBizS91ARFCIs8vdAE
RQjT7onB0+cJ/uu5McCNdgDHBIXEBAUIAAAAAIPAAT0AABAAdeuAPYQEBQgBxwXMBEUIAAAAAHRe
gD2FBAUIAHQYxwWcBAUIMK8ECIPEHLgwrwQIW15fXf/gxwWcBAUIwK8ECIPEHLjArwQIW15fXf/g
x0QkCAAAQADHRCQEAAAAAMcEJMQEBQjoI9r//4A9hAQFCAF1oscFnAQFCOCuBAiDxBy44K4ECFte
X13/4GaQoVQEBQiLFWwEBQijbAQFCKFYBAUIiRVUBAUIixVwBAUIo3AEBQihXAQFCIkVWAQFCIsV
dAQFCKN0BAUIoWAEBQiJFVwEBQiLFXgEBQijeAQFCKFkBAUIiRVgBAUIixV8BAUIo3wEBQihaAQF
CIkVZAQFCIsVgAQFCKOABAUID7YFhwQFCIkVaAQFCDwBooQEBQh0HIA9hQQFCAC4wK8ECLowrwQI
D0XCo5wEBQjDZpDHBZwEBQjgrgQIw5CNdCYAg+wUD7YNhAQFCIlcJASJfCQMiXQkCA++2Y17MA+3
hD9YBAUIjVMUg8MYiWwkEGaJRCQCoVgEBQiJxmYrNJVQBAUIja7/AwAAZoH9/gd3HmY5dCQCZom0
P1gEBQgPhC4BAADHBJ1cBAUIAAAAAIs1VAQFCIkElVAEBQjHBJ1QBAUIAAAAAIs8hok8lVgEBQgP
thWHBAUIONEPhMoAAACLDWwEBQiA+gGJNWwEBQiIFYQEBQiJDVQEBQiLDXAEBQijcAQFCKFcBAUI
iQ1YBAUIiw10BAUIo3QEBQihYAQFCIkNXAQFCIsNeAQFCKN4BAUIoWQEBQiJDWAEBQiLDXwEBQij
fAQFCKFoBAUIiQ1kBAUIiw2ABAUIo4AEBQiJDWgEBQgPhIAAAACAPYUEBQgAuMCvBAi6MK8ECA9F
wqOcBAUIi0QkHIXAdQrHBVAEBQjQREUIi1wkBIt0JAiLfCQMi2wkEIPEFMOQi0QkGIsUnVwEBQgF
0ERFCIXSo1AEBQh+0rj+////08AgBZgEBQjrw4s0nVAEBQiJNJ1cBAUI6cr+//+QjXQmAMcFnAQF
COCuBAjrjY22AAAAAI2/AAAAAIPsDPYFWgQFCAEPlAWIBAUI6wqQjXQmAOhS5P//6HHh//85BYwE
BQh07uhk4f//o4wEBQiDxAzDkI20JgAAAACAPYQEBQgBdB+APYUEBQgAuMCvBAi6MK8ECA9FwqOc
BAUIw5CNdCYAxwWcBAUI4K4ECMONtgAAAACNvCcAAAAAU4PsCIA9hAQFCAAPhZcAAACLFVgEBQgP
t9qAPYUEBQgAD4XJAAAAD74NiAQFCInQwegQOcEPhB0BAAChjAQFCIsNVAQFCIPCASMVXAQFCMHg
EIkVWAQFCIkEkaFYBAUIjZQbAAD//4Hj/wAAAMHjCYHrAAABAIPAASMFXAQFCKNYBAUIiRSBoVgE
BQiDwAEjBVwEBQijWAQFCIkcgYPECFvDjbYAAAAAoVgEBQiLFZAEBQiFwHQpg8ABiw1UBAUIIwVc
BAUIweIKAcLB4gajWAQFCIkUgYPECFvDkI10JgCDwkCJFZAEBQjrzJCNdCYAhduhjAQFCHQniw1U
BAUIg8IBIxVcBAUIweAQCdiJFVgEBQiJBJGDxAhbw5CNdCYAgeIAAAEAD5QFiAQFCOsGkOi64v//
6Nnf//87BYwEBQh07ujM3///ixVYBAUIo4wEBQjrpY10JgCB4gAAAQAPlAWIBAUI6waQ6ILi///o
od///zsFjAQFCHTu6JTf//+LFVgEBQijjAQFCOmx/v//kFUxwFdWU4PsPIA9iQQFCAAPhYIBAAAP
tgWEBAUIOgWHBAUIdAfGBZgEBQgDPAEPhCwLAACAPYUEBQgAuMCvBAi6MK8ECA9FwqOcBAUIx0Qk
GNBERQj3VCQYx0QkFO8nAACNtCYAAAAAixVQBAUIoVQEBQiLDVgEBQgPtjKNegGJPVAEBQiNHIiJ
XCQQifOA+34Ph/EAAAAPtuv/JK3k2AQIjbQmAAAAAItcJBAx9osVzARFCIs7wf8Qg+cfD4S7AAAA
iy3IBEUIuCAAAACJ0Sn4g+EfKciF7Q+OnwAAAGa+AQCJ+dPmg+4BhcCJdCQcD4imCgAAidHB+QWL
NI3QBEUIicHT7iN0JByNBBeLXCQQicLB+h/3/cHmEIl0JCCJFcwERQiLO8H/EIPnH3RPuCAAAACJ
074BAAAAifnT5in4g+Mfg+4BKdiJdCQkD4hyCgAAidHB+QWLNI3QBEUIicHT7iN0JCSNBBeJwsH6
H/f9we4QC3QkIIkVzARFCIt8JBCJN5CNdCYAg2wkFAEPhdX+//+47ycAAIPEPFteX13DD74VmAQF
CA++BYQEBQgPo8IPgrgJAACLXCQYjYQfIBQQAIsEhVAEBQgF0ERFCKNQBAUI/xWcBAUIg2wkFAEP
hYT+///rrWaQi1wkEIPpASMNXAQFCIkNWAQFCIsbhdt1h4tcJBiNhB8gFBAAiwSFUAQFCAXQREUI
g2wkFAGjUAQFCA+FQP7//+lm////jXYAi3wkEIPpATHSIw1cBAUIiQ1YBAUIix+NDIiF23QJiwGJ
wsH6H/f7g2wkFAGJEQ+FBP7//+kq////jbQmAAAAAIsVXAQFCIPpAYtcJBAh0Y1x/yHWiTVYBAUI
ixSIiwPBwBAl//8PAINsJBQBiRSFxAQFCA+Fv/3//+nl/v//ZpCLfCQQg+kBIw1cBAUIiQ1YBAUI
jQyIiwf3KQ+s0BCDbCQUAYkBD4WN/f//6bP+//+LfCQQg+kBixfBwhAp0SMNXAQFCINsJBQBiwSI
iQcPhWT9///piv7//420JgAAAACLNVwEBQiD6QGLfCQQIfGNUf8h8okVWAQFCIsfiwyIwcMQKdoh
8oNsJBQBiQyQD4Uk/f//6Ur+//+NtCYAAAAAi3wkEIPpASMNXAQFCIkNWAQFCIsXIRSIg2wkFAEP
hfX8///pG/7//4tcJBCDbCQUAfcTD4Xf/P//6QX+//9mkIt8JBCDPwEZwCUAAAEAg2wkFAGJBw+F
vfz//+nj/f//i3wkEDHAiy+F7Q9OB4NsJBQBiQcPhZ78///pxP3//5CB6rAwNQiDwQGLFJVQBAUI
Iw1cBAUIiQ1YBAUIiRSIg2wkFAEPhW78///plP3//5CLXCQQg+kBIw1cBAUIjTSIMcCJDVgEBQiL
C4XJdCeLBonPwf8fiUwkCIl8JAyJwsH6Hw+kwhDB4BCJBCSJVCQE6HsOAACDbCQUAYkGD4UW/P//
6Tz9//+Qi1wkEIPpASMNXAQFCIkNWAQFCIsTKRSIg2wkFAEPhe37///pE/3//4t8JBCD6QEjDVwE
BQiJDVgEBQiLFwEUiINsJBQBD4XF+///6ev8//+D6QGLXCQQIw1cBAUIiQ1YBAUIjTSI2wPdXCQI
2wbdHCToctL//4NsJBQB2XwkLtwN8NoECA+3RCQutAxmiUQkLNlsJCzbHtlsJC4PhW/7///plfz/
/2aQi3wkEIPpASMNXAQFCIkNWAQFCIsXMRSIg2wkFAEPhUX7///pa/z//4t8JBCD6QEjDVwEBQiJ
DVgEBQiLD4XJD4SPAQAAixVkBAUIoWAEBQiLBJAx0vc1xARFCIHC0ERFCINsJBQBiRVQBAUID4X2
+v//6Rz8//+QixVgBAUIoWQEBQiB79BERQiDwAEjBWgEBQiDbCQUAaNkBAUIiTyCD4XD+v//6en7
//+NtgAAAAChZAQFCIPpAYtcJBAjDVwEBQiLFWAEBQiDwAEjBWgEBQiJDVgEBQijZAQFCIsLwcEQ
iQyC65hmkKFkBAUIg+kBge/QREUIixVgBAUIIw1cBAUIg8ABIwVoBAUIiQ1YBAUIo2QEBQiJPIKL
fCQQiwfBwBAl//8PAIsEhcQEBQiJwsH6H/c9xARFCIHC0ERFCINsJBQBiRVQBAUID4UY+v//6T77
//+NdgCLFZQEBQiDwQEjDVwEBQiJDVgEBQiJFIiBJZQEBQj//wD/g2wkFAEPheP5///pCfv//422
AAAAAIkVUAQFCLjvJwAAxgWJBAUIAStEJBSDxDxbXl9dw2aQixVgBAUIg8EBix1kBAUIIw1cBAUI
iQ1YBAUIixSawcIQiRSIoWQEBQiD6AEjBWgEBQiDbCQUAaNkBAUID4V2+f//6Zz6//+QoWQEBQiL
XCQQiw1gBAUIg8ABIwVoBAUIo2QEBQiLE8HCEIkUgaFYBAUIg+gBIwVcBAUIg2wkFAGjWAQFCA+F
Lfn//+lT+v//oWQEBQiLDWAEBQiD6AEjBWgEBQiNFIGLAoPoAYXAiQKhZAQFCA+FzQMAAIPoAiMF
aAQFCINsJBQBo2QEBQgPheT4///pCvr//420JgAAAACLXCQQg+kBIw1cBAUIiwOJDVgEBQiJwsH6
H/c9xARFCIHC0ERFCINsJBQBiRVQBAUID4Wh+P//6cf5//+NdCYAi3wkEIsHwcAQJf//DwCLBIXE
BAUIg2wkFAGJBw+Fdvj//+mc+f//kItcJBAxwIszhfYPSQOJA4NsJBQBD4VW+P//6Xz5//+Qi3wk
ENsH3A3o2gQI3Rwk6MTP//+DbCQUAdl8JC7YDeTaBAgPt0QkLrQMZolEJCzZbCQs2x/ZbCQuD4UR
+P//6Tf5//+NdCYAi1wkEI1R/yMVXAQFCIkVWAQFCIsLwfkQ0wyQg2wkFAEPheL3///pCPn//5CN
dCYAi1wkEDHAixOF0g+IZf///4lUJCjbRCQo2A3g2gQI2cDZ+tvoD4ozAwAA3dnZfCQui1wkENgN
5NoECA+3RCQutAxmiUQkLNlsJCzbXCQo2WwkLotEJCiJA+ka////jXYAg+kBIw1cBAUIg2wkFAGJ
DVgEBQgPhV73///phPj//5CLfCQQjVH/IxVcBAUIiRVYBAUIiw+NFJD3wQAAIAAPhPQBAACLAvfR
wfkQ0/iJAoNsJBQBD4Ue9///6UT4//+QixVkBAUIg8EBIw1cBAUIg+oDiQ1YBAUIix1gBAUIIxVo
BAUIixSTwcIQiRSIg2wkFAEPheD2///pBvj//412AIsVZAQFCIPBASMNXAQFCIPqAYkNWAQFCOu+
jbYAAAAAi1wkEIPBASMNXAQFCIkNWAQFCIsTiRSIg2wkFAEPhZX2///pu/f//4sNZAQFCDHSoWAE
BQiLBIiD6QEjDWgEBQj3NcQERQiJDWQEBQiBwtBERQiDbCQUAYkVUAQFCA+FVPb//+l69///jbQm
AAAAAItcJBCD6QEjDVwEBQiJDVgEBQiLEwkUiINsJBQBD4Ul9v//6Uv3//+LXCQQg+kBge/QREUI
Iw1cBAUIgeqwMDUIiQ1YBAUIiwPBwBAl//8PAIk8hcQEBQiLBJVQBAUIBdBERQiDbCQUAaNQBAUI
D4XU9f//6fr2//+NtCYAAAAAg8EBIw1cBAUIjRSIidAtxAQFCMH4AsHAEIkNWAQFCIkC6Xn+//9m
kIt8JBCD6QEjDVwEBQiDbCQUAY0EiIsXiwiJD4kQD4V99f//6aP2//+LNVwEBQiNUf+D6QKLXCQQ
IfEh8o0UkIs7jQSIiwiDbCQUAYkLiwqJCIk6D4VH9f//6W32//9mkIsCwfkQ0+CJAukJ/v//ZpCL
BIEx0vc1xARFCIHC0ERFCINsJBQBiRVQBAUID4UO9f//6TT2//+QxwWcBAUI4K4ECOne9P//D77z
i1wkGIl0JASNhB8gFBAAiwSFUAQFCIkEJOig8P///xWcBAUI6T72//+J08H7BYs0ndQERQiNSCDT
7onBiwSd0ARFCPfZ0+AJxiN0JBzpRfX//4nTwfsFizSd1ARFCI1IINPuicGLBJ3QBEUI99nT4AnG
I3QkJOl59f//3djdHCTo+cn//+nA/P//VYnlg+wIgz18lUUIAHVCg+wMaFiVRQjoWMr//4PEEIM9
YJVFCAB0Kf8VaJVFCFBqAGj42gQI/zVglUUI6DPL//+DxBCjfJVFCKFslUUIyf/gycNVieVWMfZT
g+wgi10Ig3scAA+E1wAAAI1F9FCNRfBQjUXsUI1F6FCNReRQagBqAGoAagD/NXyVRQj/cxD/cwzH
RfQAAAAA6LbI//+DxDCDfeQAD4SWAAAAi0X0hcB0DIPsDFDoycf//4PEEI1F9DH2UI1F8FCNRexQ
jUXoUI1F5FCLRfBqAGoAg8ADwegCUGoA/zV8lUUI/3MQ/3MMx0X0AAAAAOhYyP//g8Qwg33kAHQ8
i1X0hdJ0NYtF6A+vRezB6AN0EVZQUv81YJVFCOiex///g8QQUf81fJVFCP9zEP9zDOipyP//i3X0
g8QQjWX4ifBbXl3DVYnlVlOD7HhqAf81YJVFCGWhFAAAAIlF9DHA6LrK//+LDWSVRQiDxBAx0jnI
dGuFwHRnULtAAAAAUGoAUf81fJVFCI11lGofagH/NWCVRQjopcf//4PEFP81YJVFCOg3yf//g8QQ
UFBW/zVglUUI6IbI//+DxBCDfZQfdRgx0oN9sAB0FYPsDFboe/7//4PEEInC6wVLdc7rAonQi1X0
ZTMVFAAAAHQF6D3J//+NZfhbXl3DVYnlU1Do+P3//4M9fJVFCAB0Mv8VaJVFCOgu////icP/FWyV
RQiF23QboTAEBQiFwHQMg+wMUOiKx///g8QQiR0wBAUIi138ycNVieWD7Ajorf3//4M9fJVFCAB0
Mv8VaJVFCGoA/zVklUUIagH/NWCVRQjojcj//1j/NWCVRQjoYcj//4PEEKFslUUIyf/gycNVieVX
U4PscGWhFAAAAIlF9DHAi0UIi1gEg3sIHg+FiQAAAIN7JB91NosVMAQFCDHAg8n/idfyrvfRSVFS
agBqCGof/3Mo/3Mc/zVglUUI6PDI//+LQyiDxCCJRbDrB8dFsAAAAACLUxyD7AyhYJVFCMdFlB8A
AACJVaSLUySJRaCJVayLUyyJVbSNVZRSagBqAP9zHFDo6cf//4PEFP81YJVFCOirx///g8QQi0X0
ZTMFFAAAAHQF6OfH//+NZfhbX13DVTHJieUx0ldWU7vQREUIg+wwi0UIx0Xw0FRFCIldyIlFxOsM
sQyyAusGsgHrAjHSi13EigNDiV3EjXDfifOA+112BITAdek8Lo1Y0A+URdCA+wmIXeB2EIB90AB1
Co1wv4nzgPsFd2OE0nUGsRCyATH/gH3QAHQggPoCdaeLdcixDItF8MYGMEaJOIPABDH/iXXIiUXw
65g8QY1wyYpF4Inzif4PTcMPvsDBxgSA+gEPRP7T4AnHgPoCD4Vq////g+kEg+Ef6WX///+E0nQV
i1XIi13wxgIwQok7g8MEiVXIiV3wPFx1H4tdyIt1xOsBRooGPAp0BITAdfVGiV3IiXXE6Sf///88
LA+EH////zwki3XIsgAPRMKLVfCIBkaEwIl1yMcCAAAAAHQLg8IEiVXw6ff+//+LRcTHBcgERQgA
AAAAi13IgHj/JA+FLAEAAMcF0ARFCAAAAAC6BAAAAIoID775hf8PhNgAAABAg/9cdQ6KCECA+Qp0
5YTJdfTr34D5Rn8PgPlBfTeD6TCA+Ql3zeswgPlodMF/DYD5YrkBAAAAD0TR67eA+W90DYD5cb4C
AAAAD0TW66W6AwAAAOueg+8HiNG+AQAAANPmg+8wjU7/izXIBEUIIc+5IAAAACnRiX3EiXXwg+Yf
KfGLdfCJTeB4GcH+BdPnxwS11ARFCAAAAAAJPLXQBEUI6yaLTeDB/gWLfcT32dP/i03gCTy10ARF
CIt9xIPBINPniTy11ARFCItN8AHRiQ3IBEUI6Rv///+LFcgERQiJ1sH6BYPmH3QcifGh0ARFCNPo
AckJBJXQBEUIg/kffuvpsgAAAKHQBEUIiQSV1ARFCIHr0ERFCIkdxARFCMdF8AAAAADrA4lN8ItN
8EGKkc9ERQiE0nQtgPpND4SWAAAAgPo/uzoAAAAPhJEAAAAx24D6Og+EhgAAAID6ew+EhAAAAOtJ
vk0AAAAxwDHbD7640ERFCIX/D5RF4Dn3dAqAfeAAdQQ533UiOUXwdAaAfeAAdA3HBI3MVEUIAAAA
AOsNQIkEjcxURQjrA0DrwITSD4Vx////6z2h0ARFCLkgAAAAiz3UBEUIKfHT4Inx0+8J+Ok0////
Mdu+TQAAAOsOvjsAAADrBzHbvn0AAACJyOl5////g8QwW15fXcNVg8j/ieVdw4PsLIl8JCSLfCQ0
i1QkPIl0JCCLRCQ4iWwkKIt0JDCF/4nVx0QkEAAAAAAPiK8AAACF7Q+IlwAAAIXSicWJdCQYicF1
Mzn4dl+J8In6Mcn39YnGicqLTCQQifCFyXQH99iD0gD32ot0JCCLfCQki2wkKIPELMNmkDHJMfY5
+nfTD73Kg/EfiUwkDHVsO0QkGHYGOfqJ8XO7Mcm+AQAAAOuyjbQmAAAAAIXAdQu4AQAAADHS9/WJ
wYn4MdL38YnHifD38Yn5icbrio20JgAAAAD32IPSAPdUJBD32ulZ////996D1wD338dEJBD/////
6T3///+NdCYAD7ZMJAy4IAAAAInuK0QkDNPiicHT7g+2TCQMCdaJ+ol0JByLdCQY0+WJwdPqD7ZM
JAzT54nB0+4J/onw93QkHInXicb35TnXchqLbCQYD7ZMJAzT5TnFcgcxyen7/v//Odd19YPuATHJ
6e3+//+QkJCQkJCQkJCQVVdWU+hpAAAAgcMLMwAAg+wci2wkMI27CP///+jbv///jYMI////KcfB
/wKF/3QpMfaNtgAAAACLRCQ4iSwkiUQkCItEJDSJRCQE/5SzCP///4PGATn+dd+DxBxbXl9dw+sN
kJCQkJCQkJCQkJCQkPPDixwkw5CQkJCQkJCQkJBVieVTg+wEofz+BAiD+P90E7v8/gQIZpCD6wT/
0IsDg/j/dfSDxARbXcOQkFOD7AjoAAAAAFuBw18yAADoj8f//4PECFvDAAADAAAAAQACAHQAdHl4
AG1vbm8Ab2ZmAHN0ZXIAVD0lMDRYACUzLjNmIE1vcHMlYwAlMi40ZiBmcHMAVklERU8gUz0lMDVY
ICglYyVYKQAlMDRYLiUwNFgAQVVESU8gUz0lMDVYICglYyVYKQAlZCAlZCAlZCAlZABZVVY0TVBF
RzIgVyVkIEglZCBGJWQ6JWQgSXAgQTA6MCBDNDIwbXBlZzIgWFlTQ1NTPTQyME1QRUcyCgBGUkFN
RQBcI2ZpbGUgAFwjZmlsZSB1bnRpdGxlZC5pYgoAdW50aXRsZWQuaWIAdwBcIEVSUk9SOiBjb3Vs
ZG4ndCBzYXZlIGZpbGUhCgAlZCAlZCAlZCAlZAoASUJOSVoAMQAwADUxMgBDYW4ndCBsb2FkIGZp
bGUgJyVzJwoAXCNmaWxlICVzCgBTRExfVklERU9fV0lORE9XX1BPUz0ALABJQk5JWiBxdWljayBy
ZWZlcmVuY2UgKEYxMjpxdWl0KVVzZSBjdXJzb3Iga2V5cyB0byBtb3ZlIGFyb3VuZAoKPT09PT09
PSBLZXlib2FyZCBjb21tYW5kcyA9PT09PT0KZjEgIHN0YXJ0L3BhdXNlICAgICAgICAgZjEyIGhl
bHBmMiAgcmVzZXQvcmVzdGFydCAgICAgICBlc2MgcXVpdHRhYiBoaWRlL3Nob3cgZWRpdG9yIGN0
cmwrcyBzYXZlCnNoaWZ0K2N1cnNvciAuLi4uIHNlbGVjdCBhcmVhCmN0cmwrbGVmdC9yaWdodCAu
IGp1bXAgYnkgd29yZHMgY3RybCt1cC9kb3duIC4uLi4gaW5jL2RlYyBudW1iZXJjdHJsK3gvYy92
IC4uLi4uLiBjdXQvY29weS9wYXN0ZQo9PT09PT09PSBJQk5JWiBsYW5ndWFnZSA9PT09PT09PQpP
bmUgY2hhcmFjdGVyIHBlciBvcGVyYXRpb24uCk51bWJlciBmb3JtYXQgMTYuMTYgZml4ZWRwb2lu
dC4KSW1tZWRpYXRlcyBpbiB1cHBlcmNhc2UgaGV4LgpJbXBsaWNpdCB3aG9sZS1wcm9ncmFtIGxv
b3AKICB3aXRoICdNdycgb24gZWFjaCBjeWNsZS4KCkFyaXRobWV0aWM6CgorIC0gKiAvICUgJiB8
IF4gfiBhcmUgYXMgaW4gQwoKcTpzcXJ0IHM6c2luIGE6YXRhbjIgcjpyb3IgbDpzaGwKPCA6IHpl
cm8gaWYgPDAgZWxzZSBrZWVwCj4gOiB6ZXJvIGlmID4wIGVsc2Uga2VlcAo9IDogMSBpZiB6ZXJv
IGVsc2UgMAoKU3RhY2sgbWFuaXB1bGF0aW9uOgoKICAxIGQgPSAxIDEgICAgIDIgMSB4ID0gMSAy
CjEgMSBwID0gMSAgICAgMyAyIDEgdiA9IDIgMSAzCgpOKSA9IGNvcHkgZnJvbSBOIHBsYWNlcyBk
b3duCk4oID0gc3RvcmUgdG8gTiBwbGFjZXMgZG93bgoKTWVtb3J5IG1hbmlwdWxhdGlvbjoKCk5A
ID0gbG9hZCB2YWx1ZSBmcm9tIE1FTVtOXQpNTiEgPSBzdG9yZSB2YWx1ZSBNIHRvIE1FTVtOXQoK
Q29uZGl0aW9uYWxzOgoKTj9NOyAgID0gaWYgTiE9MCB0aGVuIE0KTj9NOk87ID0gaWYgTiE9MCB0
aGVuIE0gZWxzZSBPCgpMb29wczoKCk5YLi4uTCBleGVjdXRlICcuLi4nIE4gdGltZXMKaSA9IGlu
ZGV4IG9mIGlubmVyIFggbG9vcApqID0gaW5kZXggb2Ygb3V0ZXIgWCBsb29wClsuLi5OXSByZXBl
YXQgJy4uLicgdW50aWwgTj09MAoKU3Vicm91dGluZXM6CgpOey4uLn0gZGVmaW5lIHN1YnJvdXRp
bmUKICAgICAgKHN0b3JlIHBvaW50ZXIgdG8gTUVNW05dKSBOViAgICAgcnVuIHN1YnJvdXRpbmUg
TgoKUmV0dXJuIHN0YWNrOgoKUiAgICAgcG9wIGZyb20gcnN0YWNrIHRvIHN0YWNrClAgICAgIHBv
cCBmcm9tIHN0YWNrIHRvIHJzdGFjawoKVXNlciBpbnB1dDoKClUgICAgIHJldHVybiBTU0tLLllZ
WFggd2hlcmUKICAgICAgU1MgPSBjbGljayAmIGNyc2tleSBzdGF0ZSAgICAgICBLSyA9IGxhc3Qg
a2V5ICh+YXNjaWkpCiAgICAgIFlZWFggPSBtb3VzZSBwb3NpdGlvbgoKRGF0YSBzZWdtZW50OgoK
TkcgICBmZXRjaCBOIGJpdHMgb2YgZGF0YQokICAgIHN0YXJ0IGRhdGEgc2VnbWVudCB3aGVyZQow
LUYgIGRhdGEgZGlnaXRzCmJxb2ggZGlnaXQgc2l6ZSAxLTQgYml0cwoKRGF0YSBzZWdtZW50IGlz
IHN0b3JlZCBpbgpNRU1bMC4uLl0gb24gZWFjaCBWTSByZXNldAoKU3BlY2lhbHM6Cgp3IDogcHVz
aCBsb29wIHZhcnMgKHQgb3IgdCB5IHgpIE0gOiBzZXBhcmF0ZSBhdWRpby92aWRvZSBjb2RlClQg
OiB0ZXJtaW5hdGUgcHJvZ3JhbQpcIDogY29tbWVudCBsaW5lCiwgOiBibGFuaywgc2VwYXJhdGUg
bnVtYmVycwoKPT09PT09PSBFeGFtcGxlcyA9PT09PT09CgpDb3B5IHRvIGVkaXRvciBhbmQgcnVu
OgoKXng2ci0KCmRkZCoqKgoKZDNyMTUmKgoKZGQ2ciozciYKCl54N3IrTWQ4ciYKCnY4cnNkdip2
dipeCgpkNnJ8NSp3ZEFyJisKCnY4cnNkdip2diped3BwOHItCgpheDhyKzNsd2QqeGQqK3ExeC94
NXIrXgoKdjhyZHM0WDMpTHh+Mlh2KnZ2KitpIUwxQDJAJgoKNnteXmRkZCoqKjElfTV7djhyc2R2
KnZ2Kl53cHA4ci19NHt2OHJkc3guNitzNFgzKUx4fjJYdip2dioraSFMMUAyQF59M3theDhyKzNs
d2QqeGQqK3ExeC94NnIrXn0yKTZyMyYzK1Y1NUE5Xk1kNnJ8NSp3ZEFyJisKCkZ1bGwgZG9jcyAm
IGxhdGVzdCBJQk5JWjoKaHR0cDovL3BlbHVsYW11Lm5ldC9pYm5pei8KAAoKCgpcIElCTklaIDEu
MUMwMC1OT1JFTEVBU0UKXApcIFByZXNzIGYxMiBmb3IgaGVscC4KAElCTklaIHZlcnNpb24gMS4x
QzAwLU5PUkVMRUFTRQB1c2FnZTogJXMgW2ZpbGVfdG9fbG9hZF0gW29wdGlvbnNdCndoZXJlIG9w
dGlvbnMgaW5jbHVkZToKICAtaChlbHApICAgICAgIER1bXAgdGhpcyB0ZXh0CiAgLXYoZXJzaW9u
KSAgICBEdW1wIHZlcnNpb24gaW5mbwogIC1jKG9kZSkgQ09ERSAgRXhlY3V0ZSBjb2RlCiAgLW4o
b2F1dG9ydW4pICBEbyBub3QgYXV0b3J1biBsb2FkZWQgY29kZSBvciBhdXRvaGlkZSBPU0QKICAt
cyhpemUpIFZBTCAgIFNpemUgb2YgdGhlIHdpbmRvdwogIC14IFZBTCAgICAgICAgWCBwb3NpdGlv
biBvZiB0aGUgd2luZG93CiAgLXkgVkFMICAgICAgICBZIHBvc2l0aW9uIG9mIHRoZSB3aW5kb3cK
ICAtciAgICAgICAgICAgIFJlbW92ZSBmcmFtZSB0aXRsZSBhbmQgYm9yZGVyIG9mIHRoZSB3aW5k
b3cKAAAAAHBCACR0SVC6BAg4ugQIOLoECDi6BAg4ugQIOLoECDi6BAg4ugQIOLoECDi6BAg4ugQI
OLoECDi6BAg4ugQIOLoECDi6BAg4ugQIOLoECDi6BAg4ugQIOLoECDi6BAg4ugQIOLoECDi6BAg4
ugQIOLoECDi6BAg4ugQIOLoECDi6BAg4ugQIOLoECCC7BAg4ugQIOLoECDi6BAjgugQIALwECDi6
BAjAuwQIkLsECGC7BAgwvQQIOLoECAi9BAg4ugQIsLwECIC8BAg4ugQIOLoECDi6BAg4ugQIOLoE
CDi6BAg4ugQIOLoECDi6BAixugQIOLoECGC8BAhAvAQIqMAECJi6BAiAwAQIOLoECDi6BAg4ugQI
OLoECDi6BAg4ugQIWLkECDi6BAg4ugQIQMAECDi6BAjwvwQIULoECDi6BAg4ugQIqL8ECDi6BAhg
vwQIOLoECEC/BAgIvwQImL4ECDi6BAhgvgQIOLoECDi6BAgovgQIOLoECNi9BAiwvQQIOLoECDi6
BAhYvQQIOLoECDi6BAhgwgQIOLoECDi6BAg4ugQIOLoECEDCBAgAwgQIOLoECMDBBAg4ugQIOLoE
CDi6BAigwQQIQMEECBDBBAjIwAQIOLoECDi6BAigwwQIg7oECHjDBAg4ugQIUMMECPjCBAjQwgQI
iMIECCi8BAgAAIA3AACARxgtRFT7IRk/g8jJbTBfxEBJQk5JWl9DQgAAAAABGwM7QAIAAEcAAAAM
sv//XAIAAOy1//90DQAAsLr//4ACAAAMu///sAIAAFK7///cAgAAVLz//xgDAACyvP//VAMAAOu8
//+AAwAADr3//6gDAAAvvf//yAMAAEi9///oAwAAd7///yQFAAALwP//UAUAAHjA//+EBQAAKsH/
/7wFAABGwf//5AUAAKbB//8QBgAAfcL//zgGAAAow///eAYAACnF//84BwAATcX//2AHAABoxf//
gAcAAH7F//+gBwAA/8X//+QHAABPxv//EAgAAG3G//8wCAAAhsb//1AIAADfxv//eAgAADjH//+g
CAAAUcf//8AIAAChx///5AgAAPrH//8YCQAAgMj//0wJAACiyP//eAkAAMHI//+kCQAAKsn//wAK
AAC6yf//WAoAABTK//+MCgAAUMr//7QKAAAgy///MAsAAJHL//9UCwAA+cv//4gLAAAqzP//tAsA
ADvM///UCwAAjcz///wLAAClzP//HAwAANzT//+oDgAALNT//7wOAAC81P//4A4AAIzV//8EDwAA
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
DhCGBEEOFIMFTg4wAkoOFEEOEMNBDgzGQQ4Ix0EOBMUQAAAATBEAALje//8CAAAAAAAAABAAAABg
EQAApt7//wQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/////AAAAAP////8AAAAAAAAAAAEAAAABAAAAAQAA
AMUBAAABAAAAKAIAAAEAAABBAgAADAAAANyMBAgNAAAAjM0ECPX+/2+sgQQIBQAAAGCGBAgGAAAA
8IEECAoAAAB9AwAACwAAABAAAAAVAAAAAAAAAAMAAAD0/wQIAgAAAOgBAAAUAAAAEQAAABcAAAD0
igQIEQAAANyKBAgSAAAAGAAAABMAAAAIAAAA/v//b2yKBAj///9vAgAAAPD//2/eiQQIAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABD/BAgAAAAAAAAA
ACaNBAg2jQQIRo0ECFaNBAhmjQQIdo0ECIaNBAiWjQQIpo0ECLaNBAjGjQQI1o0ECOaNBAj2jQQI
Bo4ECBaOBAgmjgQINo4ECEaOBAhWjgQIZo4ECHaOBAiGjgQIlo4ECKaOBAi2jgQIxo4ECNaOBAjm
jgQI9o4ECAaPBAgWjwQIJo8ECDaPBAhGjwQIVo8ECGaPBAh2jwQIho8ECJaPBAimjwQIto8ECMaP
BAjWjwQI5o8ECPaPBAgGkAQIFpAECCaQBAg2kAQIRpAECFaQBAhmkAQIdpAECIaQBAiWkAQIppAE
CLaQBAjGkAQI1pAECOaQBAgAAAAAAAAAAAAAAAAAAAAAGDw8GAAYAABmZgAAAAAAAGz+bGz+bAAA
GD5gPAZ8GADGzBgwZsYAADhseP7MfgAAGBhwAAAAAAAMGDAwGAwAAGAwGBgwYAAAAGY8fjxmAAAA
GBh+GBgAAAAAAAAYGHAAAAAAfgAAAAAAAAAAGBgAAAYMGDBgwAAAfMbW1sZ8AAAYOHgYGBgAAHwG
BnzA/gAAfAYcBgZ8AADGxsb+BgYAAP7A/AbGfAAAfMD8xsZ8AAD+BgwYMGAAAHzGfMbGfAAAfMbG
fgZ8AAAAGBgAGBgAAAAYGAAYGHAAAA444DgOAAAAAH4AfgAAAADgOA444AAAeAwMGAAYAAB8xs7A
wH4AAHzG/sbGxgAA/GZ8Zmb8AAB8xsDAxnwAAPxmZmZm/AAA/sDwwMD+AAD+wPDAwMAAAH7AwM7G
fgAAxsb+xsbGAAB+GBgYGH4AAAYGBgbGfAAAxsz4zMbGAADAwMDAwP4AAMb+1sbGxgAAxub23s7G
AAB8xsbGxnwAAPzGxvzAwAAAfMbGxs58BgD8xsb8zMYAAHzAfAYGfAAA/xgYGBgYAADGxsbGxnwA
AMbGxmw4EAAAxsbG1v7GAADGbDg4bMYAAMNmPBgYGAAA/gwYMGD+AAA+MDAwMD4AAMBgMBgMBgAA
fAwMDAx8AAAQOGzGAAAAAAAAAAAAAP8AMDAcAAAAAAAAPAY+Zj4AAGBgYHxmfAAAADxgYGA8AAAG
BgY+Zj4AAAA8Zn5gPAAADhh+GBgwAAAAPmZmPgZ8AGBgfGZmZgAAGAAYGBgYAAAGAAYGBgZ8AGBg
bHhsZgAAGBgYGBgMAAAAbP7WxsYAAAB8ZmZmZgAAADxmZmY8AAAAfGZ8YGBgAAA+Zj4GBgYAAH5g
YGBgAAAAPGA8BjwAABh+GBgYDgAAAGZmZmY+AAAAZmZmPBgAAADGxtb+bAAAAMZsOGzGAAAAZmZm
PgY8AAB+DBgwfgAAHDAw4DAwHAAYGBgAGBgYAHAYGA4YGHAAdtwAAAAAAAD+zgQIAdcECDfXBAhW
1wQIAQAAAEdDQzogKFVidW50dS9MaW5hcm8gNC42LjMtMXVidW50dTUpIDQuNi4zAAAuc2hzdHJ0
YWIALmludGVycAAubm90ZS5BQkktdGFnAC5ub3RlLmdudS5idWlsZC1pZAAuZ251Lmhhc2gALmR5
bnN5bQAuZHluc3RyAC5nbnUudmVyc2lvbgAuZ251LnZlcnNpb25fcgAucmVsLmR5bgAucmVsLnBs
dAAuaW5pdAAudGV4dAAuZmluaQAucm9kYXRhAC5laF9mcmFtZV9oZHIALmVoX2ZyYW1lAC5jdG9y
cwAuZHRvcnMALmpjcgAuZHluYW1pYwAuZ290AC5nb3QucGx0AC5kYXRhAC5ic3MALmNvbW1lbnQA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAEAAAACAAAAVIEE
CFQBAAATAAAAAAAAAAAAAAABAAAAAAAAABMAAAAHAAAAAgAAAGiBBAhoAQAAIAAAAAAAAAAAAAAA
BAAAAAAAAAAhAAAABwAAAAIAAACIgQQIiAEAACQAAAAAAAAAAAAAAAQAAAAAAAAANAAAAPb//28C
AAAArIEECKwBAABEAAAABQAAAAAAAAAEAAAABAAAAD4AAAALAAAAAgAAAPCBBAjwAQAAcAQAAAYA
AAABAAAABAAAABAAAABGAAAAAwAAAAIAAABghgQIYAYAAH0DAAAAAAAAAAAAAAEAAAAAAAAATgAA
AP///28CAAAA3okECN4JAACOAAAABQAAAAAAAAACAAAAAgAAAFsAAAD+//9vAgAAAGyKBAhsCgAA
cAAAAAYAAAACAAAABAAAAAAAAABqAAAACQAAAAIAAADcigQI3AoAABgAAAAFAAAAAAAAAAQAAAAI
AAAAcwAAAAkAAAACAAAA9IoECPQKAADoAQAABQAAAAwAAAAEAAAACAAAAHwAAAABAAAABgAAANyM
BAjcDAAALgAAAAAAAAAAAAAABAAAAAAAAAB3AAAAAQAAAAYAAAAQjQQIEA0AAOADAAAAAAAAAAAA
ABAAAAAEAAAAggAAAAEAAAAGAAAA8JAECPAQAACcPAAAAAAAAAAAAAAQAAAAAAAAAIgAAAABAAAA
BgAAAIzNBAiMTQAAGgAAAAAAAAAAAAAABAAAAAAAAACOAAAAAQAAAAIAAACozQQIqE0AAFkNAAAA
AAAAAAAAAAgAAAAAAAAAlgAAAAEAAAACAAAABNsECARbAABEAgAAAAAAAAAAAAAEAAAAAAAAAKQA
AAABAAAAAgAAAEjdBAhIXQAAdBEAAAAAAAAAAAAABAAAAAAAAACuAAAAAQAAAAMAAAD8/gQI/G4A
AAgAAAAAAAAAAAAAAAQAAAAAAAAAtQAAAAEAAAADAAAABP8ECARvAAAIAAAAAAAAAAAAAAAEAAAA
AAAAALwAAAABAAAAAwAAAAz/BAgMbwAABAAAAAAAAAAAAAAABAAAAAAAAADBAAAABgAAAAMAAAAQ
/wQIEG8AAOAAAAAGAAAAAAAAAAQAAAAIAAAAygAAAAEAAAADAAAA8P8ECPBvAAAEAAAAAAAAAAAA
AAAEAAAABAAAAM8AAAABAAAAAwAAAPT/BAj0bwAAAAEAAAAAAAAAAAAABAAAAAQAAADYAAAAAQAA
AAMAAAD0AAUI9HAAABQDAAAAAAAAAAAAAAQAAAAAAAAA3gAAAAgAAAADAAAACAQFCAh0AAB4kUAA
AAAAAAAAAAAEAAAAAAAAAOMAAAABAAAAMAAAAAAAAAAIdAAAKgAAAAAAAAAAAAAAAQAAAAEAAAAB
AAAAAwAAAAAAAAAAAAAAMnQAAOwAAAAAAAAAAAAAAAEAAAAAAAAA"""

    if DEBUG: print "Decodage de IBNIZ"
    with open(IBNIZPATH,'w') as fic:
        ibniz = ibniz_b64.decode('base64')
        fic.write(ibniz)
        chmod(IBNIZPATH, 755)


# MAIN
if __name__ == '__main__':
    """Le programme principal appelle la fonction decode si l'exécutable IBNIZ n'est pas présent dans le répertoire courant, et instancie ensuite la classe Pybniz contenant le métier de l'application"""
    if not exists(IBNIZPATH): decode()
    Pybniz()
