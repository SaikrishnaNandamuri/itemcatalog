# !/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as session_for_login
from flask import make_response, jsonify
from sqlalchemy import desc
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os
import random
import string
import httplib2
import json
import requests
from flask import Flask, render_template, request, url_for
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from database_setup import Costumes, Base, Items, Users

file_handle = open('client_secret.json', 'r')

CLIENT_ID = json.loads(file_handle.read())['web']['client_id']

file_handle.close()
Base = declarative_base()
engine = create_engine("sqlite:///costumes.db")
Base.metadata.create_all(engine)

session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)


@app.route('/read')
def read():
    print('i am in read')
    costume = session.query(Costumes).first()
    return str(costume.name)


@app.route('/')
@app.route('/costumes')
def home():
    items = session.query(Items).order_by(desc(Items.item_id)).limit(6).all()
    return render_template("normal.html", items=items)


# To display the categories
@app.route('/category')
def showCategory():
    if request.method == "GET":
        costumes = session.query(Costumes).all()
        return render_template("showcategory.html", costumes=costumes)
    else:
        return "Unsuccessful to show categories"


# To create a new category
@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    if 'email' not in session_for_login:
        flash('Please login and after try again')
        return redirect(url_for('home'))
    email = session_for_login['email']
    user_id = getUserID(email)
    if user_id is None:
        flash('email not found')
        return redirect(url_for('home'))

    print('i am in newcategory')
    if request.method == 'GET':
        return render_template("newcategory.html")
    else:
        print('else')
        costume_name = request.form['name']
        user_id = user_id
        costumeObj = Costumes(name=costume_name, user_id=user_id)
        session.add(costumeObj)
        session.commit()
        flash('Category successfully created')
        return redirect(url_for('home'))


# To edit the selected category with category id
@app.route('/category/<int:category_id>/edit', methods=["GET", "POST"])
def editCategory(category_id):
    if 'email' not in session_for_login:
        flash('Please, login and try again')
        return redirect(url_for('home'))
    email = session_for_login['email']
    user_id = getUserID(email)
    if user_id is None:
        flash('email not found')
        return redirect(url_for('home'))
    costume = session.query(Costumes).filter_by(
        category_id=category_id).one_or_none()
    if costume is None:
        flash('category not found')
        return redirect(url_for('home'))
    if costume.user_id != user_id:
        flash('You are not admin to this category')
        return redirect(url_for('home'))

    if request.method == "GET":
        costume = session.query(Costumes).filter_by(
            category_id=category_id).one_or_none()
        return render_template(
            "editcategory.html",
            old_name=costume.name, category_id=costume.category_id)
    else:
        costume = session.query(Costumes).filter_by(
            category_id=category_id).one_or_none()
        costume_name = request.form['name']
        costume.name = costume_name
        session.add(costume)
        session.commit()
        flash('name updated')
        return redirect(url_for('home'))


# To delete the category of given category id
@app.route('/category/<int:category_id>/delete')
def deleteCategory(category_id):
    if 'email' not in session_for_login:
        flash('Please,login and try again')
        return redirect(url_for('home'))
    email = session_for_login['email']
    user_id = getUserID(email)
    costume = session.query(Costumes).filter_by(
        category_id=category_id).one_or_none()
    if costume is None:
        flash('category not found')
        return redirect(url_for('home'))
    if costume.user_id != user_id:
        flash('You are not admin to this category')
        return redirect(url_for('home'))
    if costume:
        name = costume.name
        session.delete(costume)
        session.commit()
        flash(str(name)+" deleted successfully")
        return redirect(url_for('home'))
    else:
        flash("Category deletion unsuccessful")
        return redirect(url_for('home'))


# To remove the selected category which created by current user
@app.route('/removecategory', methods=['POST', 'GET'])
def removeCategory():
    if request.method == "POST":
        category_id = request.form['category']
        print('\n\n\ncategory:', category_id)
        category = session.query(Costumes).filter_by(
            category_id=category_id).one_or_none()
        if category and 'email' in session_for_login:
            # name = item.name
            session.delete(category)
            session.commit()
            flash('Removed successfully')
            return redirect(url_for('home'))
        else:
            flash('Please,login and try again')
            return redirect(url_for('home'))
    else:
        email = session_for_login['email']
        categories = session.query(Costumes).filter_by(
            user_id=getUserID(email))
        return render_template("removeCategory.html", categories=categories)


# To display the items which are present in the category of given category id
@app.route('/category/<int:category_id>')
@app.route('/category/<int:category_id>/items')
def showItems(category_id):
    if request.method == "GET":
        items = session.query(Items).filter_by(
            category_id=category_id).all()
        return render_template(
            "showitems.html", items=items, category_id=category_id)
    else:
        flash("Unsuccessful to show Items")
        return redirect(url_for('home'))


# To show the details of given item id present in given category id
@app.route(
    '/category/<int:category_id>/<int:item_id>/', methods=["GET", "POST"])
def showItemDetails(category_id, item_id):
    if request.method == "GET":
        item = session.query(Items).filter_by(
            item_id=item_id).one_or_none()
        return render_template("showitemdetails.html", item=item)
    else:
        flash('Item unavailable')
        return redirect(url_for('home'))


# To create the new item in the selected category
@app.route('/category/<int:category_id>/new', methods=["GET", "POST"])
def newItem(category_id):
    if 'email' not in session_for_login:
        flash('Please,login and try again')
        return redirect(url_for('home'))
    email = session_for_login['email']
    user_id = getUserID(email)
    costume = session.query(Costumes).filter_by(
        category_id=category_id).one_or_none()
    if costume is None:
        flash('Category not found')
        return redirect(url_for('home'))
    if costume.user_id != user_id:
        flash('You are not admin.You cannot add new item in this category')
        return redirect(url_for('home'))
    if request.method == "GET":
        return render_template("newitem.html", category_id=category_id)
    else:
        item_name = request.form['name']
        item_wtype = request.form['wtype']
        item_ctype = request.form['ctype']
        item_gender = request.form['gender']
        item_price = request.form['price']
        item_brand = request.form['brand']
        item_image_url = request.form['image_url']
        itemObj = Items(
            name=item_name, wtype=item_wtype,
            ctype=item_ctype, gender=item_gender,
            price=item_price, brand=item_brand,
            image_url=item_image_url,
            category_id=category_id)
        session.add(itemObj)
        session.commit()
        flash("Item successfully created")
        return redirect(url_for('home'))


# To edit the item of given item id present in given category id
@app.route(
    '/category/<int:category_id>/<int:item_id>/edit', methods=["GET", "POST"])
def editItem(category_id, item_id):
    if 'email' not in session_for_login:
        flash('Please, Login and try again later')
        return redirect(url_for('home'))
    email = session_for_login['email']
    user_id = getUserID(email)
    costume = session.query(Costumes).filter_by(
        category_id=category_id).one_or_none()
    if costume is None:
        flash('Category not found')
        return redirect(url_for('home'))
    if costume.user_id != user_id:
        flash('You are not admin.You cannot edit item in this category')
        return redirect(url_for('home'))
    if request.method == "GET":
        item = session.query(Items).filter_by(
            item_id=item_id).one_or_none()
        return render_template(
            "edititem.html", old_name=item.name,
            old_wtype=item.wtype, old_ctype=item.ctype,
            old_gender=item.gender, old_price=item.price,
            old_brand=item.brand, old_image_url=item.image_url,
            category_id=item.category_id, item_id=item.item_id)
    else:
        item = session.query(Items).filter_by(item_id=item_id).one()
        item_name = request.form['name']
        item.name = item_name
        item_wtype = request.form['wtype']
        item.wtype = item_wtype
        item_ctype = request.form['ctype']
        item.ctype = item_ctype
        item_gender = request.form['gender']
        item.gender = item_gender
        item_price = request.form['price']
        item.price = item_price
        item_brand = request.form['brand']
        item.brand = item_brand
        item_image_url = request.form['image_url']
        item.image_url = item_image_url
        session.add(item)
        session.commit()
        flash("Item successfully updated")
        return redirect(url_for('home'))


# To remove the item of given item id present in the given category id
@app.route(
    '/category/<int:category_id>/<int:item_id>/delete',
    methods=["GET", "POST"])
def deleteItem(category_id, item_id):
    if 'email' not in session_for_login:
        flash('Please, Login and try again')
        return redirect(url_for('home'))
    email = session_for_login['email']
    user_id = getUserID(email)
    costume = session.query(Costumes).filter_by(
        category_id=category_id).one_or_none()
    if costume is None:
        flash('Category not found')
        return redirect(url_for('home'))
    if costume.user_id != user_id:
        flash('You are not admin.You cannot delete items in this category')
        return redirect(url_for('home'))
    item = session.query(Items).filter_by(
        item_id=item_id, category_id=category_id).one()
    if item:
        name = item.name
        session.delete(item)
        session.commit()
        flash(str(name)+" deleted successfully")
        return redirect(url_for('home'))
    else:
        flash("Item deletion unsuccessful")
        return redirect(url_for('home'))


# login routing
@app.route('/glogin')
def glogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session_for_login['state'] = state
    return render_template('googlelogin.html', STATE=state)


# it helps the user to loggedin and display flash profile
@app.route('/glogout')
def glogout():
    if 'email' in session_for_login:
        return gdisconnect()
    return redirect(url_for('home'))


# GConnect
@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != session_for_login['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')
    # Obtain authorization code
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            """Failed to upgrade the authorisation code"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    myurl = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    header = httplib2.Http()
    result = json.loads(header.request(myurl, 'GET')[1].decode('utf-8'))

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_access_token = session_for_login.get('access_token')
    stored_gplus_id = session_for_login.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    session_for_login['access_token'] = credentials.access_token
    session_for_login['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION
    session_for_login['email'] = data['email']
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = addUser()
    session_for_login['user_id'] = user_id
    flash("Welcome{}".format(session_for_login['email']))
    return "Login success"


def addUser():
    email = session_for_login['email']
    user = Users(email=email)
    session.add(user)
    session.commit()
    user = session.query(Users).filter_by(email=email).first()
    return user.user_id


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.user_id
    except Exception as e:
        print('\n'*5, 'Error', e)
        return None


# Gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    del session_for_login['email']
    # Only disconnect a connected user.
    access_token = session_for_login.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    print('\n'*5, 'SAI error', url)
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del session_for_login['access_token']
        del session_for_login['gplus_id']
        response = redirect(url_for('home'))
        response.headers['Content-Type'] = 'application/json'
        flash("successfully Logout", "success")
        return response
    else:

        # if given token is invalid, unable to revoke token
        response = make_response(json.dumps('Failed to revoke token for user'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.context_processor
def inject_to_parent():
    costumes = session.query(Costumes).all()
    return dict(costumes=costumes)


# Json points
@app.route('/costumes.json')
def costumesJson():
    costumes = session.query(Items).all()
    return jsonify(Costumes=[costume.serialize for costume in costumes])


@app.route('/costumes/<int:category>.json')
def eachCostumeJson(category):
    costumes = session.query(Items).filter_by(
            category_id=category
            ).all()
    return jsonify(Costumes=[costume.serialize for costume in costumes])


if __name__ == "__main__":
    app.secret_key = 'supersecretkey123@'
    app.run()
