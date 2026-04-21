import marshmallow as ma
import uuid
from sqlalchemy.dialects.postgresql import UUID
from db import db

class AppUsers(db.Model):
    __tablename__ = 'AppUsers'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    role = db.Column(db.String(), nullable=False, default='user')

    auth = db.relationship('AuthTokens', back_populates='user')

    def __init__(self, first_name, last_name, email, password, active=True, role='user'):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.active = active
        self.role = role

    def new_user_obj():
        return AppUsers('', '', '', '', True, 'user')
    
class AppUsersSchema(ma.Schema):
    class Meta:
        fields = ['user_id', 'first_name', 'last_name', 'email', 'active','role' ]
    
    user_id = ma.fields.UUID()
    first_name = ma.fields.String(required=True)
    last_name = ma.fields.String(required=True)
    email = ma.fields.String(required=True)
    active = ma.fields.Boolean(required=True, dump_default=True)
    role = ma.fields.String(required=True, dump_default='user')


app_user_schema = AppUsersSchema()
app_users_schema = AppUsersSchema(many=True)