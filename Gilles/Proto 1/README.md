# Introduction

Ce premier prototype est basé sur un Raspberry Pico (RP2) programmé sous micropython.

Il utilise deux moteurs à courant continu munis chacun d'un encodeur optique et alimentés par un double pont en H. Le pilotage est fait par télécommande infra-rouge. Pour simplifier, la réception et la transmission des commandes au RP2 utilise une diode infra-rouge et un ESP01 programmé pour cette tâche.

L'alimentation des moteurs se fait en 12V (3 accus Li-ion). Un convertisseur buck-boost fournit les 5V nécessaires au RP2.

# Schéma electrique

# Liste de matériel
