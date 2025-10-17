from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    Field,
    PasswordField,
    StringField,
    SubmitField,
    validators,
)


class LoginForm(FlaskForm):
    email = EmailField("Email", [validators.Email(), validators.InputRequired()])
    password = PasswordField("Password", [validators.InputRequired()])
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    email = EmailField(
        "Email",
        [validators.Email(), validators.InputRequired(), validators.Length(max=20)],
    )
    password = PasswordField(
        "Password", [validators.InputRequired(), validators.Length(8, 20)]
    )
    username = StringField(
        "Username", [validators.Length(5, 10), validators.InputRequired()]
    )
    submit = SubmitField("Sign up")


class BackupCreationForm(FlaskForm):
    url = Field(
        "url",
        [
            validators.Regexp(
                r"^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
            ),
            validators.InputRequired(),
        ],
    )
    submit = SubmitField("Create!")
