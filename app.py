from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base

from waitress import serve

from flask import Flask, render_template, request, redirect, session as flask_session
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from datetime import datetime
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do .env
load_dotenv()

# Flask
app = Flask(__name__)
app.secret_key = os.environ.get("APP_KEY")
user = os.environ.get("usuario")
password = os.environ.get("senha")
user_sql = os.environ.get("PGUSER")
password_sql = os.environ.get("PGPASSWORD")
host_sql = os.environ.get("PGHOST")
db_name = os.environ.get("PGDATABASE")


# Conexão via DATABASE_URL
DATABASE_URL = f"postgresql://{user_sql}:{password_sql}@{host_sql}:5432/{db_name}"
engine = create_engine(DATABASE_URL, echo=False)

# SQLAlchemy Base e sessão
Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(bind=engine))


# Modelo
class Msg(Base):
    __tablename__ = "MSG"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    nome = Column("NOME", String(255), nullable=False)
    end_email = Column("END_EMAIL", String(255), nullable=False)
    assunto = Column("ASSUNTO", String(255), nullable=False)
    mensagem = Column("MENSAGEM", Text, nullable=False)
    dt = Column("DT", DateTime(timezone=True), server_default=func.now())


# Cria as tabelas se não existirem
Base.metadata.create_all(bind=engine)


# Rotas
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == os.getenv("usuario") and senha == os.getenv("senha"):
            flask_session["usuario"] = usuario
            return redirect("/tabela")
        else:
            return render_template(
                "user/login.html",
                erro1="Usuário ou senha inválidos!",
                erro2="Tente novamente.",
            )
    return render_template("user/login.html")


@app.route("/tabela", methods=["GET"])
def tabela():
    if "usuario" not in flask_session:
        return redirect("/login")
    session = SessionLocal()
    mensagens = session.query(Msg).all()
    session.close()
    dados = [
        {
            "nome": m.nome,
            "email": m.end_email,
            "assunto": m.assunto,
            "mensagem": m.mensagem,
            "dt": m.dt.strftime("%d/%m/%Y %H:%M"),
        }
        for m in mensagens
    ]
    nome_user = (
        "Charlante"
        if flask_session["usuario"] == "charlante"
        else flask_session["usuario"]
    )
    return render_template(
        "user/tabela.html", nome=nome_user, dic=dados if dados else ""
    )


@app.route("/tabela", methods=["POST"])
def delete():
    if "usuario" not in flask_session:
        return redirect("/login")
    session = SessionLocal()
    session.query(Msg).delete()
    session.commit()
    session.close()
    return redirect("/tabela")


@app.route("/logout")
def logout():
    flask_session.clear()
    return redirect("/login")


# Páginas do site
@app.route("/")
@app.route("/index.html")
@app.route("/sobre")
def index():
    return render_template("site/index.html")


@app.route("/experiencia")
def experiencia():
    return render_template("site/experiencia.html")


@app.route("/educacao")
def educacao():
    return render_template("site/educacao.html")


@app.route("/habilidades")
def habilidades():
    return render_template("site/habilidades.html")


@app.route("/interesses")
def interesses():
    return render_template("site/interesse.html")


@app.route("/contato")
def contato():
    return render_template("site/contato.html")


@app.route("/contato", methods=["POST"])
def enviar():
    nome = request.form.get("nome")
    email = request.form.get("end_email")
    assunto = request.form.get("assunto")
    mensagem = request.form.get("mensagem")

    if not all([nome, email, assunto, mensagem]):
        return redirect("/erro")

    nova_msg = Msg(
        nome=nome,
        end_email=email,
        assunto=assunto,
        mensagem=mensagem,
        dt=datetime.now(),
    )
    session = SessionLocal()
    session.add(nova_msg)
    session.commit()
    session.close()

    return redirect("/sucesso")


@app.route("/sucesso")
def sucesso():
    return render_template("site/sucesso.html")


@app.route("/erro")
def erro():
    return render_template("site/erro.html")


# Execução
if __name__ == "__main__":
    serve(app, host="0.0.0.0")
    # app.run(host="localhost", port=9000, debug=True)
