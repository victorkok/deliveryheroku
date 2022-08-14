from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Consumer, Product, Destiny, Theme
from . import tables


@tables.route('/consumer')
def consumer():
    # consumers = Consumer.query.with_entities(Consumer.id, Consumer.username,
    #                                          Consumer.email)
    consumers = Consumer.query.all()
    return render_template('consumer/consumer.html', consumers=consumers)


@tables.route('/edit_consumer/<int:id>', methods=['GET', 'POST'])
def edit_destiny(id):
    consumer = Consumer.query.get(id)
    if request.method == 'POST':
        consumer.destiny.address = request.form['address']
        consumer.destiny.number = request.form['number']
        consumer.destiny.zipcode = request.form['zipcode']
        consumer.destiny.neighborhood = request.form['neighborhood']
        consumer.destiny.complement = request.form['complement']
        consumer.destiny.city = request.form['city']
        consumer.destiny.state = request.form['state']
        db.session.commit()
        return redirect(url_for('tables.consumer'))
    return render_template('consumer/edit_destiny.html', consumer=consumer)


@tables.route('/delete_consumer/<int:id>')
def delete_consumer(id):
    consumer = Consumer.query.get(id)
    db.session.delete(consumer)
    db.session.commit()
    return redirect(url_for('tables.consumer'))


@tables.route('/product')
def product():
    products = Product.query.all()
    return render_template('product/product.html', products=products)


@tables.route("/add_product", methods=["GET", "POST"])
def add_product():
    theme = Theme()
    themes = theme.query.all()
    if request.method == 'POST':
        theme_got = request.form['theme']
        product = Product(name=request.form['name'],
                          price=request.form['price'].replace(",", "."),
                          description=request.form['description'],
                          players=request.form['players'],
                          age=request.form['age'],
                          theme=theme.query.filter_by(name=theme_got).first())
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('tables.product'))
    return render_template('product/add_product.html', themes=themes)


@tables.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get(id)
    theme = Theme()
    themes = theme.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        product.players = request.form['players']
        product.age = request.form['age']
        new_theme = theme.query.filter_by(name=request.form['theme']).first()
        print(">>>", new_theme.id)
        print("--->", product.theme.id)
        product.theme_id = new_theme.id
        db.session.commit()
        return redirect(url_for('tables.product'))
    return render_template('product/edit_product.html', product=product, themes=themes)


@tables.route('/delete_product/<int:id>')
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('tables.product'))

@tables.route('/product/<int:id>')
def get_produto_id(id):
    product = Product.query.get(id)
    return render_template('product/product_id.html', product=product)

@tables.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)