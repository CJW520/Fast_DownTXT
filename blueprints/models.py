# CJW
# models.py
# 时间：2025-04-24 20:50

from tortoise import Model, fields


class User(Model):
    __tablename__ = 'users'
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, unique=True, null=False)
    password = fields.CharField(max_length=100, null=False)
    email = fields.CharField(max_length=100, unique=True, null=False)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'email': self.email
        }
