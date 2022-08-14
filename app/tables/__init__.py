from flask import Blueprint

tables = Blueprint('tables', __name__)

from . import views