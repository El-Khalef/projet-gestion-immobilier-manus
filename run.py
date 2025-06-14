#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Point d'entrée principal de l'application Flask.
Ce fichier permet de lancer l'application en mode développement.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


