import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, IntegerField, TimeField
from wtforms.validators import DataRequired, Email, NumberRange
from helpers import login_required
from flask_mysqldb import MySQL



app = Flask(__name__)

#secret key
app.secret_key = "FelipeWai0132?"


#database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'foxcampdb'

mysql = MySQL(app)

#Create a form Class
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")

class RegisterForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    sobrenome = StringField("Sobrenome", validators=[DataRequired()])
    usuario = StringField("Usuário", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    idade = IntegerField("Idade", validators=[DataRequired(), NumberRange(min=1, max=60)])
    senha = PasswordField("Senha", validators=[DataRequired()])
    confirmar_senha = PasswordField("Confirmar Senha", validators=[DataRequired()])
    submit = SubmitField("Registrar")

class criaretapaForm(FlaskForm):
    local = StringField("Usuário", validators=[DataRequired()])
    dia = IntegerField("Dia", validators=[DataRequired(), NumberRange(min=1, max=31)])
    mes = IntegerField("Mes", validators=[DataRequired(), NumberRange(min=1, max=12)])
    ano = IntegerField("Ano", validators=[DataRequired()])
    horario = TimeField("Horário", validators=[DataRequired()])
    submit = SubmitField("Criar etapa")

class JogadoresForm(FlaskForm):
    nome = StringField("Nome do jogador", validators=[DataRequired()])
    submit = SubmitField("Procurar")

@app.route("/teste")
def teste():
    cursor = mysql.connection.cursor()
    check = cursor.execute("SELECT id_etapa FROM times_etapas WHERE id_etapa = 7")
    check2 = cursor.fetchone()
    return render_template("teste.html", id = check2)


@app.route("/")
def index():
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()
        return render_template("index.html", username = get_nome2[0], user = user)
    return render_template("index.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
    nome = None
    sobrenome = None
    usuario = None
    email = None
    idade = None
    senha = None
    confirmar_senha = None
    genero = 'Masculino'
    form = RegisterForm()
    if request.method == 'GET':
        return render_template("register.html", 
                nome = nome,
                sobrenome = sobrenome,
                usuario = usuario,
                email = email,
                idade = idade,
                senha = senha,
                confirmar_senha = confirmar_senha,
                form = form)
    if form.validate_on_submit():
        nome = form.nome.data.upper()
        sobrenome = form.sobrenome.data.upper()
        usuario = form.usuario.data
        email = form.email.data.upper()
        idade = form.idade.data
        senha = form.senha.data
        confirmar_senha = form.confirmar_senha.data
        cursor = mysql.connection.cursor()
        already_email = cursor.execute("SELECT email FROM jogadores WHERE email = %s", [email])
        already_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE usuario = %s", [usuario])
        if already_usuario != 0:
            flash("Nome de Usuário já está em uso!", category="info")
            return redirect("/register")
        if already_email != 0:
            flash("Email já utilizado!", category="info")
            return redirect("/register")
        if senha != confirmar_senha:
            flash("Senhas não coincidem!", category="info")
            return redirect("/register")
        password_hash = generate_password_hash(senha)
        add_to_database = cursor.execute("""INSERT INTO jogadores (nome, sobrenome, usuario, email, genero, idade, senha) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                                        (nome, sobrenome, usuario, email, genero, idade, password_hash))
        mysql.connection.commit()
        cursor.close()
        return redirect("/login")
    return redirect("/")



@app.route("/login", methods=['POST', 'GET'])
def login():
    email = None
    senha = None
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data.upper()
            senha = form.senha.data
            cursor = mysql.connection.cursor()
            check_user = cursor.execute(""" SELECT * FROM jogadores WHERE email = %s """, [email])
            get_user_password = cursor.execute(""" SELECT senha FROM jogadores WHERE email =  %s """, [email])
            get_user_password2 = cursor.fetchone()

            if check_user != 1 or not check_password_hash(get_user_password2[0], senha):
                flash("Email ou senha inválidos!", category = "info")
                return redirect("/login")
            
            get_user_id = cursor.execute(f""" SELECT id FROM jogadores WHERE email LIKE '%{email}%' """)
            get_user_id2 = cursor.fetchone()
            
            session["user_id"] = get_user_id2[0]
            
            return redirect("/")
        
        flash("Usuário não encontrado!", category = "info")
        return redirect("/login")

    
    return render_template("login.html", 
                        form=form,
                        email = email,
                        senha = senha)



@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")



@app.route("/jogadores", methods=['POST', 'GET'])
def jogadores():
    nome = None
    form = JogadoresForm()
    if request.method == 'POST':
        if "user_id" in session:
            user = session["user_id"]
            cursor = mysql.connection.cursor()
            get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
            get_nome2 = cursor.fetchone()
            nome = form.nome.data
            get_jogadores = cursor.execute(f""" SELECT * FROM jogadores WHERE nome LIKE '%{nome}%' """)
            get_jogadores2 = cursor.fetchall()
            return render_template("jogadores_query.html",
                                user = user,
                                username = get_nome2[0],
                                jogador = nome,
                                jogadores = get_jogadores2)
        

        nome = form.nome.data
        cursor = mysql.connection.cursor() 
        get_jogadores = cursor.execute(f""" SELECT * FROM jogadores WHERE nome LIKE '%{nome}%' """)
        get_jogadores2 = cursor.fetchall()
        return render_template("jogadores_query.html", 
                                jogador = nome,
                                jogadores = get_jogadores2)

    if "user_id" in session:
            user = session["user_id"]
            cursor = mysql.connection.cursor()
            get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
            get_nome2 = cursor.fetchone()
            return render_template("jogadores.html",
                                user = user,
                                username = get_nome2[0],
                                form = form,
                                nome = nome)
    
    
    return render_template("jogadores.html",
                                form = form,
                                nome = nome)


@app.route("/alljogadores")
def alljogadores():
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()
        get_jogadores = cursor.execute(f""" SELECT * FROM jogadores """)
        get_jogadores2 = cursor.fetchall()
        return render_template("jogadores_all.html",
                                user = user,
                                username = get_nome2[0],
                                jogadores = get_jogadores2)
        

    cursor = mysql.connection.cursor()
    get_jogadores = cursor.execute(f""" SELECT * FROM jogadores""")
    get_jogadores2 = cursor.fetchall()
    return render_template("jogadores_all.html", 
                                jogadores = get_jogadores2)


@app.route("/times")
def times():
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()
        get_times = cursor.execute(""" SELECT * FROM times """)
        get_times2 = cursor.fetchall()
        return render_template("times.html", 
                            username = get_nome2[0], 
                            user = user,
                            times = get_times2)
    
    cursor = mysql.connection.cursor()
    get_times = cursor.execute(""" SELECT * FROM times """)
    get_times2 = cursor.fetchall()
    return render_template("times.html", 
                        times = get_times2)


@app.route("/criartime", methods=['POST', 'GET'])
@login_required
def criartime():
    if request.method == 'GET':     
        return render_template("criartime.html")
    user = session["user_id"]
    nome = request.form.get("nome")
    categoria = request.form.get("select-categoria")
    genero = request.form.get("select-genero")
    cursor = mysql.connection.cursor()
    add_to_database = cursor.execute(""" INSERT INTO times (nome, genero, categoria, id_criador) VALUES (%s, %s, %s, %s)""", (nome, genero, categoria, user))
    mysql.connection.commit()
    cursor.close()
    return redirect("/")


@app.route("/jogadores/<jogador>")
def jogador(jogador):
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()
        
        get_jogador = cursor.execute(f""" SELECT * FROM jogadores WHERE email = (SELECT email FROM jogadores WHERE usuario LIKE '%{jogador}%') """)
        jogador_infos = cursor.fetchall()

        get_id_jogador = cursor.execute(f""" SELECT id FROM jogadores WHERE usuario LIKE '%{jogador}%' """)
        get_id_jogador2 = cursor.fetchone()

        get_infos = cursor.execute(f" SELECT * FROM infos_jogadores WHERE id_jogador = (SELECT id FROM jogadores WHERE usuario LIKE '%{jogador}%') ")
        get_infos2 = cursor.fetchall()

        if user == get_id_jogador2[0]:
            same = True
        else:
            same = False

        get_time = cursor.execute(f"""SELECT * FROM times WHERE nome LIKE (SELECT time FROM jogadores WHERE id = (SELECT id FROM jogadores WHERE usuario LIKE '{jogador}'))""")
        get_time2 = cursor.fetchall()
        
        if get_time == 0:
            semtime = True
        else:
            semtime = False

        if jogador == 'Admin' and user != 1:
            flash("Ação não permitida!", category="info")
            return redirect("/")

        return render_template("jogador.html", username = get_nome2[0], 
                            user = user, 
                            jogador=jogador, 
                            jogadores = jogador_infos,
                            same = same,
                            infos = get_infos2,
                            time = get_time2,
                            semtime = semtime)
    
    
    
    cursor = mysql.connection.cursor()
    get_jogador = cursor.execute(f""" SELECT * FROM jogadores WHERE email = (SELECT email FROM jogadores WHERE usuario LIKE '%{jogador}%') """)
    jogador_infos = cursor.fetchall()
    get_time = cursor.execute(f"""SELECT * FROM times WHERE nome LIKE (SELECT time FROM jogadores WHERE id = (SELECT id FROM jogadores WHERE usuario LIKE '{jogador}'))""")
    get_time2 = cursor.fetchall()
        
    if get_time == 0:
        semtime = True
    else:
        semtime = False

    return render_template("jogador.html", jogador=jogador, jogadores = jogador_infos, time = get_time2, semtime = semtime)


@app.route("/times/<time>")
def time(time):
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        
        #pegar nome para colocar no nav 
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()
        
        #Pegar informações do time
        get_time = cursor.execute(""" SELECT * FROM times WHERE nome = %s """, [time])
        get_time2 = cursor.fetchall()
        
        #Pegar jogadores que estão no time 
        get_jogadores = cursor.execute(""" SELECT * FROM jogadores WHERE time LIKE %s """, [time])
        get_jogadores2 = cursor.fetchall()
        
        #verificar se a pessoa logada é o dono do time
        get_id_time = cursor.execute(""" SELECT id_criador FROM times WHERE nome LIKE %s """, [time])
        get_id_time2 = cursor.fetchone()
        if user == get_id_time2[0]:
            same = True
        else:
            same = False

        
        return render_template("time.html", 
                            username = get_nome2[0], 
                            user = user, 
                            time = get_time2, 
                            jogadores=get_jogadores2, 
                            same=same)
    

    cursor = mysql.connection.cursor()
    get_time = cursor.execute(""" SELECT * FROM times WHERE nome = %s """, [time])
    get_time2 = cursor.fetchall()
    get_jogadores = cursor.execute(""" SELECT * FROM jogadores WHERE time LIKE %s """, [time])
    get_jogadores2 = cursor.fetchall()
    return render_template("time.html", time = get_time2, jogadores=get_jogadores2)

    
@app.route("/excluirjogador/<jogador>")
@login_required
def excluirjogador(jogador):
    cursor = mysql.connection.cursor()
    get_time = cursor.execute("SELECT time FROM jogadores WHERE usuario LIKE %s", [jogador])
    get_time2 = cursor.fetchone()
    delete_team = cursor.execute(""" UPDATE jogadores SET time = NULL WHERE usuario LIKE %s """, [jogador])
    mysql.connection.commit()
    cursor.close()
    return redirect(f"/times/{get_time2[0]}")


@app.route("/adicionarjogador/<time>", methods=['POST', 'GET'])
@login_required
def adicionarjogador(time):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        #ver quantos jogadores estão no time
        get_qtd_jogadores = cursor.execute(" SELECT * FROM jogadores WHERE time LIKE %s", [time])
        if get_qtd_jogadores == 6:
            flash("Este time já possui 6 jogadores")
            return redirect(f"/times/{time}")

        get_all_jogadores = cursor.execute(" SELECT usuario FROM jogadores ")
        get_all_jogadores2 = cursor.fetchall()

        return render_template("adicionarjogador.html",
                             jogadores = get_all_jogadores2)
    cursor = mysql.connection.cursor()
    #ver quantos jogadores estão no time
    get_qtd_jogadores = cursor.execute(" SELECT * FROM jogadores WHERE time LIKE %s", [time])
    jogador = request.form.get("add-jogador")
    
    #check if jogador has a team
    check_time = cursor.execute(" SELECT time FROM jogadores WHERE usuario LIKE %s ", [jogador])
    check_time2 = cursor.fetchone()
    
    get_cat_time = cursor.execute(" SELECT categoria FROM times ")
    get_cat_time2 = cursor.fetchone()
    
    check_age = cursor.execute(" SELECT idade FROM jogadores WHERE usuario LIKE %s ", [jogador])
    check_age2 = cursor.fetchone()
    if check_time2[0] != None:
        flash("Este jogador já tem um time!")
        return redirect(f"/adicionarjogador/{time}")
    
    if get_cat_time2[0] == 'U23' and check_age2[0] > 23:
            flash("A idade do jogador não coincide com a categoria do time")
            return redirect(f"/adicionarjogador/{time}")
    
    elif get_cat_time2[0] == 'U18' and check_age2[0] > 18:
            flash("A idade do jogador não coincide com a categoria do time")
            return redirect(f"/adicionarjogador/{time}")
    
        
    add_to_team = cursor.execute(""" UPDATE jogadores SET time = %s WHERE usuario LIKE %s """, (time, jogador))
    mysql.connection.commit()
    return redirect(f"/times/{time}")


@app.route("/editarperfil/<jogador>", methods=['POST', 'GET'])
@login_required
def editarperfil(jogador):
    user = session["user_id"]
    cursor = mysql.connection.cursor()
    get_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE id = %s", [user])
    get_usuario2 = cursor.fetchone()
    if jogador != get_usuario2[0]:
        flash("Essa ação não é permitida!", category='info')
        return redirect("/")
    get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
    get_nome2 = cursor.fetchone()
        
    get_jogador = cursor.execute(f""" SELECT * FROM jogadores WHERE email = (SELECT email FROM jogadores WHERE usuario LIKE '%{jogador}%') """)
    jogador_infos = cursor.fetchall()

    get_id_jogador = cursor.execute(f""" SELECT id FROM jogadores WHERE usuario LIKE '%{jogador}%' """)
    get_id_jogador2 = cursor.fetchone()

    get_infos = cursor.execute(f" SELECT * FROM infos_jogadores WHERE id_jogador = (SELECT id FROM jogadores WHERE usuario LIKE '%{jogador}%') ")
    get_infos2 = cursor.fetchall()

    if get_infos == 0:
        nulo = True
    else:
        nulo = False


    return render_template("editarperfil.html", username = get_nome2[0], 
                            user = user, 
                            jogador=jogador, 
                            jogadores = jogador_infos,
                            infos = get_infos2,
                            nulo = nulo)



@app.route("/editar/usuario/<jogador>", methods=['POST', 'GET'])
@login_required
def editarusuario(jogador):
    if request.method == 'GET':
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE id = %s", [user])
        get_usuario2 = cursor.fetchone()
        if jogador != get_usuario2[0]:
            flash("Essa ação não é permitida!", category='info')
            return redirect("/")
        return render_template("editarusuario.html", jogador = jogador)
    
    cursor = mysql.connection.cursor()
    usuario = request.form.get("usuario")
    search_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE usuario = %s", [usuario])
    if search_usuario != 0:
        flash("Nome de usuário já em uso!", category="info")
        return redirect(f"/jogadores/{jogador}")
    mudar_usuario = cursor.execute("UPDATE jogadores SET usuario = %s WHERE usuario = %s", (usuario, jogador))
    mysql.connection.commit()
    cursor.close()
    return redirect(f"/jogadores/{usuario}")

@app.route("/editar/idade/<jogador>", methods=['POST', 'GET'])
@login_required
def editaridade(jogador):
    if request.method == 'GET':
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE id = %s", [user])
        get_usuario2 = cursor.fetchone()
        if jogador != get_usuario2[0]:
            flash("Essa ação não é permitida!", category='info')
            return redirect("/")
        return render_template("editaridade.html", jogador = jogador)
    
    cursor = mysql.connection.cursor()
    idade = request.form.get("idade")
    mudar_idade = cursor.execute("UPDATE jogadores SET idade = %s WHERE usuario = %s", (idade, jogador))
    mysql.connection.commit()
    cursor.close()
    return redirect(f"/jogadores/{jogador}")



@app.route("/editar/altura/<jogador>", methods=['POST', 'GET'])
def editaraltura(jogador):
    if request.method == 'GET':
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE id = %s", [user])
        get_usuario2 = cursor.fetchone()
        if jogador != get_usuario2[0]:
            flash("Essa ação não é permitida!", category='info')
            return redirect("/")
        return render_template("editaraltura.html", jogador = jogador)
    
    user = session["user_id"]
    cursor = mysql.connection.cursor()
    altura = request.form.get("altura")
    search_id_db = cursor.execute("SELECT id_jogador FROM infos_jogadores WHERE id_jogador = %s", [user])
    if search_id_db == 0:
        insert_into_db = cursor.execute("INSERT INTO infos_jogadores (id_jogador, altura) VALUES (%s, %s)", (user, altura))
        mysql.connection.commit()
    else:
        update_altura = cursor.execute("UPDATE infos_jogadores SET altura = %s WHERE id_jogador = %s", (altura, user))
        mysql.connection.commit()
        cursor.close()
    return redirect(f"/jogadores/{jogador}")



@app.route("/editar/peso/<jogador>", methods=['POST', 'GET'])
def editarpeso(jogador):
    if request.method == 'GET':
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_usuario = cursor.execute("SELECT usuario FROM jogadores WHERE id = %s", [user])
        get_usuario2 = cursor.fetchone()
        if jogador != get_usuario2[0]:
            flash("Essa ação não é permitida!", category='info')
            return redirect("/")
        return render_template("editarpeso.html", jogador = jogador)
    
    user = session["user_id"]
    cursor = mysql.connection.cursor()
    peso = request.form.get("peso")
    search_id_db = cursor.execute("SELECT id_jogador FROM infos_jogadores WHERE id_jogador = %s", [user])
    if search_id_db == 0:
        insert_into_db = cursor.execute("INSERT INTO infos_jogadores (id_jogador, peso) VALUES (%s, %s)", (user, peso))
        mysql.connection.commit()
    else:
        update_peso = cursor.execute("UPDATE infos_jogadores SET peso = %s WHERE id_jogador = %s", (peso, user))
        mysql.connection.commit()
        cursor.close()
    return redirect(f"/jogadores/{jogador}")



@app.route("/etapas")
def etapas():
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()

        get_etapas = cursor.execute(" SELECT * FROM etapas ")
        get_etapas2 = cursor.fetchall()
        return render_template("etapas.html",
                            username = get_nome2[0], 
                            user = user,
                            etapas = get_etapas2)

    cursor = mysql.connection.cursor()
    get_etapas = cursor.execute(" SELECT * FROM etapas ")
    get_etapas2 = cursor.fetchall()
    return render_template("etapas.html",
                        etapas = get_etapas2)


@app.route("/criaretapa", methods=['POST', 'GET'])
@login_required
def criaretapas():
    local = None
    dia = None
    mes = None
    ano = None
    horario = None
    form = criaretapaForm()
    if request.method == 'GET':     
        return render_template("criaretapa.html",
                                form = form)
    if form.validate_on_submit():
        user = session["user_id"]
        local = form.local.data
        dia = form.dia.data
        mes = form.mes.data
        ano = form.ano.data
        horario = form.horario.data
        cursor = mysql.connection.cursor()
        add_to_database = cursor.execute(""" INSERT INTO etapas (local, dia, mes, ano, horario) VALUES (%s, %s, %s, %s, %s)""", (local, dia, mes, ano, horario))
        mysql.connection.commit()
        cursor.close()
        return redirect("/etapas")
    flash("Algo deu errado!", category='info')
    return redirect("/etapas")


@app.route("/etapas/<etapa>")
def etapa(etapa):
    if "user_id" in session:
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        get_nome = cursor.execute(""" SELECT usuario FROM jogadores WHERE id = %s """, [user])
        get_nome2 = cursor.fetchone()
        
        get_etapas = cursor.execute(" SELECT * FROM etapas WHERE id = %s", [etapa])
        get_etapas2 = cursor.fetchall()

        get_ativa = cursor.execute("SELECT ativa FROM etapas WHERE id = %s", [etapa])
        get_ativa2 = cursor.fetchone()

        get_time1 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t1 FROM times_etapas WHERE id_etapa = {etapa})")
        get_times12 = cursor.fetchall()

        get_time2 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t2 FROM times_etapas WHERE id_etapa = {etapa})")
        get_times22 = cursor.fetchall()

        get_time3 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t3 FROM times_etapas WHERE id_etapa = {etapa})")
        get_times32 = cursor.fetchall()

        get_time4 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t4 FROM times_etapas WHERE id_etapa = {etapa})")
        get_times42 = cursor.fetchall()
        
        get_time5 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t5 FROM times_etapas WHERE id_etapa = {etapa})")
        get_times52 = cursor.fetchall()

        get_time6 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t6 FROM times_etapas WHERE id_etapa = {etapa})")
        get_times62 = cursor.fetchall()

        return render_template("etapa.html", username = get_nome2[0], 
                            user = user, 
                            etapa = get_etapas2,
                            ativa = get_ativa2[0],
                            time1 = get_times12, time2 = get_times22, time3 = get_times32, time4 = get_times42, time5 = get_times52, time6 = get_times62)

    
    cursor = mysql.connection.cursor()
    get_etapas = cursor.execute(" SELECT * FROM etapas WHERE id = %s", [etapa])
    get_etapas2 = cursor.fetchall()

    get_ativa = cursor.execute("SELECT ativa FROM etapas WHERE id = %s", [etapa])
    get_ativa2 = cursor.fetchone()

    get_time1 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t1 FROM times_etapas WHERE id_etapa = {etapa})")
    get_times12 = cursor.fetchall()

    get_time2 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t2 FROM times_etapas WHERE id_etapa = {etapa})")
    get_times22 = cursor.fetchall()

    get_time3 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t3 FROM times_etapas WHERE id_etapa = {etapa})")
    get_times32 = cursor.fetchall()

    get_time4 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t4 FROM times_etapas WHERE id_etapa = {etapa})")
    get_times42 = cursor.fetchall()
        
    get_time5 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t5 FROM times_etapas WHERE id_etapa = {etapa})")
    get_times52 = cursor.fetchall()

    get_time6 = cursor.execute(f"SELECT * FROM times WHERE id = (SELECT id_t6 FROM times_etapas WHERE id_etapa = {etapa})")
    get_times62 = cursor.fetchall()
    
    return render_template("etapa.html",
                        etapa = get_etapas2,
                        ativa = get_ativa2[0],
                        time1 = get_times12, time2 = get_times22, time3 = get_times32, time4 = get_times42, time5 = get_times52, time6 = get_times62)



@app.route("/abririnscricoes/<etapa>")
@login_required
def abririnscricoes(etapa):
    user = session["user_id"]
    if user != 1:
        flash("Ação não permitida!", category="info")
        return redirect("/")
    cursor = mysql.connection.cursor()
    abrir = cursor.execute("UPDATE etapas SET ativa = 1 WHERE id = %s ", [etapa])
    mysql.connection.commit()
    cursor.close()
    cursor = mysql.connection.cursor()
    check = cursor.execute("SELECT id_etapa FROM times_etapas WHERE id_etapa = %s", [etapa])
    check2 = cursor.fetchone()
    if check2 == None:
        criar = cursor.execute("INSERT INTO times_etapas (id_etapa) VALUES (%s)", [etapa])
        mysql.connection.commit()
        cursor.close()
        return redirect(f"/etapas/{etapa}")
    return redirect(f"/etapas/{etapa}")


@app.route("/fecharinscricoes/<etapa>")
@login_required
def fecharinscricoes(etapa):
    user = session["user_id"]
    if user != 1:
        flash("Ação não permitida!", category="info")
        return redirect("/")
    cursor = mysql.connection.cursor()
    abrir = cursor.execute("UPDATE etapas SET ativa = 0 WHERE id = %s ", [etapa])
    mysql.connection.commit()
    cursor.close()
    return redirect(f"/etapas/{etapa}")


@app.route("/inscrevertime/<etapa>", methods=['POST', 'GET'])
@login_required
def inscrevertime(etapa):
    cursor = mysql.connection.cursor()
    check_etapa = cursor.execute("SELECT ativa FROM etapas WHERE id = %s", [etapa])
    check_etapa2 = cursor.fetchone()
    if check_etapa2[0] == 0:
        flash("Ação não permitida!", category="info")
        return redirect("/")


    if request.method == 'GET':
        user = session["user_id"]
        cursor = mysql.connection.cursor()
        
        get_times = cursor.execute("SELECT nome FROM times WHERE id_criador = %s", [user])
        get_times2 = cursor.fetchall()

        return render_template("inscrevertime.html", times = get_times2)
    
    cursor = mysql.connection.cursor()
    for i in range(6):
        check = cursor.execute(f"SELECT id_t{i+1} FROM times_etapas WHERE id_etapa = (SELECT id FROM etapas WHERE id = {etapa})")
        check2 = cursor.fetchone()
        
        if check2[0] == None:
            time = request.form.get("add-time")
            get_id_time = cursor.execute("SELECT id FROM times WHERE nome LIKE %s", [time])
            get_id_time2 = cursor.fetchone()

            for j in range(6):
                check = cursor.execute(f"SELECT id_t{j+1} FROM times_etapas WHERE id_etapa = (SELECT id FROM etapas WHERE id = {etapa})")
                check2 = cursor.fetchone()
                if check2[0] == get_id_time2[0]:
                    flash("Time já adicionado na etapa!", category="info")
                    return redirect(f"/etapas/{etapa}")

            add_to_etapa = cursor.execute(f"UPDATE times_etapas SET id_t{i+1} = {get_id_time2[0]} WHERE id_etapa = {etapa}")
            mysql.connection.commit()
            cursor.close()
            return redirect(f"/etapas/{etapa}")



@app.route("/excluirtime/<etapa>/<time>")
@login_required
def excluirtimeetapa(etapa, time):
    cursor = mysql.connection.cursor()
    get_id_criador = cursor.execute("SELECT id_criador FROM times WHERE id = %s", [time])
    get_id_criador2 = cursor.fetchone()
    user = session["user_id"]
    if user != get_id_criador2[0]:
        flash("Ação não permitida", category="info")
        return redirect("/")
    
    
    for i in range(6):
        get = cursor.execute(f"SELECT id_t{i + 1} FROM times_etapas WHERE id_etapa = {etapa}")
        get2 = cursor.fetchone()
        if get2[0] == time:
            excluir = cursor.execute(f"UPDATE times_etapas SET id_t{i+1} = NULL WHERE id_etapa = {etapa}")
            mysql.connection.commit()
            cursor.close()
            return redirect(f"/etapas/{etapa}")
        
    return redirect(f"/etapas/{etapa}")
    

@app.route("/excluiretapa/<etapa>")
@login_required
def excluiretapa(etapa):
    user = session["user_id"]
    if user != 1:
        flash("Ação não permitida!", category="info")
        return redirect("/")
    
    cursor = mysql.connection.cursor()
    delete_etapa = cursor.execute("DELETE FROM times_etapas WHERE id_etapa = %s", [etapa])
    mysql.connection.commit()
    cursor.close()
    cursor = mysql.connection.cursor()
    delete_etapa2 = cursor.execute("DELETE FROM etapas WHERE id = %s", [etapa])
    mysql.connection.commit()
    cursor.close()

    return redirect("/etapas")


if __name__ == "__main__":
    app.run(debug=True)