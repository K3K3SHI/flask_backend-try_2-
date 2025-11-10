from flask import Flask, jsonify, request,send_from_directory
from flask_cors import CORS
import da.login_da
import da.product_da
import os
from werkzeug.utils import secure_filename
import stripe


app = Flask(__name__)
CORS(app, origins=["https://vercelapp-page.vercel.app/"])  # Enable CORS so React app on different origin can call this API
IMG_DIR = os.path.join("static", "images")
os.makedirs(IMG_DIR, exist_ok=True)
stripe.api_key = "sk_test_51SQYIqDSFdmXUPuARshdAMR8KQ6XUhI0ZWXsFRw9qu5De3svXv1sewkQzhKdcTA6oFcU5jj9GlBL0FRpL9nyP7ol00JnR5zMfr"
# Your Stripe test secret key


@app.route('/')
def hello():
    return 'Hi there'


product_data = []


@app.route('/productlist', methods=['GET'])
def get_products():
    products = da.product_da.get_all_products()
    return jsonify({"status": "OK", "product": products}), 200


@app.route('/filter_products', methods=['GET'])
def fil_products():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email parameter"}), 400

    products = da.product_da.get_user_products(email)
    return jsonify({"products": products})


# CHANGED: Accept multipart/form-data and save image
@app.route("/products", methods=["POST"])
def add_product():
    # Check request type
    if 'multipart/form-data' not in request.content_type:
        return jsonify({"error": "Content-Type must be multipart/form-data"}), 400

    name = request.form.get("name")
    details = request.form.get("details")
    seller_id = request.form.get("seller_id")
    image_file = request.files.get("image")
    price = request.form.get("price")
    category = request.form.get("category")
    stock = request.form.get("stock")
    brand = request.form.get("brand")
    color = request.form.get("color")

    if not all([name, details, seller_id, image_file]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        return jsonify({"error": "Price and stock must be numeric"}), 400

    filename = secure_filename(image_file.filename)
    image_path = os.path.join(IMG_DIR, filename)
    image_file.save(image_path)
    image_url = f"/static/images/{filename}"

    da.product_da.add_product(name, details, image_url, seller_id, price, category, stock, brand, color)
    products = da.product_da.get_all_products()
    return jsonify({"status": "OK", "product": products}), 201


# CHANGED: Serve uploaded images
@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMG_DIR, filename)


@app.route('/product/<int:id>', methods=['GET'])
def get_product_detail(id):
    product = da.product_da.get_product_by_id(id)  # Implement this function in your product_da
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"product": product}), 200


@app.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    try:
        user_id = data.get('user_id')
        address = data.get('address')
        items = data.get('items')
        total_price = data.get('total_price')
        status = "Pending"
        print(user_id)
        print(items)
        print(address)
        print(total_price)
        print(status)
        # --- Robust validation (feature 8) ---
        if not user_id or not address or not items or total_price is None:
            return jsonify({'error': 'Missing fields'}), 400
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({'error': 'Order must have items'}), 400
        try:
            total_price = float(total_price)
        except:
            return jsonify({'error': 'Invalid price'}), 400

        order_id = da.product_da.insert_order(user_id, items, address, total_price, status)
        return jsonify({'success': True, 'order_id': order_id}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': 'Could not create order'}), 500


@app.route('/orders_get', methods=['GET'])
def get_user_orders():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    try:
        orders = da.product_da.get_orders_by_user(user_id)
        return jsonify({'orders': orders}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Could not fetch orders'}), 500


@app.route('/login', methods=['POST'])
def login():
    print('called login')
    data = request.get_json()  # Parse JSON data sent by React
    user_name = data.get('user_name') if data else None
    password = data.get('password') if data else None

    response_dict = da.login_da.check_login(user_name, password)
    return jsonify(response_dict)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['login_name', 'password', 'first_name', 'last_name']
    if not all(data.get(field) for field in required):
        return jsonify({'error': 'Missing registration fields'}), 400

    user = da.product_da.register_user(
        login_name=data['login_name'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    if 'error' in user:
        return jsonify({'error': user['error']}), 500
    return jsonify(user)


@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    data = request.get_json()
    try:
        amount_in_paise = int(float(data['amount']) * 100)
        intent = stripe.PaymentIntent.create(
            amount=amount_in_paise,
            currency='inr',
            metadata={'integration_check': 'accept_a_payment'},
        )
        return jsonify({'clientSecret': intent['client_secret']})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Payment error'}), 500


@app.route('/update_order_status', methods=['POST'])
def update_order_status_route():
    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('new_status')  # Example: "Complete"
    if not order_id or not new_status:
        return jsonify({'error': 'Missing order ID or status'}), 400
    da.product_da.update_order_status(order_id, new_status)
    return jsonify({'success': True})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
