from marshmallow import Schema, fields, validate


class AccountUpdateSchema(Schema):
    email = fields.Email(required=False)
    Avatar = fields.Str(required=False)

class UpdateConfigSchema(Schema):
    target_language = fields.Str(required=False)