import re
from flask import request, jsonify, render_template, flash, make_response, redirect, url_for
from countries import app, db
from flask_login import current_user, login_user, login_required, logout_user

#import models
from models.user import User
from models.country import Country
from models.address import Address
#
from user_forms import LoginForm, RegisterForm
import users_view, addresses_view
import country.views

def check_password_valid(password):
    if len(password) < 8:
        return False
        # return false if password is less than 8 characters
    elif re.search(r"\d", password) is None:
        return False
        # return false if password does not contain digits
    elif re.search(r"[A-Z]", password) is None:
        return False
        # return false if password does not contain uppercase characters
    elif re.search(r"[a-z]", password) is None:
        return False
        # return false if password does not contain lowercase characters
    elif re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
        return False
        # return false if password does not contain lowercase characters
    else:
        return True


def check_email(self,field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Your email is already registered!')

def check_username(self,field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('username is already taken!')



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('you logged out')
    return redirect(url_for('country.index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user = None
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form["email"]).first()
        if (user != None) and (user.check_password(request.form["password"])):
            app.logger.info(f'{user.username} logged in successfully')
            login_user(user)
            flash(f'user {request.form["email"]} logged in', 'info')
            next = request.args.get('next')
            if (next == None) or (not next[0]=='/'):
                next = url_for('country.index')
            return redirect(next)
        else:
            flash(f'User not found or wrong password', 'danger')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register/', methods=['POST','GET'])
@app.route('/register', methods=['POST','GET'])
def register():
    hashed_password=picture=firstname=middlename=lastname=email=""
    if request.method == 'GET': # show register page
        form = RegisterForm()
        return render_template('register.html', title="registration", form=form)
    elif request.method == 'POST': # register user sent via POST:
        # if email exist then user is already registered
        #return f"<h1>{request.form['firstname']} | {request.form['lastname']} | {request.form['email']}</h1>"
        #user = User({request.form['firstname']},{request.form['lastname']},{request.form['email']})
        if ('email' in request.form) or ('email'in request.args):
            email = request.form['email']
            test = User.query.filter_by(email=email).first()
            if test:
                return jsonify(message='That email already exists.'), 409
        if 'middlename' in request.form:
            middlename = request.form["middlename"]
        else:
            middlename = ""
        if 'picture' in request.form:
            picture = request.form['picture']
        else:
            picture = "defaultuser.png"
        user = User("","","","","","","")
        if 'password' in request.form:
            if check_password_valid(request.form["password"]):
                hashed_password = user.set_password(request.form["password"])
            else:
                flash("please enter a complex password")
                form = RegisterForm()
                return render_template('register.html', title="registration", form=form)
        user.firstname = request.form["firstname"]
        user.middlename = middlename
        user.lastname = request.form["lastname"]
        user.email = request.form["email"]
        user.username = request.form["username"]
        user.picture = picture
        db.session.add(user)
        try:
            db.session.commit()
            flash('user registered successfully',category='info')
        except:
            flash('user registration encountered an issue','error')
        return render_template('login.html',form = LoginForm(),title="Sign in"), 201
    else:
        return f"<p>Invalid method: {request.method}</p>", 408
