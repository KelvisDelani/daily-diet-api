from flask import Flask, request, jsonify 
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db 
from models import User, Meal 
from datetime import datetime

# Rotas para manipulação de usuários

# Essa rota cria um novo usuário no sistema
@app.route('/creater_user', methods=['POST'])
def creater_user():

    # Recebe os dados do usuário
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verifica se o nome de usuário e senha foram fornecidos
    if not username or not password:
        return jsonify({"message": "Nome de usuário e senha são obrigatórios"}), 400

    # Verifica se o usuário já existe no banco de dados
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Usuário já existe"}), 400
    
    # Cria um novo usuário e salva no banco de dados
    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário criado com sucesso"}), 201

# Esta rota permite que um usuário faça login no sistema
@app.route('/login', methods=['POST'])
def login():

    # Recebe os dados do usuário
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Verifica se o nome de usuário e a senha foram fornecidos
        if not username or not password:
            return jsonify({"message": "Nome de usuário e senha são obrigatórios"}), 400
        
        # Verifica se o usuário existe e se a senha está correta
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"message": "Usuário ou senha inválidos"}), 401
        
        # Faz o login do usuário
        login_user(user)
        return jsonify({"message": "Usuário logado com sucesso"}), 200
    except Exception as e:
        return jsonify({"message": "Ocorreu um erro ao tentar fazer login", "error": str(e)}), 500

# Esta rota permite que um usuário logado atualize suas informações        
@app.route('/update', methods=['PUT'])
@login_required
def update_user():

    # Recebe os dados do usuário
    try:
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')

        # Verifica se o novo nome de usuário ou senha foram fornecidos
        if not new_username and not new_password:
            return jsonify({"message": "Nome de usuário e senha são obrigatórios"}), 400
        
        user = User.query.filter_by(id=current_user.id).first()

        # Atualiza o nome de usuário se fornecido
        if new_username:
            if User.query.filter_by(username=new_username).first():
                return jsonify({"message": "Nome de usuário já existe"}), 400
            user.username = new_username

        # Atualiza a senha se fornecida
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso"}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao tentar atualizar o usuário", "error": str(e)}), 500

# Esta rota permite que um usuário logado faça logout do sistema    
@app.route('/logout', methods=['GET'])
@login_required 
def logout():
    logout_user()
    return jsonify({"message": "Usuário deslogado com sucesso"}), 200

# Esta rota permite que um usuário logado delete sua conta
# Ao deletar sua conta, deleta as refeições associadas a ele
@app.route('/delete', methods=['DELETE'])
@login_required
def delete_user():
    try:
        user = current_user
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao tentar deletar o usuário", "error": str(e)}), 500

# Rotas para manipulação de refeições 

# Esta rota permite que um usuário logado crie uma nova refeição
@app.route('/meals', methods=['POST'])
@login_required 
def create_meal():

    # Recebe os dados da refeição
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    date_time = data.get('date_time')
    in_diet = data.get('in_diet')
    user_id = current_user.id

    # Verifica se todos os campos obrigatórios foram preenchidos
    if not all([name, date_time, user_id]):
        return jsonify({"message": "Preencha todos os campos obrigatórios"}), 400

    # Cria uma nova refeição e salva no banco de dados
    meal = Meal(
        name=name,
        description=description,
        date_time=datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S'),
        in_diet=in_diet,
        user_id=user_id 
    )

    db.session.add(meal)
    db.session.commit()

    return jsonify(meal.to_dict()), 201

# Esta rota permite que um usuário logado atualize uma refeição existente
@app.route('/meals/<int:meal_id>', methods=['PUT'])
@login_required
def update_meal(meal_id):

    # Recebe os dados da refeição
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    date_time = data.get('date_time')
    in_diet = data.get('in_diet')
    
    # Verifica se a refeição existe
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()

    if not meal:
        return jsonify({"message": "Refeição não encontrada"}), 404
    
    # Atualiza os campos da refeição se fornecidos
    if name:
        meal.name = name
    if description:
        meal.description = description
    if date_time:
        meal.date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    if in_diet:
        meal.in_diet = in_diet

    db.session.commit()

    return jsonify(meal.to_dict()), 200

# Esta rota permite que um usuário logado delete uma refeição existente
@app.route('/meals/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_meal(meal_id):

    # Verifica se a refeição existe
    try:
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()

        if not meal:
            return jsonify({"message": "Refeição não encontrada"}), 404

        db.session.delete(meal)
        db.session.commit()
        
        return jsonify({"message": "Refeição deletada com sucesso"}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao tentar deletar a refeição", "error": str(e)}), 500

# Esta rota permite que um usuário logado liste todas as suas refeições
@app.route('/meals', methods=['GET'])
@login_required
def list_meals():

    # Lista todas as refeições associadas ao usuário logado
    try:
        meals = Meal.query.filter_by(user_id=current_user.id).all()
        meals_list = [meal.to_dict() for meal in meals]
        return jsonify(meals_list), 200
    except Exception as e:
        return jsonify({"message": "Erro ao tentar listar as refeições", "error": str(e)}), 500

# Esta rota permite que um usuário logado visualize uma refeição específica
@app.route('/meals/<int:meal_id>', methods=['GET'])
@login_required
def get_meal(meal_id):

    # Verifica se a refeição existe
    try:
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()

        if not meal:
            return jsonify({"message": "Refeição não encontrada"}), 404

        return jsonify(meal.to_dict()), 200
    except Exception as e:
        return jsonify({"message": "Erro ao tentar visualizar a refeição", "error": str(e)}), 500