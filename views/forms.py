from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired
from models.parameters import Account, Category


class TransactionUploadForm(FlaskForm):
    file = FileField("Upload Transactions", validators=[DataRequired()])
    account = SelectField('Account', validators=[DataRequired()], coerce=int)
    submit = SubmitField("Import")

    def __init__(self, *args, **kwargs):
        super(TransactionUploadForm, self).__init__(*args, **kwargs)
        self.account.choices = [(param.id, param.name) for param in Account.query.filter_by(type='account').all()]

class AddAccountForm(FlaskForm):
    account_name = StringField("Account Name", validators=[DataRequired()])
    submit = SubmitField("Add Account")

class AddCategoryForm(FlaskForm):
    category_name = StringField("Category Name", validators=[DataRequired()])
    submit = SubmitField("Add Category")
