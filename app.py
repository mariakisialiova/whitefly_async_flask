from asgiref.wsgi import WsgiToAsgi
from flask import Flask, redirect, render_template, request, url_for
from models import db
from celery_worker import celery_init_app
from tasks import save_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/0",
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)
db.init_app(app)

asgi_app = WsgiToAsgi(app)

with app.app_context():
    db.create_all()


@app.route('/')
async def hello_world():
    return render_template('index.html')


@app.route('/confirmation')
async def confirmation():
    return render_template('confirmation.html')


@app.route('/form', methods=['GET', 'POST'])
async def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        save_user.apply_async(args=[name, email])
        return redirect(url_for('confirmation'))
    return render_template('form.html')


if __name__ == '__main__':
    app.run(debug=True)
