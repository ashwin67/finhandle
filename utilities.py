# utilities.py

def get_monthly_spending_by_category(categories, transactions):
    return [
        {
            "category": category.name,
            "amount": sum(transaction.amount for transaction in transactions if transaction.category_id == category.id)
        }
        for category in categories
    ]
