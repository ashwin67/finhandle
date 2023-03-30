import pandas as pd
from flask_login import current_user
from datetime import datetime

from models.transaction import Transaction
from models.parameters import Account
from app import db
import re

def parse_transactions(file, account_id, custom_mapping=None):
    df = pd.read_csv(file)
    account = Account.query.get(account_id)
    missed_rows = []

    date_col = custom_mapping['date'] if custom_mapping else 'Date'
    description_col = custom_mapping['description'] if custom_mapping else 'Description'
    amount_col = custom_mapping['amount'] if custom_mapping else 'Amount'

    for index, row in df.iterrows():
        try:
            date_format = "%Y%m%d"
            date_object = datetime.strptime(str(row[date_col]), date_format).date()
            transaction = Transaction(
                date=date_object,
                amount=row[amount_col],
                description=extract_name_from_description(row[description_col]),
                account=account,
                category=None
            )
            transaction.user_id = current_user.id
            db.session.add(transaction)
        except Exception as e:
            missed_rows.append(index)
            print("Error parsing row {}: {}".format(index, e))
    db.session.commit()



def extract_name_from_description(description):
    name_pattern = re.compile(r"/NAME/(.*?)/")
    match = name_pattern.search(description)
    if match:
        name = match.group(1)
    else:
        # Use the description as the name when the /NAME/ pattern is not found
        name = description

    # Remove long numbers and any words in all caps that accompany them
    name = re.sub(r'(\b[A-Z]+\b\s*)?\d{5,}(\s*\b[A-Z]+\b)?', '', name)

    # Remove date or time-like strings
    name = re.sub(r'\b\d{1,4}[-/:.]\d{1,2}[-/:.]\d{1,4}\b', '', name)
    name = re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\b', '', name)

    # Replace multiple spaces with a single space
    name = re.sub(r'\s{2,}', ' ', name)

    return name.strip()


