from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_login import UserMixin, LoginManager, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    word = db.relationship('Word', backref='user', lazy=True)
    category = db.relationship('Category', backref='user', lazy=True)

class Rel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.relationship('Rel', backref='word', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.relationship('Rel', backref='category', lazy=True)

# NEW -------------

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)

# NEW -------------

"""
CONVERSATION CLASS
"""
class ConversationClass:
    
    def get_conversations(self):
        return Conversation.query.filter_by(user_id=user_id())
    
    def add_conversation(self, title):
        print(f"Creating conversation with {title=}")
        new_conversation= Conversation(title=title, user_id=user_id())
        db.session.add(new_conversation)
        db.session.commit()
        return new_conversation
    
    def get_newest_conversation(self):
        conversations = self.get_conversations()

        if conversations.first() == None:
            return self.add_conversation("New conversation")
        else:
            return conversations.order_by(Conversation.id.desc()).first()
        
    def get_sentences_in_conversation(self, conversation_id):
#        results = db.session.query(Conversation, Sentence).join(Sentence, Conversation.id == Sentence.conversation_id).all()
        results = db.session.query(Conversation, Sentence).join(Sentence, Conversation.id == Sentence.conversation_id).filter(Conversation.id == conversation_id).all()
        print(results)
    
        for conversation, sentence in results:
            print(f"Conversation ID: {conversation.id}, Sentence ID: {sentence.id}, Sentence Text: {sentence.content}, Role {sentence.role}")


""" 
VOCABULARY CLASS 
"""
class VocabClass:
    
    """ GETTERS """
    def get_word_entry(self, word):
        return Word.query.filter_by(title=word, user_id=user_id()).first()
    
    def get_category_entry(self, category):
        return Category.query.filter_by(title=category, user_id=user_id()).first()
    
    def get_word_note(self, word):
        word_entry = self.get_word_entry(word)
        return word_entry.note if word_entry else ""

    def get_category_note(self, category):
        category_entry = self.get_category_entry(category)
        return category_entry.note if category_entry else ""
    
    def get_category(self, word):
        word_entry = self.get_word_entry(word)
        
        if word_entry:
            category_entry = Rel.query.filter_by(word_id=word_entry.id).first()
            
            if category_entry:
                category = Category.query.get(category_entry.category_id)
                return category.title
            else:
                return "Category not found for the word"
        else:
            return "Word not found"
            
    def get_known_words(self):
        words = Word.query.filter_by(user_id=user_id())
        return [word.title for word in words]
    
    def get_known_categories(self):
        categories = Category.query.filter_by(user_id=user_id())
        return [category.title for category in categories]
    
    def get_words_in_category(self, category):
        category_entry = self.get_category_entry(category)
    
        if category_entry:
            word_ids = [rel.word_id for rel in Rel.query.filter_by(category_id=category_entry.id).all()]
    
            if word_ids:
                words = Word.query.filter(Word.id.in_(word_ids)).all()
                return [word.title for word in words]
    
        return []

    """ SETTERS """
    def add_word(self, word, note):
        new_word= Word(title=word, note=note, user_id=user_id())
        db.session.add(new_word)
        db.session.commit()
        return new_word
    
    def add_category(self, category, note):
        new_category = Category(title=category, note=note, user_id=user_id())
        db.session.add(new_category)
        db.session.commit()
        return new_category
    
    def set_word_note(self, word, note):
        word_entry = self.get_word_entry(word)
    
        if word_entry:
            word_entry.note = note
            db.session.commit()
            return word_entry
        else:
            return self.add_word(word, note)


    def set_category_note(self, category, note):
        category_entry = self.get_category_entry(category)
        
        if category_entry:
            category_entry.note = note
            db.session.commit()
            return category_entry
        else:
            return self.add_category(category, note)
    
    def set_word_category(self, word, category):
        word_entry = self.get_word_entry(word)
    
        if word_entry:
            category_entry = self.get_category_entry(category)
            
            if not category_entry:
                category_entry = self.add_category(category, "")
    
            rel_entry = Rel.query.filter_by(word_id=word_entry.id).first()
            
            if rel_entry:
                rel_entry.category_id = category_entry.id
            else:
                new_rel_entry = Rel(word_id=word_entry.id, category_id=category_entry.id)
                db.session.add(new_rel_entry)

            db.session.commit()

def get_user_id(self):
    if current_user.is_authenticated:
        return current_user.get_id()
    else:
        return None

def user_id():
    return current_user.get_id()

def get_logged_in_username():
    user = User.query.filter_by(id=user_id()).first()
    return user.username if user else ""