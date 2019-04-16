# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 20)])
    submit = SubmitField('Login in')


class SendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField()


class NodeDeleteForm(FlaskForm):
    node = StringField('Node')
    mac_addr = StringField('Mac_Addr')
    submit = SubmitField()