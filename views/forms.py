from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired
from models.parameters import Account, Category
from wtforms import HiddenField


class TransactionUploadForm(FlaskForm):
    csrf_token = HiddenField(id='transaction_upload_csrf_token')
    file = FileField("Upload Transactions", validators=[DataRequired()])
    account = SelectField('Account', validators=[DataRequired()], coerce=int, id='transaction_upload_account')
    submit = SubmitField("Import", id='transaction_upload_submit')

    def __init__(self, *args, **kwargs):
        super(TransactionUploadForm, self).__init__(*args, **kwargs)
        self.account.choices = [(param.id, param.name) for param in Account.query.filter_by(type='account').all()]

class AddAccountForm(FlaskForm):
    csrf_token = HiddenField(id='add_account_csrf_token')
    account_name = StringField("Account Name", validators=[DataRequired()], id='add_account_name')
    submit = SubmitField("Add Account", id='add_account_submit')

class AddCategoryForm(FlaskForm):
    csrf_token = HiddenField(id='add_category_csrf_token')
    category_name = StringField("Category Name", validators=[DataRequired()], id='add_category_name')
    submit = SubmitField("Add Category", id='add_category_submit')
