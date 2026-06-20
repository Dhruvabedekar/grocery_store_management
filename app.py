
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MYSQL CONNECTION
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="grocery_store"
)

cursor = db.cursor(dictionary=True)

# HOME PAGE
@app.route('/')
def index():

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    return render_template(
        'index.html',
        products=products
    )

# CATEGORY FILTER
@app.route('/category/<string:category>')
def category(category):

    cursor.execute(
        "SELECT * FROM products WHERE category=%s",
        (category,)
    )

    products = cursor.fetchall()

    return render_template(
        'index.html',
        products=products
    )

# ADD PRODUCT
@app.route('/add', methods=['POST'])
def add_product():

    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    quantity = request.form['quantity']

    sql = """
        INSERT INTO products
        (name, category, price, quantity)
        VALUES(%s, %s, %s, %s)
    """

    values = (
        name,
        category,
        price,
        quantity
    )

    cursor.execute(sql, values)

    db.commit()

    return redirect('/')

# DELETE PRODUCT
@app.route('/delete_product/<int:id>')
def delete_product(id):

    cursor.execute(
        "DELETE FROM products WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/')

# CART PAGE
@app.route('/cart')
def cart():

    category = request.args.get('category')

    if category:

        cursor.execute(
            "SELECT * FROM products WHERE category=%s",
            (category,)
        )

    else:

        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template(
        'cart.html',
        products=products
    )

# PLACE ORDER
@app.route('/place_order', methods=['POST'])
def place_order():

    customer_name = request.form['customer_name']

    selected_products = request.form.getlist('products')

    total_amount = 0

    # CREATE ORDER
    cursor.execute(
        "INSERT INTO orders(customer_name, total_amount) VALUES(%s, %s)",
        (customer_name, 0)
    )

    db.commit()

    order_id = cursor.lastrowid

    for item in selected_products:

        product_id, qty = item.split('-')

        qty = int(qty)

        cursor.execute(
            "SELECT * FROM products WHERE id=%s",
            (product_id,)
        )

        product = cursor.fetchone()

        total = qty * float(product['price'])

        total_amount += total

        cursor.execute("""
            INSERT INTO order_items
            (order_id, product_name, quantity, price, total)
            VALUES(%s, %s, %s, %s, %s)
        """, (
            order_id,
            product['name'],
            qty,
            product['price'],
            total
        ))

    # UPDATE TOTAL
    cursor.execute(
        "UPDATE orders SET total_amount=%s WHERE id=%s",
        (total_amount, order_id)
    )

    db.commit()

    return redirect('/orders')

# ORDERS PAGE
@app.route('/orders')
def orders():

    cursor.execute("SELECT * FROM orders")

    orders = cursor.fetchall()

    return render_template(
        'orders.html',
        orders=orders
    )

# ORDER DETAILS
@app.route('/order_details/<int:id>')
def order_details(id):

    cursor.execute(
        "SELECT * FROM order_items WHERE order_id=%s",
        (id,)
    )

    items = cursor.fetchall()

    return render_template(
        'order_details.html',
        items=items
    )

# DELETE ORDER
@app.route('/delete_order/<int:id>')
def delete_order(id):

    cursor.execute(
        "DELETE FROM order_items WHERE order_id=%s",
        (id,)
    )

    cursor.execute(
        "DELETE FROM orders WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/orders')

if __name__ == '__main__':
    app.run(debug=True)