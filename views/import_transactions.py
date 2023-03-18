from ..models.transaction import Transaction
import pandas as pd
from ..app import db

def parse_transactions(file):
    # Read the file using pandas
    df = pd.read_csv(file)

    # Clean and format the data
    # This step depends on the structure of your transaction file

    # Save the parsed transactions to the database
    for index, row in df.iterrows():
        transaction = Transaction(
            date=row["date"],
            description=row["description"],
            amount=row["amount"],
            category=row["category"]
        )
        # Add the user ID to the transaction
        transaction.user_id = user_id

        db.session.add(transaction)
    db.session.commit()

