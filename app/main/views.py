from flask import Blueprint, render_template, session
from . import main


@main.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', name=session.get('name'), known=session.get('known', False))