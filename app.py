from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
import os
from functools import wraps

# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey123'  # В реальном приложении используйте переменные окружения
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, авторизуйтесь для доступа к этой странице.'

# Модели базы данных
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Team(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    players = db.relationship('Player', backref='team', lazy=True)
    
    def __repr__(self):
        return f"Team('{self.team_name}')"

class Player(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)
    
    def __repr__(self):
        return f"Player('{self.last_name}', '{self.first_name}')"

class Coach(db.Model):
    coach_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    experience_years = db.Column(db.SmallInteger, nullable=False)
    
    def __repr__(self):
        return f"Coach('{self.last_name}', '{self.first_name}')"

class Match(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_date = db.Column(db.DateTime, nullable=False)
    tournament = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"Match('{self.tournament}', '{self.match_date}')"

class Fan(db.Model):
    fan_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Fan('{self.last_name}', '{self.first_name}')"

# Загрузчик пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Декоратор для проверки прав администратора
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Для доступа к этой странице требуются права администратора.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Формы
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован. Пожалуйста, используйте другой.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class TeamForm(FlaskForm):
    team_name = StringField('Название команды', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class PlayerForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()], format='%Y-%m-%d')
    position = StringField('Позиция', validators=[DataRequired()])
    team_id = SelectField('Команда', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить')
    
    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.team_id.choices = [(team.team_id, team.team_name) for team in Team.query.all()]

class CoachForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()], format='%Y-%m-%d')
    experience_years = IntegerField('Опыт работы (лет)', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class MatchForm(FlaskForm):
    match_date = DateField('Дата матча', validators=[DataRequired()], format='%Y-%m-%d')
    tournament = StringField('Турнир', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class FanForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# Маршруты приложения
@app.route('/')
def index():
    teams = Team.query.all()
    players = Player.query.all()
    return render_template('index.html', teams=teams, players=players)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт создан! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Ошибка входа. Пожалуйста, проверьте email и пароль', 'danger')
    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Администраторские маршруты

# Команды
@app.route('/admin/teams')
@login_required
@admin_required
def admin_teams():
    teams = Team.query.all()
    return render_template('admin/teams.html', title='Управление командами', teams=teams)

@app.route('/admin/teams/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(team_name=form.team_name.data)
        db.session.add(team)
        db.session.commit()
        flash('Команда успешно добавлена!', 'success')
        return redirect(url_for('admin_teams'))
    return render_template('admin/team_form.html', title='Добавить команду', form=form, legend='Добавить команду')

@app.route('/admin/teams/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm()
    if form.validate_on_submit():
        team.team_name = form.team_name.data
        db.session.commit()
        flash('Команда успешно обновлена!', 'success')
        return redirect(url_for('admin_teams'))
    elif request.method == 'GET':
        form.team_name.data = team.team_name
    return render_template('admin/team_form.html', title='Редактировать команду', form=form, legend='Редактировать команду')

@app.route('/admin/teams/<int:team_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('Команда успешно удалена!', 'success')
    return redirect(url_for('admin_teams'))

# Игроки
@app.route('/admin/players')
@login_required
@admin_required
def admin_players():
    players = Player.query.all()
    return render_template('admin/players.html', title='Управление игроками', players=players)

@app.route('/admin/players/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_player():
    form = PlayerForm()
    if form.validate_on_submit():
        player = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birth_date=form.birth_date.data,
            position=form.position.data,
            team_id=form.team_id.data
        )
        db.session.add(player)
        db.session.commit()
        flash('Игрок успешно добавлен!', 'success')
        return redirect(url_for('admin_players'))
    return render_template('admin/player_form.html', title='Добавить игрока', form=form, legend='Добавить игрока')

@app.route('/admin/players/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    form = PlayerForm()
    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.birth_date = form.birth_date.data
        player.position = form.position.data
        player.team_id = form.team_id.data
        db.session.commit()
        flash('Игрок успешно обновлен!', 'success')
        return redirect(url_for('admin_players'))
    elif request.method == 'GET':
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
        form.birth_date.data = player.birth_date
        form.position.data = player.position
        form.team_id.data = player.team_id
    return render_template('admin/player_form.html', title='Редактировать игрока', form=form, legend='Редактировать игрока')

@app.route('/admin/players/<int:player_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    flash('Игрок успешно удален!', 'success')
    return redirect(url_for('admin_players'))

# Тренеры
@app.route('/admin/coaches')
@login_required
@admin_required
def admin_coaches():
    coaches = Coach.query.all()
    return render_template('admin/coaches.html', title='Управление тренерами', coaches=coaches)

@app.route('/admin/coaches/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_coach():
    form = CoachForm()
    if form.validate_on_submit():
        coach = Coach(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birth_date=form.birth_date.data,
            experience_years=form.experience_years.data
        )
        db.session.add(coach)
        db.session.commit()
        flash('Тренер успешно добавлен!', 'success')
        return redirect(url_for('admin_coaches'))
    return render_template('admin/coach_form.html', title='Добавить тренера', form=form, legend='Добавить тренера')

@app.route('/admin/coaches/<int:coach_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_coach(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    form = CoachForm()
    if form.validate_on_submit():
        coach.first_name = form.first_name.data
        coach.last_name = form.last_name.data
        coach.birth_date = form.birth_date.data
        coach.experience_years = form.experience_years.data
        db.session.commit()
        flash('Тренер успешно обновлен!', 'success')
        return redirect(url_for('admin_coaches'))
    elif request.method == 'GET':
        form.first_name.data = coach.first_name
        form.last_name.data = coach.last_name
        form.birth_date.data = coach.birth_date
        form.experience_years.data = coach.experience_years
    return render_template('admin/coach_form.html', title='Редактировать тренера', form=form, legend='Редактировать тренера')

@app.route('/admin/coaches/<int:coach_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_coach(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    db.session.delete(coach)
    db.session.commit()
    flash('Тренер успешно удален!', 'success')
    return redirect(url_for('admin_coaches'))

# Матчи
@app.route('/admin/matches')
@login_required
@admin_required
def admin_matches():
    matches = Match.query.all()
    return render_template('admin/matches.html', title='Управление матчами', matches=matches)

@app.route('/admin/matches/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_match():
    form = MatchForm()
    if form.validate_on_submit():
        match = Match(
            match_date=form.match_date.data,
            tournament=form.tournament.data
        )
        db.session.add(match)
        db.session.commit()
        flash('Матч успешно добавлен!', 'success')
        return redirect(url_for('admin_matches'))
    return render_template('admin/match_form.html', title='Добавить матч', form=form, legend='Добавить матч')

@app.route('/admin/matches/<int:match_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    form = MatchForm()
    if form.validate_on_submit():
        match.match_date = form.match_date.data
        match.tournament = form.tournament.data
        db.session.commit()
        flash('Матч успешно обновлен!', 'success')
        return redirect(url_for('admin_matches'))
    elif request.method == 'GET':
        form.match_date.data = match.match_date
        form.tournament.data = match.tournament
    return render_template('admin/match_form.html', title='Редактировать матч', form=form, legend='Редактировать матч')

@app.route('/admin/matches/<int:match_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    flash('Матч успешно удален!', 'success')
    return redirect(url_for('admin_matches'))

# Болельщики
@app.route('/admin/fans')
@login_required
@admin_required
def admin_fans():
    fans = Fan.query.all()
    return render_template('admin/fans.html', title='Управление болельщиками', fans=fans)

@app.route('/admin/fans/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_fan():
    form = FanForm()
    if form.validate_on_submit():
        fan = Fan(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            registration_date=datetime.utcnow()
        )
        db.session.add(fan)
        db.session.commit()
        flash('Болельщик успешно добавлен!', 'success')
        return redirect(url_for('admin_fans'))
    return render_template('admin/fan_form.html', title='Добавить болельщика', form=form, legend='Добавить болельщика')

@app.route('/admin/fans/<int:fan_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_fan(fan_id):
    fan = Fan.query.get_or_404(fan_id)
    form = FanForm()
    if form.validate_on_submit():
        fan.first_name = form.first_name.data
        fan.last_name = form.last_name.data
        fan.email = form.email.data
        fan.phone = form.phone.data
        db.session.commit()
        flash('Болельщик успешно обновлен!', 'success')
        return redirect(url_for('admin_fans'))
    elif request.method == 'GET':
        form.first_name.data = fan.first_name
        form.last_name.data = fan.last_name
        form.email.data = fan.email
        form.phone.data = fan.phone
    return render_template('admin/fan_form.html', title='Редактировать болельщика', form=form, legend='Редактировать болельщика')

@app.route('/admin/fans/<int:fan_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_fan(fan_id):
    fan = Fan.query.get_or_404(fan_id)
    db.session.delete(fan)
    db.session.commit()
    flash('Болельщик успешно удален!', 'success')
    return redirect(url_for('admin_fans'))

# Маршруты для обычных пользователей для просмотра данных
@app.route('/teams')
def teams():
    teams = Team.query.all()
    return render_template('teams.html', title='Команды', teams=teams)

@app.route('/players')
def players():
    players = Player.query.all()
    return render_template('players.html', title='Игроки', players=players)

@app.route('/coaches')
def coaches():
    coaches = Coach.query.all()
    return render_template('coaches.html', title='Тренеры', coaches=coaches)

@app.route('/matches')
def matches():
    matches = Match.query.all()
    return render_template('matches.html', title='Матчи', matches=matches)

@app.route('/fans')
def fans():
    fans = Fan.query.all()
    return render_template('fans.html', title='Болельщики', fans=fans)

# Создание первого администратора при запуске
@app.before_first_request
def create_admin():
    db.create_all()
    admin_exists = User.query.filter_by(email='admin@example.com').first()
    if not admin_exists:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', email='admin@example.com', password=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)