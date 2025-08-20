import cv2
from cv2 import aruco
import json
import datetime
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = [10, 6]                                                                                #On adapte la taille des figures matplotlib qui seront affichées
import pandas as pd

def EnSeconde(date):                                                                                                    #Fonction permettant d'obtenir le temps en seconde à partir des minutes et des secondes
    return date.hour*60+date.minute*60+date.second

def Resultats():                                                                                                        #Fonction réalisant l'écriture des résultats sur un fichier txt
        Lf[0].append(Lcompte[0])
        Lf[1].append(Lcompte[1])
        Lf[2].append(Lcompte[2])

        R = open("résultats.txt", "a")
        R.write(DictQuestions[str(compteQ)]+"\n")
        R.write("{} participants au sondage.\n".format(Lcompte[0]+Lcompte[1]+Lcompte[2]))
        R.write("Résultats : {} POUR : {} \n".format(Lcompte[0], StrOui))
        R.write("            {} CONTRE : {} \n".format(Lcompte[1], StrNon))
        R.write("            {} NUL : {} \n\n".format(Lcompte[2], StrNul))
        R.close()

with open('participants.json') as mon_fichier:                                                                          #Ouverture du fichier json des participants et création du dictionnaire correspondant
    Dictparticipants = json.load(mon_fichier)

with open('Questions.json') as mon_fichier:                                                                             #Ouverture du fichier json des questions et création du dictionnaire correspondant
    DictQuestions = json.load(mon_fichier)

NbrQ = len(DictQuestions.keys())                                                                                        #Obtention du nombre de questions
Coul = [(0,0,255), (0,247,255), (0,255,15)]                                                                             #Liste contenant les couleurs que prendront les cadres autour des marqueurs

compteQ = 1                                                                                                             #Compte permettant de savoir à quel question en est le vote

LimTemps = 6                                                                                                            #Choix de la durée du décompte pour le mode avec  (en seconde)

Q = False
Manuel = False
Tempo = False
graph = False                                                                                                            #4 booléens s'apparentant à des variables d'états pour faire fonctionner le programme

Lf = [[],[],[]]                                                                                                         #Liste qui recense les résultats de toutes les questions

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)                                                                 #Choix de la bibliothèque de marqueurs utilisée
parameters = aruco.DetectorParameters()                                                                      #Création des paramètres de détection des marqueurs

date = EnSeconde(datetime.datetime.now())                                                                               #Obtention de la date puis passage de cette dernière en seconde à l'aide de la fonction EnSeconde()

cap = cv2.VideoCapture(0)                                                                                               #Démarrage de la capture vidéo

while(True):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corner, num, rejected_point = detector.detectMarkers(gray)
    listMarq = [corner,num]

    if Q is False and Manuel is False and Tempo is False:
        cv2.putText(frame, "Veuillez choisir votre mode de vote", (130,25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 4)
        cv2.putText(frame, "Veuillez choisir votre mode de vote", (130,25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.putText(frame, "Appuyer sur t pour une temporisation ou sur y pour un mode manuel", (35,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(frame, "Appuyer sur t pour une temporisation ou sur y pour un mode manuel", (35,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (56, 56, 255), 2)     #Sélection du mode de vote (temporisation ou manuel)
        
        if cv2.waitKey(1) == ord('t'):
            Tempo = True
            date = EnSeconde(datetime.datetime.now())
        elif cv2.waitKey(1) == ord('y'):
            Manuel = True                                                                                                                                    #Détection du choix et démarrage des votes en conséquence

    elif Q is True :                                                                                                                                        #Partie du code correspondant à la fin des questions (si le booléen Q est vrai, alors tous les votes on été réalisés)
        cv2.putText(frame, "Fin des questions !", (25,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 180, 180), 4)
        cv2.putText(frame, "Fin des questions !", (25,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
        if graph is True:
            LQ = []
            for i in range(NbrQ):
                LQ.append(str(i+1))

            plotdata = pd.DataFrame({    
                "Non":Lf[1],
                "Nul":Lf[2],
                "Oui":Lf[0]
                }, 
                index=LQ)                                                                                                                                   #Création d'un dataframe à l'aide de la librairie panda
                                                                                                                                                            #=> Tableau à 3 colonnes (Oui, Non et Nul) et autant de ligne
                                                                                                                                                            #que de questions, recensant les résultats du vote
                                                              
            diag = plotdata.plot(kind="bar", stacked='true', color = ['red', '#FFBF00','green'])                                                            #Mise en forme de ce dataframe sous forme de diagramme en bâtons avec la librairie pyplot de matplotlib
            plt.title("Résultats des votes")
            plt.xlabel("Indice de la question")
            plt.ylabel("Votes")
            for c in diag.containers:                                                                                                                       #Récupération des valeurs de chacun des tronçons pour les afficher
                labels = [v.get_height() if v.get_height() > 0 else '' for v in c]                                                                          #On n'affiche pas les valeurs de tronçons qui valent 0
                diag.bar_label(c, label_type='center', labels = labels, color = 'black')                                                                    #On affiche les valeurs
            plt.show()
            graph = False                                                                                                                                    #Le booléen graph devient faux, signe que le diagramme a bien été plot. Cela évite qu'il soit affiché à chaque itération de la boucle principale

    if Manuel or Tempo :                                                                                                            
        try :                                                                                                                       #Affichage de la question
            cv2.putText(frame, DictQuestions[str(compteQ)], (25,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 180, 180), 4)
            cv2.putText(frame, DictQuestions[str(compteQ)], (25,30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)                  #Essaie d'afficher la question d'indice CompteQ
        except KeyError:
            Q = True
            graph = True
            Manuel = False
            Tempo = False                                                                                                            #Si la question d'indice compteQ n'existe pas, c'est-à-dire que les
                                                                                                                                     #questions sont finies, on met fin au cycle
    if Manuel is True and cv2.waitKey(1) == ord('y'):   
        Resultats()
        compteQ += 1                                                                                                                 #Lorsque la touche y est préssée, on traite les résultats et on passe
                                                                                                                                     #à la question suivante
    if Tempo :
        DiffTemps = EnSeconde(datetime.datetime.now()) - date                                                                        #On compare le temps actuel avec le moment où la question est apparu pour
                                                                                                                                     #décompter le temps qui passe
        cv2.rectangle(frame, (10, 410), (52, 440), (255,255,255), -1)
        cv2.putText(frame, str(LimTemps-DiffTemps), (20,435), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (180, 180, 180), 4)
        cv2.putText(frame, str(LimTemps-DiffTemps), (20,435), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)                          #Affichage du timer
        if DiffTemps >= LimTemps : 
            Resultats()
            compteQ += 1
            date = EnSeconde(datetime.datetime.now())                                                                                #Lorsque que le délai de temporisation est passé on traite les résultats,
                                                                                                                                     #on passe à la question suivante et on pose une nouvelle balise temporelle 
                                                                                                                                     #pour le prochain timer de la prochaine question                                                               
    
    Lvote = []                                                                                                                       #Initialisation d'une liste qui contiendra les votes affichés à l'écran à l'instant t
    for j, i in enumerate(corner):
        for marqueurs in i:
            LCorner = []                                                                                                             #Initlisation d'une liste qui contiendra les coordonnées des 4 coins du marqueur ArUco
            for coins in marqueurs:
                cercle = cv2.circle(frame, (int(coins[0]), int(coins[1])), 10, (100,0,255), 3)                                       #Affichage des cercles autour des coins des marqueurs
                Ltemp = [int(coins[0]), int(coins[1])] 
                LCorner.append(Ltemp)                                                                                                #Remplissage de la liste contenant les coordonnées des coins

            if LCorner[0][0] >= LCorner[2][0]:
                Droite = True
            else:
                Droite = False
                
            if LCorner[0][1] >= LCorner[2][1]:
                Bas = True
            else:
                Bas = False                                                                                                           #On vient comparer les coins supérieur gauche et inférieur droit afin de
                                                                                                                                      #déterminer l'orientation du marqueur.
            if Droite is True and Bas is True:
                try :
                    Lvote.append([Dictparticipants[str(num[j][0])],"NON"])
                except KeyError:
                    Lvote.append(["inconnu","NON"])
                k = 0
            elif Droite is False and Bas is False:
                try :
                    Lvote.append([Dictparticipants[str(num[j][0])],"OUI"])
                except KeyError:
                    Lvote.append(["inconnu","OUI"])
                k = 2
            else:
                try :
                    Lvote.append([Dictparticipants[str(num[j][0])],"NUL"])
                except KeyError:
                    Lvote.append(["inconnu","NUL"])
                k = 1                                                                                                                                       #En fonction de l'orientation déterminée, on définit si le marqueur vaut
                                                                                                                                                            #OUI, NON ou NUL. On remplir alors la liste avec le participant associé 
                                                                                                                                                            #au marqueur et son vote associé. Si jamais le marqueur n'est pas référencé
                                                                                                                                                            #dans la liste des participants, on fait correspondre le vote à une liste vide
            for i in range (4):
                if i < 3:
                    cv2.line(frame, (int(LCorner[i][0]), int(LCorner[i][1])), (int(LCorner[i+1][0]), int(LCorner[i+1][1])), Coul[k], 2)
                else :
                    cv2.line(frame, (int(LCorner[i][0]), int(LCorner[i][1])), (int(LCorner[0][0]), int(LCorner[0][1])), Coul[k], 2)                         #On trace un cadre autour du marqueur qui change de couleur selon le vote
           
    if Lvote is not None:
        vote = str()
        Lcompte = [0,0,0]                                                                                                              #Initialisation d'une liste contenant le nombre de OUIs, de NONs et de NULs
        StrOui = ''
        StrNon = ''
        StrNul = ''                                                                                                                    #Initialisation de 3 chaines de caractères qui met en relation le vote
                                                                                                                                       #et l'identifiant de la personnes ayant réalisé ce vote
        for i in Lvote :
            vote += " "+i[1]+"({})".format(i[0])
            text1 = "Votes :{}".format(vote)
            cv2.putText(frame, text1, (25,110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)                                           #Affichage à l'écran des votes et par qui ils sont effectués
            cv2.putText(frame, text1, (25,110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (44, 177, 234), 2)
            
            if i[1] == "OUI":
                Lcompte[0] +=1
                StrOui += i[0]+' '
            if i[1] == "NON":
                Lcompte[1] +=1
                StrNon += i[0]+' '
            if i[1] == "NUL":
                Lcompte[2] +=1
                StrNul += i[0]+' '                                                                                                     #Remplissage de Lcompte et des chaines de caractères
    
    if Lcompte is not None and Lcompte!=[0,0,0]:
        text2 = "Votes : {} OUI, {} NON, {} NUL".format(Lcompte[0], Lcompte[1], Lcompte[2])
        cv2.putText(frame, text2, (25,145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)                                               #Affichage du nombre de OUIs, de NONs et de NULs       
        cv2.putText(frame, text2, (25,145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (44, 177, 234), 2)
        
    cv2.imshow('frame', frame)                                                                                                         #Affichage de la capture vidéo modifiée
    
    if cv2.waitKey(1) == ord('q'):   
        break

cap.release()                                                                                                                          #Arrêt de la capture vidéo en cas d'appui sur q
cv2.destroyAllWindows()                               
