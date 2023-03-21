import pandas as pd
from flask_login import current_user
from datetime import datetime

from models.transaction import Transaction
from app import db
import re

def parse_transactions(file, account_type):
    # Read the file using pandas
    df = pd.read_csv(file)

    # Clean and format the data
    # This step depends on the structure of your transaction file
    missed_rows = []
    # Save the parsed transactions to the database
    for index, row in df.iterrows():
        try:
            date_format = "%Y%m%d"
            date_object = datetime.strptime(str(row["transactiondate"]), date_format).date()
            transaction = Transaction(
                date=date_object,
                amount=row["amount"],
                description=extract_name_from_description(row["description"]),
                account=account_type,
                category='Uncategorized'
            )
            # Add the user ID to the transaction
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
        return match.group(1)
    else:
        return ""