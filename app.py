from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

# Cria uma aplicação Flask
app = Flask(__name__)

# Configurações da aplicação
app.config['SECRET_KEY'] = 'minhasenha'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados e o gerenciador de login
db = SQLAlchemy(app)
login_manager = LoginManager(app)  
login_manager.login_view = 'login' # Define a rota de login

# Importa as rotas da aplicação
from routes import *

# Executa a aplicação
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria todas as tabelas no banco de dados
    app.run(debug=True) # Executa a aplicação em modo de depuração