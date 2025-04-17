from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import json
app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    conn = sqlite3.connect('database/mall.db')
    conn.row_factory = sqlite3.Row  # 딕셔너리처럼 사용 가능
    return conn

def get_products():
    conn = sqlite3.connect('database/mall.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return products

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not name or not email or not password:
            flash('모든 항목을 입력해주세요.')
            return redirect(url_for('register'))

        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, password)
            )
            conn.commit()
            conn.close()
            flash('회원가입이 완료되었습니다.')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('이미 등록된 이메일입니다.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                            (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        else:
            flash("이메일 또는 비밀번호가 올바르지 않습니다.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    # JSON에서 설명 정보 로드
    with open('static/data/product_descriptions.json', encoding='utf-8') as f:
        descriptions = json.load(f)
        product_desc = descriptions.get(str(product_id), {})

    return render_template('product_detail.html', product=product, desc=product_desc)

    
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        flash('로그인 후 이용 가능합니다.')
        return redirect(url_for('login'))
    
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    cart = session.get('cart', [])

    # 중복 상품이면 수량만 추가
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})

    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('로그인 후 이용 가능합니다.')
        return redirect(url_for('login'))
    cart_items = session.get('cart', [])

    conn = get_db_connection()
    products = []
    total_price = 0

    for item in cart_items:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (item['product_id'],)).fetchone()
        if product:
            quantity = int(item['quantity'])
            subtotal = product['price'] * quantity
            total_price += subtotal
            products.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': quantity,
                'subtotal': subtotal
            })
    conn.close()

    return render_template('cart.html', products=products, total_price=total_price)

@app.route('/cart/update', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        flash('로그인 후 이용 가능합니다.')
        return redirect(url_for('login'))
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        flash('로그인 후 이용 가능합니다.')
        return redirect(url_for('login'))
    product_id = int(request.form['product_id'])
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/products')
def products():
    category = request.args.get('category')

    conn = get_db_connection()
    
    if category:
        products = conn.execute('SELECT * FROM products WHERE category = ?', (category,)).fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()

    categories = conn.execute('SELECT DISTINCT category FROM products').fetchall()
    conn.close()

    return render_template('product.html', products=products, categories=categories, selected=category)

@app.context_processor
def cart_count_processor():
    cart = session.get('cart', [])
    total_items = sum(item['quantity'] for item in cart)
    return dict(cart_count=total_items)

@app.route('/contact')
def contact():
    board_type = request.args.get('type', 'notice')

    conn = get_db_connection()
    posts = conn.execute(
        'SELECT * FROM posts WHERE board_type = ? ORDER BY created_at DESC',
        (board_type,)
    ).fetchall()
    conn.close()

    return render_template('contact.html', board_type=board_type, posts=posts)

@app.route('/contact/write', methods=['GET', 'POST'])
def write_post():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))

    board_type = request.args.get('type', 'qna')

    if board_type in ['notice', 'faq'] and not session.get('is_admin'):
        flash('접근 권한이 없습니다.')
        return redirect(url_for('contact', type=board_type))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = session['user_id']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO posts (title, content, board_type, author_id) VALUES (?, ?, ?, ?)',
            (title, content, board_type, author_id)
        )
        conn.commit()
        conn.close()

        flash('글이 작성되었습니다.')
        return redirect(url_for('contact', type=board_type))

    return render_template('write_post.html', board_type=board_type)

@app.route('/edit_post_inline', methods=['POST'])
def edit_post_inline():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))

    post_id = request.form['post_id']
    title = request.form['title']
    content = request.form['content']

    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    if not post or (session['user_id'] != post['author_id'] and not session.get('is_admin')):
        flash('수정 권한이 없습니다.')
        return redirect(url_for('contact', type=post['board_type']))

    conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
    conn.commit()
    conn.close()

    flash('게시글이 수정되었습니다.')
    return redirect(url_for('contact', type=post['board_type']))

if __name__ == "__main__":
    app.run(debug=True)
