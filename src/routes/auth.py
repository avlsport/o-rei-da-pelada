from flask import Blueprint, request, jsonify, session
from src.models.jogador import Jogador, db
from werkzeug.security import generate_password_hash, check_password_hash
import os

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    try:
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        posicao = request.form.get("posicao")
        foto = request.files.get("foto")

        if not nome or not email or not senha or not posicao:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        if Jogador.query.filter_by(email=email).first():
            return jsonify({"error": "Email já cadastrado"}), 400

        novo_jogador = Jogador(
            nome=nome,
            email=email,
            posicao=posicao,
            foto_url=None # Será atualizado após salvar a foto
        )
        novo_jogador.set_senha(senha)

        foto_url = None
        if foto:
            filename = f"{os.urandom(16).hex()}_{foto.filename}"
            foto_path = os.path.join(os.getcwd(), "src", "uploads", filename)
            foto.save(foto_path)
            foto_url = f"/uploads/{filename}"
            novo_jogador.foto_url = foto_url

        db.session.add(novo_jogador)
        db.session.commit()

        return jsonify({
            "message": "Usuário registrado com sucesso",
            "id": novo_jogador.id,
            "nome": novo_jogador.nome,
            "email": novo_jogador.email,
            "posicao": novo_jogador.posicao,
            "foto_url": novo_jogador.foto_url
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        senha = data.get("senha")

        jogador = Jogador.query.filter_by(email=email).first()

        if not jogador or not jogador.check_senha(senha):
            return jsonify({"error": "Email ou senha inválidos"}), 401

        session["jogador_id"] = jogador.id
        session.permanent = True # Torna a sessão permanente

        return jsonify({
            "id": jogador.id,
            "nome": jogador.nome,
            "email": jogador.email,
            "posicao": jogador.posicao,
            "foto_url": jogador.foto_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.pop("jogador_id", None)
    return jsonify({"message": "Logout realizado com sucesso"}), 200

@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    jogador_id = session.get("jogador_id")
    if not jogador_id:
        return jsonify({"error": "Não autenticado"}), 401

    jogador = Jogador.query.get(jogador_id)
    if not jogador:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({
        "id": jogador.id,
        "nome": jogador.nome,
        "email": jogador.email,
        "posicao": jogador.posicao,
        "foto_url": jogador.foto_url
    }), 200


