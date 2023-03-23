from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired
from models.parameter import Parameter


class TransactionUploadForm(FlaskForm):
    file = FileField("Upload Transactions", validators=[DataRequired()])
    account = SelectField('Account', validators=[DataRequired()], coerce=int)
    submit = SubmitField("Import")

    def __init__(self, *args, **kwargs):
        super(TransactionUploadForm, self).__init__(*args, **kwargs)
        self.account.choices = [(param.id, param.name) for param in Parameter.query.filter_by(type='account').all()]

class AddAccountForm(FlaskForm):
    account_name = StringField("Account Name", validators=[DataRequired()])
    submit = SubmitField("Add Account")
