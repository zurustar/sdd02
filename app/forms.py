from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, IntegerField, PasswordField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class ScheduleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=140)])
    start_time = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=140)])
    room = SelectField('Meeting Room', coerce=int, choices=[])
    participants = SelectMultipleField('Share with Team Members', coerce=int, choices=[])
    submit = SubmitField('Save')


class RoomForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')
