from flask import render_template, url_for, redirect, flash, request, jsonify
from flask_login import login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from database import app, db, bcrypt, login_manager, User, VocabClass, ConversationClass, get_logged_in_username # Word, Category, Rel, 
from gpt import ChatBot

"""
Login
"""
class RegisterForm(FlaskForm):
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username placeholder"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password placeholder"})
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""
RENDER PAGES
"""
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    print("LOGOUT!")
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"New user: {form.username.data}, {form.password.data}, {hashed_password}")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/')
def index():
    db.create_all() # ToDo should this really be here?
    return render_template('index.html')

@app.route('/conversation')
@login_required
def conversation():
    return render_template('conversation.html')

@app.route('/vocabulary')
@login_required
def vocabulary():
    return render_template('vocabulary.html')

@app.route('/top_bar')
def top_bar():
    return render_template('top_bar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('conversation'))
            else:
                flash('Invalid username or password', 'danger');
        else:
            flash('Invalid username or password', 'danger');
    return render_template('login.html', form=form)

@app.route('/user')
def user():
    return render_template('user.html')

""" 
GETTERS
"""
def get(key):
    if key in request.form:
        val = request.form[key]
    else:
        print(f"[WARNING] key {key} not found in {request.form.keys()}")
        val = ""    
    return val.strip().lower()

@app.route('/get_newest_conversation', methods=['POST'])
def get_newest_conversation():
    conversation.get_sentences_in_conversation(1)
    
    
    title = conversation.get_newest_conversation().title
    print(f"Conversation title: {title}")
    return jsonify({'title': title})

@app.route('/get_username', methods=['POST'])
def get_username():
    username = get_logged_in_username()
    return jsonify({'username': username})

@app.route('/get_category_info', methods=['POST'])
def get_category_info():
    """ Input can be both a word and a category """
    category = request.form['category'] if 'category' in request.form else vocab.get_category(request.form['word'])
    
    category_notes = vocab.get_category_note(category)
    words_in_category = vocab.get_words_in_category(category)
    return jsonify({'category': category, 'category_notes': category_notes, 'words_in_category': words_in_category})

@app.route('/get_word_info', methods=['POST'])
def get_word_info():
    word = get('word')
    
    word_note = vocab.get_word_note(word)
    category = vocab.get_category(word)
    category_note = vocab.get_category_note(category)
    return jsonify({'word_note': word_note, 'category': category, 'category_note': category_note})

@app.route('/get_vocabulary', methods=['POST'])
def get_vocabulary():
    return jsonify({'categories': vocab.get_known_categories(), 'words': vocab.get_known_words()})

@app.route('/get_words_in_category', methods=['POST'])
def get_words_in_category():
    category = get('category')
    
    return jsonify({'words_in_category': vocab.get_words_in_category(category)})


"""
SETTERS
"""
@app.route('/set_word_note', methods=['POST']) # Done
def set_word_note():
    selectedWord = get('selectedWord')
    text = get('text')
    
    vocab.set_word_note(selectedWord, text)    
    return ""

@app.route('/set_word_category', methods=['POST'])
def set_word_category():
    word = get('word')
    category = get('category')
    
    vocab.set_word_category(word, category)
    return ""

@app.route('/set_category_note', methods=['POST'])
def set_category_note():
    category = get('selectedCategory')
    text = get('text')
    
    vocab.set_category_note(category, text)
    return ""

@app.route('/insert_into_chat', methods=['POST'])
def insert_into_chat():
    user_input = request.json.get('text', '')
    
    response = "Hello world"
    
    return get_message_div(user_input, "chat-box doubleClickable") + get_message_div(response, "chat-box doubleClickable right")


"""
Homemade html utils (ToDo replace with built-in methods)
"""
def get_message_div(sentence, classes=None):
    spans = sentence2spans(sentence)
    
    out = get_element("p", spans, classes=classes)
    out = get_element("div", out)
    return out

def get_element(element, content, classes=None, id=None):
    """
    returns a formattet html element
    """
    s = f"<{element}"
    if classes:
        s += ' class="' + ' '.join(classes.split(" ")) + '"'
        
    if id:
        s += f' id="{id}"'
        
    s += f'>{content}</{element}>'
    return s

def sentence2spans(sentence):
    """
    gives each word in the sentence its separate 'span' element and class 'black'
    """
    return "\n".join([f'<span class="black">{word} </span>' for word in sentence.split(' ')])


#%%
vocab = VocabClass()
conversation = ConversationClass()

if __name__ == '__main__':
    app.run(debug=False)
