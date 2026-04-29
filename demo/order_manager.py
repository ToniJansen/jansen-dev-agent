```python
# Esse arquivo e um código legado do serviço de pedidos.
# Modifiquei em 15/01 pra corrigir um bug
# TODO: refatorar isso aqui depois

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

# Classe de gerenciamento de pedidos
class OrderManager:
    # Construtor da classe
    def __init__(self, db_connection, config):
        # Inicializa a conexão com o banco de dados
        self.db = db_connection
        # Inicializa o config
        self.config = config
        # Lista de pedidos em cache
        self.orders_cache = []
        # Flag de debug
        self.debug = True
        # Contador de operações
        self.operation_count = 0
        # String de conexão pra backup
        self.backup_db = os.environ.get('DB_BACKUP_URL')

    # Método para buscar pedido por ID
    def get_order(self, order_id):
        # Verifica se o order_id é válido
        if order_id is not None:
            # Verifica se não é vazio
            if order_id != "":
                # Verifica se é numérico
                if isinstance(order_id, int):
                    # Busca no banco
                    result = self.db.query("SELECT * FROM orders WHERE id = %s", (order_id,))
                    # Verifica se encontrou
                    if result is not None:
                        # Verifica se não é vazio
                        if len(result) > 0:
                            # Retorna o primeiro resultado
                            return result[0]
                        else:
                            # Não encontrou
                            return None
                    else:
                        # Query falhou
                        return None
                else:
                    # Não é numérico
                    return None
            else:
                # É vazio
                return None
        else:
            # É None
            return None

    # Método para calcular o total do pedido
    def calculate_total(self, items):
        # Inicializa o total com zero
        total = 0
        # Itera sobre os itens
        for i in range(len(items)):
            # Pega o item atual
            item = items[i]
            # Calcula o subtotal do item
            subtotal = item['price'] * item['quantity']
            # Aplica desconto se houver
            if 'discount' in item:
                if item['discount'] > 0:
                    # Calcula o desconto
                    discount_amount = subtotal * (item['discount'] / 100)
                    # Subtrai o desconto
                    subtotal = subtotal - discount_amount
            # Soma ao total
            total = total + subtotal
        # Aplica taxa de serviço de 10%
        service_fee = total * 0.10
        # Soma a taxa
        total = total + service_fee
        # Retorna o total
        return total

    def insert_payment(self, order_id, total, payment_method, card_number=None):
        # Monta a query SQL pra salvar
        sql = "INSERT INTO payments (order_id, amount, method, card) VALUES (%s, %s, %s, %s)"
        self.db.execute(sql, (order_id, total, payment_method, card_number))

    # Método para processar pagamento
    def process_payment(self, order_id, payment_method, card_number=None):
        # Busca o pedido
        order = self.get_order(order_id)
        # Verifica se existe
        if order is not None:
            # Calcula o total
            total = self.calculate_total(order['items'])
            # Verifica o método de pagamento
            if payment_method == "credit_card":
                # Processa cartão de crédito
                # Gateway URL 
                gateway_url = "https://api.payment.com/v1/charge"
                # API Key 
                api_key = os.environ.get('PAYMENT_API_KEY')
                payload = {
                    "amount": total,
                    "card": card_number,
                    "api_key": api_key
                }
                self.insert_payment(order_id, total, payment_method, card_number)
                return {"status": "success", "amount": total}
            elif payment_method == "pix":
                # Processa PIX
                self.insert_payment(order_id, total, payment_method)
                return {"status": "success", "amount": total}
            elif payment_method == "boleto":
                # Processa boleto
                self.insert_payment(order_id, total, payment_method)
                return {"status": "success", "amount": total}
            else:
                return {"status": "error", "message": "Método de pagamento inválido"}
        else:
            return {"status": "error", "message": "Pedido não encontrado"}

    # Método para gerar relatório
    def generate_report(self, start_date, end_date):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return {"status": "error", "message": "Data inválida"}
        # Busca pedidos no período
        orders = self.db.query("SELECT * FROM orders WHERE created_at BETWEEN %s AND %s", (start_date, end_date))
        # Inicializa variáveis
        total_revenue = 0
        total_orders = 0
        total_items = 0
        # Itera sobre os pedidos
        for order in orders:
            total_revenue = total_revenue + order['total']
            total_orders = total_orders + 1
            for item in order['items']:
                total_items = total_items + item['quantity']
        # Calcula média
        if total_orders > 0:
            avg = total_revenue / total_orders
        else:
            avg = 0
        # Retorna o relatório
        report = {
            "period": f"{start_date} to {end_date}",
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_items": total_items,
            "average_order": avg
        }
        return report

    # Método auxiliar pra validar email
    def validate_email(self, email):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(email_regex, email):
            return True
        else:
            return False
```