import requests, re
from countries import app, db
from flask import Blueprint, request, jsonify, render_template, flash, make_response, redirect, url_for
from flask_login import login_required, login_user, logout_user
from models.country import Country

from user_forms import LoginForm, RegisterForm
import json

country = Blueprint("country", __name__, template_folder="templates", static_folder="static")


@country.errorhandler(401)
def unauthorized(e):
    # set the 401 status explicitly
    flash('unauthorized access please login')
    form = LoginForm()
    return render_template('login.html',title='Sign in',form=form), 401

def syncCountries():
    #### Load countries from API call api.countrylayer.com
    #access_key ="075b22ca9daf90656f7b81e7e6007201"
    #base_url = "http://api.countrylayer.com/v2"
    #params={"content-type": "application/json"}
    #countries = requests.get(base_url + "/all" + "?access_key=" + access_key , params=params)
    #### Alternative load from JSON file
    file = open("countries.json", encoding="utf8")
    countries = json.load(file)
    file.close()
    #
    for country in countries:
        if country["name"]:
            c = Country(name=country["name"],topLevelDomain=country["topLevelDomain"],alpha2Code=country["alpha2Code"],alpha3Code=country["alpha3Code"],callingCodes=country["callingCodes"],region=country["region"],capital=country["capital"])
            c.name=country["name"]
            c.topLevelDomain=country["topLevelDomain"]
            c.alpha2Code=country["alpha2Code"]
            c.alpha3Code=country["alpha3Code"]
            c.callingCodes=country["callingCodes"]
            c.region=country["region"]
            c.capital=country["capital"]
            app.logger.info(f'{country["name"]} - {country["topLevelDomain"]} - {country["alpha2Code"]} - {country["alpha3Code"]} - {country["callingCodes"]} - {country["capital"]} - {country["region"]}')
            db.session.add(c)
            db.session.commit()
    return countries

def getCountries():
    return Country.query.all()

@country.route('/index')
@country.route('/')
@login_required
def index():
    title = "Countries list"
    countries = getCountries()
    app.logger.info(countries)
    columns = None
    if countries and countries[0]:
        countries = getCountries()
        columns = vars(countries[0]).items() # <-- get properties of the first Country object instance 
    else:
        countries = syncCountries()
    return render_template('index.html', title = title, countries = countries, columns = columns)

@country.route('/search', methods=['GET','POST'])
def search(country):
    if request.method == 'POST':
        if country == "":
            #countries = getCountries()
            flash('please enter country name to search for a country','danger')
            return render_template('index.html', title = title, countries = countries)
        else:
            coutry = request.args 
            country = [Country.query.filter_by(name=country).first()]
            return redirect('index.html',countries=country)
    else:
        title = "countries"
        #countries = getCountries()
        return render_template('index.html', title = title, countries = countries)
