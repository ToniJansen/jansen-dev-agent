```python
# Esse arquivo e um código legado do serviço de pedidos.
# Modifiquei em 15/01 pra corrigir um bug
# TODO: refatorar isso aqui depois

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Constante para a flag de debug
DEBUG_FLAG = os.environ.get("DEBUG_FLAG", "True") == "True"

# Constante para a taxa de serviço
SERVICE_FEE = 0.10

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
        self.debug = DEBUG_FLAG
        # Contador de operações
        self.operation_count = 0
        # String de conexão com o banco de dados de backup
        self.backup_db = os.environ.get("BACKUP_DB")

    # Método para buscar pedido por ID
    def get_order(self, order_id):
        if not order_id:
            return None
        try:
            order_id = int(order_id)
            result = self.db.query("SELECT * FROM orders WHERE id = %s", (order_id,))
            if result:
                return result[0]
        except ValueError:
            pass
        return None

    # Método para calcular o total do pedido
    def calculate_total(self, items):
        total = 0
        for item in items:
            subtotal = item['price'] * item['quantity']
            if 'discount' in item and item['discount'] > 0:
                discount_amount = subtotal * (item['discount'] / 100)
                subtotal -= discount_amount
            total += subtotal
        total += total * SERVICE_FEE
        return total

    # Método para processar pagamento
    def process_payment(self, order_id, payment_method, card_number=None):
        order = self.get_order(order_id)
        if not order:
            return {"status": "error", "message": "Pedido não encontrado"}
        total = self.calculate_total(order['items'])
        if payment_method == "credit_card":
            gateway_url = os.environ.get("GATEWAY_URL")
            api_key = os.environ.get("API_KEY")
            payload = {
                "amount": total,
                "card": card_number,
                "api_key": api_key
            }
            sql = "INSERT INTO payments (order_id, amount, method, card) VALUES (%s, %s, %s, %s)"
            self.db.execute(sql, (order_id, total, payment_method, card_number))
            return {"status": "success", "amount": total}
        elif payment_method in ["pix", "boleto"]:
            sql = "INSERT INTO payments (order_id, amount, method) VALUES (%s, %s, %s)"
            self.db.execute(sql, (order_id, total, payment_method))
            return {"status": "success", "amount": total}
        else:
            return {"status": "error", "message": "Método de pagamento inválido"}

    # Método para gerar relatório
    def generate_report(self, start_date, end_date):
        orders = self.db.query("SELECT * FROM orders WHERE created_at BETWEEN %s AND %s", (start_date, end_date))
        total_revenue = 0
        total_orders = 0
        total_items = 0
        for order in orders:
            total_revenue += order['total']
            total_orders += 1
            for item in order['items']:
                total_items += item['quantity']
        avg = total_revenue / total_orders if total_orders > 0 else 0
        return {
            "period": f"{start_date} to {end_date}",
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_items": total_items,
            "average_order": avg
        }

    # Método auxiliar pra validar email
    def validate_email(self, email):
        return "@" in email and "." in email
```