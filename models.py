from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime

# Classe que representa um usuário no banco de dados
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True) # Indentificador único de usuário 
    username = db.Column(db.String(80), unique=True, nullable=False) # Nome de usuário único
    password_hash = db.Column(db.String(120), nullable=False) # Senha criptografada do usuário

    # Método para definir a senha do usuário
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    # Método para verificar se a senha está correta
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Função para carregar um usuário pelo seu id   
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

# Classe que representa uma refeição no banco de dados
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Identificador único da refeição
    name = db.Column(db.String(100), nullable=False) # Nome da refeição
    description = db.Column(db.String(200), nullable=True) # Descrição da refeição
    date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) # Data e hora da refeição
    in_diet = db.Column(db.Boolean, default=True, nullable=False) # Indica se a refeição está na dieta
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # ID do usuário que registrou a refeição
    # Relacionamento com o usuário. Quando um usuário é deletado, todas as refeições associadas a ele também são deletadas
    user = db.relationship('User', backref=db.backref('meals', lazy=True, cascade="all, delete-orphan"))

    # Construtor da classe Meal
    def __init__(self, name, description, date_time, in_diet, user_id):
        self.name = name # Atribui o nome da refeição
        self.description = description # Atribui a descrição da refeição
        self.date_time = date_time # Atribui a data e hora da refeição 
        self.id_diet = in_diet # Atribui se a refeição está na dieta
        self.user_id = user_id # Atribui o ID do usuário que registrou a refeição

    # Método para atualizar os dados de uma refeição 
    def update_meal(self, name, description, date_time, in_diet):
        self.name = name # Atualiza o nome da refeição
        self.description = description # Atualiza a descrição da refeição
        self.date_time = date_time # Atualiza a data e hora da refeição
        self.in_diet = in_diet # Atualiza se a refeição está na dieta
        db.session.commit() 

    # Método estático para deletar uma refeição pelo seu ID
    @staticmethod
    def delete_meal(meal_id): 

        # Busca a refeição pelo ID
        meal = Meal.query.get(meal_id)
        if meal:
            db.session.delete(meal)
            db.session.commit()
    
    # Método estático para obter todas as refeições de um usuário
    @staticmethod
    def get_all_meals(user_id):
        return Meal.query.filter_by(user_id=user_id).all()
    
    # Método estático para obter uma refeição pelo seu ID
    @staticmethod
    def get_meal(meal_id):
        return Meal.query.get(meal_id)
    
    # Método para converter a refeição em um dicionário
    def to_dict(self):
        return {
            'id': self.id, 
            'name': self.name,
            'description': self.description,
            'date_time': self.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'in_diet': self.in_diet,
            'user_id': self.user_id
        }