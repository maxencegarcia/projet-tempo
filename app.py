#! /usr/bin/python3
# -*- coding:utf-8 -*-

import os
import pymysql.cursors
from flask import (
    Flask, request, render_template, redirect,
    url_for, abort, flash, session, g
)
from dotenv import load_dotenv

# Charge .env en local uniquement (Railway ignore)
load_dotenv()

# --------------------
# App Flask
# --------------------
app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "une-cle-secrete-en-local"
)

# --------------------
# Database
# --------------------
def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=os.environ.get("MYSQLHOST"),
            user=os.environ.get("MYSQLUSER"),
            password=os.environ.get("MYSQLPASSWORD"),
            database=os.environ.get("MYSQLDATABASE"),
            port=int(os.environ.get("MYSQLPORT", 3306)),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# --------------------
# Blueprints imports
# --------------------
from controllers.auth_security import auth_security
from controllers.fixtures_load import fixtures_load

from controllers.client_ski import client_ski
from controllers.client_panier import client_panier
from controllers.client_commande import client_commande
from controllers.client_commentaire import client_commentaire
from controllers.client_coordonnee import client_coordonnee
from controllers.client_liste_envies import client_liste_envies

from controllers.admin_ski import admin_ski
from controllers.admin_declinaison_ski import admin_declinaison_ski
from controllers.admin_commande import admin_commande
from controllers.admin_type_ski import admin_type_ski
from controllers.admin_dataviz import admin_dataviz
from controllers.admin_commentaire import admin_commentaire

# --------------------
# Middleware sécurité
# --------------------
@app.before_request
def before_request():
    if request.path.startswith(("/admin", "/client")):
        if "role" not in session:
            return redirect("/login")

        if (
            request.path.startswith("/client")
            and session["role"] != "ROLE_client"
        ) or (
            request.path.startswith("/admin")
            and session["role"] != "ROLE_admin"
        ):
            session.clear()
            flash("Accès non autorisé", "alert-warning")
            return redirect("/logout")

# --------------------
# Routes
# --------------------
@app.route("/")
def show_accueil():
    if "role" in session:
        if session["role"] == "ROLE_admin":
            return redirect("/admin/commande/index")
        return redirect("/client/ski/show")
    return render_template("auth/layout.html")

# --------------------
# Register blueprints
# --------------------
app.register_blueprint(auth_security)
app.register_blueprint(fixtures_load)

app.register_blueprint(client_ski)
app.register_blueprint(client_panier)
app.register_blueprint(client_commande)
app.register_blueprint(client_commentaire)
app.register_blueprint(client_coordonnee)
app.register_blueprint(client_liste_envies)

app.register_blueprint(admin_ski)
app.register_blueprint(admin_declinaison_ski)
app.register_blueprint(admin_commande)
app.register_blueprint(admin_type_ski)
app.register_blueprint(admin_dataviz)
app.register_blueprint(admin_commentaire)

# --------------------
# Local run only
# --------------------
if __name__ == "__main__":
    app.run(debug=True)
