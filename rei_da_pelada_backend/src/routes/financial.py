from flask import Blueprint, jsonify, request, session
from datetime import datetime, date
from src.models.user import User, Pelada, PeladaMember, FinancialRecord, db

financial_bp = Blueprint('financial', __name__)

def require_auth():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def require_pelada_member(pelada_id, user_id):
    """Verificar se o usuário é membro aprovado da pelada"""
    return PeladaMember.query.filter_by(user_id=user_id, pelada_id=pelada_id, is_approved=True).first()

def require_pelada_admin(pelada_id, user_id):
    """Verificar se o usuário é admin da pelada"""
    return PeladaMember.query.filter_by(user_id=user_id, pelada_id=pelada_id, is_admin=True).first()

@financial_bp.route('/peladas/<int:pelada_id>/financial', methods=['GET'])
def get_financial_records(pelada_id):
    """Obter registros financeiros de uma pelada"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é membro da pelada
    if not require_pelada_member(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    records = FinancialRecord.query.filter_by(pelada_id=pelada_id).order_by(FinancialRecord.date.desc()).all()
    
    # Calcular totais
    total_income = sum(record.amount for record in records if record.type == 'income')
    total_expense = sum(record.amount for record in records if record.type == 'expense')
    balance = total_income - total_expense
    
    result = {
        'records': [record.to_dict() for record in records],
        'summary': {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance
        }
    }
    
    return jsonify(result), 200

@financial_bp.route('/peladas/<int:pelada_id>/financial', methods=['POST'])
def add_financial_record(pelada_id):
    """Adicionar registro financeiro (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.json
        
        # Validação dos campos obrigatórios
        required_fields = ['description', 'amount', 'type', 'date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Validar tipo
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': 'Tipo deve ser income ou expense'}), 400
        
        # Validar valor
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Valor deve ser positivo'}), 400
        except ValueError:
            return jsonify({'error': 'Valor inválido'}), 400
        
        # Converter data
        try:
            record_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Data inválida'}), 400
        
        # Criar registro
        record = FinancialRecord(
            pelada_id=pelada_id,
            description=data['description'],
            amount=amount,
            type=data['type'],
            date=record_date
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'message': 'Registro financeiro adicionado com sucesso',
            'record': record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/peladas/<int:pelada_id>/financial/<int:record_id>', methods=['PUT'])
def update_financial_record(pelada_id, record_id):
    """Atualizar registro financeiro (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    record = FinancialRecord.query.get_or_404(record_id)
    
    if record.pelada_id != pelada_id:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    try:
        data = request.json
        
        # Atualizar campos se fornecidos
        if 'description' in data:
            record.description = data['description']
        
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return jsonify({'error': 'Valor deve ser positivo'}), 400
                record.amount = amount
            except ValueError:
                return jsonify({'error': 'Valor inválido'}), 400
        
        if 'type' in data:
            if data['type'] not in ['income', 'expense']:
                return jsonify({'error': 'Tipo deve ser income ou expense'}), 400
            record.type = data['type']
        
        if 'date' in data:
            try:
                record.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Data inválida'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Registro financeiro atualizado com sucesso',
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/peladas/<int:pelada_id>/financial/<int:record_id>', methods=['DELETE'])
def delete_financial_record(pelada_id, record_id):
    """Excluir registro financeiro (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    record = FinancialRecord.query.get_or_404(record_id)
    
    if record.pelada_id != pelada_id:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    try:
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': 'Registro financeiro excluído com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/peladas/<int:pelada_id>/members/payments', methods=['GET'])
def get_member_payments(pelada_id):
    """Obter status de pagamento dos membros"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é membro da pelada
    if not require_pelada_member(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    members = PeladaMember.query.filter_by(pelada_id=pelada_id, is_approved=True).all()
    
    result = []
    for member in members:
        result.append({
            'member_id': member.id,
            'user_id': member.user_id,
            'user_name': member.user.name,
            'user_position': member.user.position,
            'user_photo_url': member.user.photo_url,
            'monthly_payment_status': member.monthly_payment_status,
            'is_admin': member.is_admin
        })
    
    return jsonify(result), 200

@financial_bp.route('/peladas/<int:pelada_id>/members/<int:member_id>/payment', methods=['PUT'])
def update_member_payment(pelada_id, member_id):
    """Atualizar status de pagamento de um membro (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    member = PeladaMember.query.get_or_404(member_id)
    
    if member.pelada_id != pelada_id:
        return jsonify({'error': 'Membro não encontrado'}), 404
    
    data = request.json
    payment_status = data.get('payment_status')
    
    if payment_status is None:
        return jsonify({'error': 'Status de pagamento é obrigatório'}), 400
    
    member.monthly_payment_status = bool(payment_status)
    db.session.commit()
    
    return jsonify({
        'message': 'Status de pagamento atualizado com sucesso',
        'member': {
            'member_id': member.id,
            'user_name': member.user.name,
            'monthly_payment_status': member.monthly_payment_status
        }
    }), 200

