from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from config.database import db
from backend.models import Class, Document

class_bp = Blueprint('class', __name__, url_prefix='/class')


@class_bp.route('/')
@login_required
def list_class():
    classes = Class.query.all()
    return render_template('class/list.html', classes=classes)


@class_bp.route('/<int:id>')
@login_required
def class_detail(id):
    class_obj = Class.query.get_or_404(id)
    documents = Document.query.filter_by(class_id=class_obj.id).all()
    return render_template('class/detail.html', class_obj=class_obj, documents=documents)