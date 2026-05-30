import pymongo
import bcrypt
import re
from flask import Flask, request, jsonify
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

# Connects to local MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Uses database 'SwedishDB'
db = client["SwedishDB"]

# Select collections from the database
food_items_collection = db["SwedishFilteredItems"] # Collection for food item documents
users_collection = db["Users"] # Collection for user documents

def search_for_swedish_product_name(barcode):
    """
    Search for a Swedish product by its barcode in the food items collection.

    Args:
        barcode (str): The barcode of the product to search for.

    Returns:
        dict: A dictionary containing product details if found:
            - product (str): Swedish product name
            - ingredients (str): Ingredients text
            - quantity (str): Product quantity
            - barcode (str): The product barcode
            - image_url (str): URL to the product image
        If not found, returns a dictionary with an error message.
    """
    print("Searching for Swedish product name")

    # Find food document by barcode
    food_items = food_items_collection.find({
        "_id": barcode,
    })

    for item in food_items:
        # Extracts swedish product name. Defaults to empty string
        product_name = str(item.get("product_name_sv", ""))
        if product_name:
            print("Product found")
            # Return product details in dictionary
            return {
                "product": product_name,
                "ingredients": str(item.get("ingredients_text", "")),
                "quantity": str(item.get("quantity", "")),
                "barcode": barcode,
                "image_url": str(item.get("image_url", ""))
            }
    print("Product not found")
    # Returns error message if product not found
    return {"error": "Product not found"}

@app.route("/product/<barcode>", methods=["GET"])
def get_product(barcode):
    """
    Retrieve product details by barcode.

    Args:
        barcode (str): The 13-character barcode of the product.

    Returns:
        JSON response with product details and HTTP 200 if found,
        or an error message with HTTP 400 (invalid barcode) or 404 (not found).
    """

    # Validate that barcode is provided and has exactly 13 characters
    if not barcode or (len(barcode) != 13):
        return jsonify({"error": "No/invalid barcode provided"}), 400

    # Find food document by barcode
    food_items = food_items_collection.find({
        "_id": barcode,
    })

    for item in food_items:
        # Extracts product_name from database result. Defaults to empty string
        product_name = str(item.get("product_name", ""))
        if product_name:
            print("Product found")
            # Returns JSON food object
            return jsonify({
                "product": product_name,
                "ingredients": str(item.get("ingredients_text", "")),
                "quantity": str(item.get("quantity", "")),
                "barcode": barcode,
                "image_url": str(item.get("image_url", ""))
            }), 200

    # If not product_name was found, calls function to check for swedish product_name
    search_result = search_for_swedish_product_name(barcode)

    # Returns swedish product object if a swedish product name was found, else returns error message
    if "error" in search_result:
        return jsonify(search_result), 404
    else:
        return jsonify(search_result), 200

@app.route("/users", methods=["POST"])
def users():
    """
    Register a new user by storing their data with a hashed password.

    Expects JSON data with:
        - surname (str)
        - lastname (str)
        - email (str)
        - password (str)

    Returns:
        - 201 Created: If the user is registered successfully.
        - 400 Bad Request: If the request has missing or invalid data.
        - 409 Conflict: If the email address is already registered.
        - 500 Internal Server Error: For any other server-side errors.
    """
    try:
        data = request.get_json()

        # Check if JSON data exists in the request
        if not data:
            return jsonify({"error": "Request must contain JSON data."}), 400

        required_fields = ["surname", "lastname", "email", "password", "confirm_password"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": "Validation failed",
                    "message": f"{field.capitalize().replace('_', ' ')} is required."
                }), 400

        surname = data.get("surname").strip()
        lastname = data.get("lastname").strip()
        email = data.get("email").strip().lower()
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        validation_errors = {}
        if not surname:
            validation_errors["surname"] = "Surname cannot be empty."
        if not lastname:
            validation_errors["lastname"] = "Lastname cannot be empty."

        # Email format validation
        email_regex = re.compile(r"^(?!.*\.\.)[^\s@]+@[^\s@]+\.[^\s@]+$")
        if not email_regex.match(email):
            validation_errors["email"] = "Please enter a valid email address."

        # Password strength validation
        password_regex = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,}$")
        if not password_regex.match(password):
            validation_errors["password"] = ("Password must be at least 6 characters, "
                                             "include 1 uppercase, 1 number, and 1 special character.")

        if password != confirm_password:
            validation_errors["confirm_password"] = "Passwords do not match. Please try again."

        if validation_errors:
            return jsonify({
                "error": "Validation failed",
                "message": "One or more fields have invalid data.",
                "details": validation_errors
            }), 400

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        user_document = {
            "surname": surname,
            "lastname": lastname,
            "email": email,
            "password": hashed_password,
        }

        users_collection.insert_one(user_document)

        return jsonify({
            "message": "User registered successfully",
            "user": {"surname": surname, "email": email}
        }), 201

    except DuplicateKeyError:
        # Catch the duplicate key error from MongoDB
        return jsonify({
            "error": "Conflict",
            "message": "This email address is already registered."
        }), 409

    except Exception as e:
        # Catch any other server errors and return a generic message
        # Log the actual error for debugging purposes
        print(f"An unexpected error occurred: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server."
        }), 500

@app.route("/users/<email>", methods=["GET"])
def get_user(email):
    """
    Retrieve user information by email.

    Args:
        email (str): The email of the user to look up.

    Returns:
        JSON response with user data (surname, lastname, email) and HTTP 200 if found,
        otherwise an error message with HTTP 404.
    """

    # Find user document by matching email
    user_data = users_collection.find({
        "email": email,
    })

    for item in user_data:
        # Extracts email from database result. Defaults to empty string
        db_email = str(item.get("email", ""))
        # Confirm matching email
        if db_email == email:
            return jsonify({
                "surname": str(item.get("surname", "")),
                "lastname": str(item.get("lastname", "")),
                "email": email,
            }), 200

    # Returns 404 response if no user was found
    return jsonify({"error": "User not found"}), 404

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user by verifying email and password.

    Expects JSON payload with:
        - email (str)
        - password (str)

    Returns:
        JSON success message with HTTP 200 if authentication succeeds,
        or error message with HTTP 401 for invalid credentials,
        or HTTP 500 for server errors.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        # Find user by email
        user = users_collection.find_one({"email": email})
        if not user:
            # No user found. Returns error message
            return jsonify({"error": "Invalid email or password"}), 401
        # Check provided password against stored hashed password
        if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            # Authentication successful. Returns true success boolean
            return jsonify({"success": True}), 200

        # Invalid password. Returns error message
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        # Logs the exception and returns error message
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def hello():
    return "Hello from the correct file!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
