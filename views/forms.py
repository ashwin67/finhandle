from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired
from models.parameters import Account, Category
from wtforms import HiddenField
from wtforms.validators import Optional
from flask_login import current_user


class TransactionUploadForm(FlaskForm):
    csrf_token = HiddenField(id='transaction_upload_csrf_token')
    file = FileField("Upload Transactions", validators=[DataRequired()])
    account = SelectField('Account', validators=[DataRequired()], coerce=int, id='transaction_upload_account')
    mapping_key = SelectField('Custom Mapping', validators=[Optional()])
    submit = SubmitField("Import", id='transaction_upload_submit')

    def __init__(self, *args, **kwargs):
        super(TransactionUploadForm, self).__init__(*args, **kwargs)
        self.account.choices = [(param.id, param.name) for param in Account.query.filter_by(type='account').all()]
        mappings = current_user.custom_mappings or []
        self.mapping_key.choices = [(i, mapping['mapping_name']) for i, mapping in enumerate(mappings)] + [('default', 'Default')]

class AddAccountForm(FlaskForm):
    csrf_token = HiddenField(id='add_account_csrf_token')
    account_name = StringField("Account Name", validators=[DataRequired()], id='add_account_name')
    submit = SubmitField("Add Account", id='add_account_submit')

class AddCategoryForm(FlaskForm):
    csrf_token = HiddenField(id='add_category_csrf_token')
    category_name = StringField("Category Name", validators=[DataRequired()], id='add_category_name')
    submit = SubmitField("Add Category", id='add_category_submit')

class CustomMappingForm(FlaskForm):
    csrf_token = HiddenField(id='add_custom_mapping_csrf_token')
    mapping_name = StringField('Mapping Name', validators=[DataRequired()])
    date = StringField('Date Column Name', validators=[DataRequired()])
    description = StringField('Description Column Name', validators=[DataRequired()])
    amount = StringField('Amount Column Name', validators=[DataRequired()])
    submit = SubmitField('Save')
