from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class TransactionUploadForm(FlaskForm):
    file = FileField("Upload Transactions", validators=[DataRequired()])
    submit = SubmitField("Import")