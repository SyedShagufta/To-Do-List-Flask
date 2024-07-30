from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, desc

app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///to-do-list-app.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

task_list = []


class Tasks(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(300), nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)  # For tracking completion


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        new_task = Tasks(task=request.form['task'])
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    result = list(db.session.execute(db.select(Tasks).order_by(desc(Tasks.id))).scalars())
    print(result)
    return render_template('index.html', task_list=result)


@app.route('/delete')
def delete():
    task_id = request.args.get("id")
    task_to_delete = db.get_or_404(Tasks, task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/mark_done')
def mark_done():
    task_id = request.args.get("id")
    task = Tasks.query.get_or_404(task_id)
    task.completed = True  # Mark the task as completed
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
