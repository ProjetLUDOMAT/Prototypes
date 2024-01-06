![](photo_1.png).

## Introduction

Le deuxième prototype possède la même structure que Proto 1 : Raspberry Pico (RP2) programmé en micropython, deux moteurs à courant continu pilotés par un double pont en H (L293D), transmission des commandes infra-rouges au RP2 par un ESP01.

Plusieurs différences cependant : le chassis, les moteurs et les roues proviennent d'un kit Aliexpress, les encodeurs optiques des moteurs sont des encodeurs à une seule voie (pas de détection du sens de rotation) et à très faible résolution (20 pulses par tour de roue, il est donc compliqué d'obtenir des déplacements précis), et l'alimentation est assurée par 4 piles AA de 1,5V (ou 4 accus NiMh de 1,2V). Ce dernier choix permet d'alimenter directement le RP2 sans passer par un régulateur de tension.

## Schéma electrique

![](Schema.svg).

## Réalisation

![](photo_2.png).

Pour simplifier et compte tenu de la taille du chassis, les connections sont réalisées sur deux breadboards.

Le diamètre des roues est de 65mm.

Pour Palier l'absence de deuxième voie sur les encodeurs, les broches 1 et 3 du RP2 sont connectées (resp.) aux broches 14 et 17 (dont l'état donne le sens de la commande des moteurs, et non le sens réel).

![](photo_3.png).


## Installation

Identique à celle de Proto 1 :

- Avec l'IDE Arduino, téléverser le fichier _IRrecvDemo.ino_ dans l'_ESP01_. Ce dernier est alors programmé pour recevoir en continu les signaux de la télécommande et les transmettre au _RP2_ sur la liaison série UART1. La vitesse de transmission est fixée à 9600 bauds, mais elle peut être augmentée à 115200 bauds sans difficulté. Par défaut, le codage IR utilisé est celui de la télécommande ci-dessus ("chinoise"). Il est possible d'utiliser un autre modèle à condition de remplacer le fichier _codes_chi.py_ par un fichier contenant les nouveaux codes. Ci-dessus, _codes_pan.py_ = Panasonic, _codes_phi.py_ = Philips, _codes_sam.py_ = samsung.
- Charger ensuite l'interpreteur micropython sur la carte RP2, puis copier les fichiers .py ci-dessus dans le répertoire principal. A la mise sous tension le robot est prêt à fonctionner.

## Fonctionnement

![](telecommande.png)

## Code

- __dcMotor.py__ : driver de moteur à courant continu.
- __PioEncoder.py__ : driver d'encodeur optique. Il est basé sur les machines d'état (Pio) du RP2.
- __codes_chi.py__ : codes infra-rouges de la télécommande (avec la fonction de lecture _decode_ir_).
- __proto_ludomat_2.py__ : script principal
  
  Lla fonction _go_position_ qui permet d'atteindre la position cible contient un correcteur proportionnel pour chacun des moteurs (au contraire de Proto 1, la correction PD n'est pas nécéssaire ici). L'arrêt du moteur se fait à l'interieur d'un intervalle centré sur la position cible (_tgt_count_) de largeur _dead_zone_=1. L'erreur de position linéaire est donc au maximum de : 1/20 x pi x 65 = 10 mm pour chacune des roues, ce qui est assez médiocre. Pour une améloriation de la précision, voir le code d'Arnaud.
