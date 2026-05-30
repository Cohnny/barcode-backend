# Swedish Food Barcode Scanner API

This project is a RESTful API built with Flask that allows users to:

- Search for food product details by scanning barcodes (with support for Swedish product names),
- Register and authenticate users securely,
- Hash passwords using bcrypt,
- Store and retrieve data from a MongoDB database.

## Features

- **Barcode Lookup**: Search for product details by 13-digit barcode.
- **Swedish Fallback**: If no English product name is found, the API attempts to return the Swedish name instead.
- **User Registration & Login**:
  - Password hashing using bcrypt.
  - Strong password validation.
  - Duplicate email check and conflict handling.
- **Secure Authentication**: Passwords are never stored in plain text.
- **Input Validation**: Handles edge cases like empty fields, invalid emails, and weak passwords.

---

## Technologies

- **Python** & **Flask** – Web framework.
- **MongoDB** – NoSQL database for storing food items and user accounts.
- **bcrypt** – Secure password hashing.
- **Regex** – Used for validating email and password formats.

## API Endpoints

### GET `/product/<barcode>`

Retrieves product details from the database using a 13-digit barcode.

- Returns a JSON object with product information.
- If `product_name` is not found, attempts to retrieve `product_name_sv`.

**Success Response**

- Code: `200 OK`
- Content:

```json
{
  "product": "Mjölk",
  "ingredients": "Mjölk",
  "quantity": "1L",
  "barcode": "1234567890123",
  "image_url": "https://example.com/image.jpg"
}
```

**Error Responses**

- Code: `400 Bad Request`: Invalid or missing barcode.
- Code: `404 Not Found`: Product not found in the database.

---

### POST `/users`

Registers a new user with hashed password and validation.

**Expected JSON Payload**

```json
{
  "surname": "Anna",
  "lastname": "Andersson",
  "email": "anna@example.com",
  "password": "StrongPass123!",
  "confirm_password": "StrongPass123!"
}
```

**Validation Requirements**

- All fields are required.
- Email must be valid.
- Password must:
  - Be at least 6 characters long,
  - Contain at least 1 uppercase letter,
  - Contain at least 1 number,
  - Contain at least 1 special character (`@$!%*?&`).

**Success Response**

- Code: `201 Created`

```json
{
  "message": "User registered successfully",
  "user": {
    "surname": "Anna",
    "email": "anna@example.com"
  }
}
```

**Error Responses**

- `400 Bad Request`: Missing or invalid fields.
- `409 Conflict`: Email is already registered.
- `500 Internal Server Error`: Unexpected server error.

---

### POST `/login`

Authenticates a user using email and password.

**Expected JSON Payload**

```json
{
  "email": "anna@example.com",
  "password": "StrongPass123!"
}
```

**Success Response**

- Code: `200 OK`

```json
{
  "success": true
}
```

**Error Response**

- Code: `401 Unauthorized`: Invalid email or password.

---

### GET `/users/<email>`

Retrieves basic user information by email. Passwords are never included in the response.

**Success Response**

- Code: `200 OK`

```json
{
  "surname": "Anna",
  "lastname": "Andersson",
  "email": "anna@example.com"
}
```

**Error Response**

- Code: `404 Not Found`: User not found.

---

## Database Structure

### Collection: `SwedishFilteredItems`

Each document represents a food product:

```json
{
  "_id": "1234567890123",
  "product_name": "Milk",
  "product_name_sv": "Mjölk",
  "ingredients_text": "Mjölk",
  "quantity": "1L",
  "image_url": "https://example.com/image.jpg"
}
```

### Collection: `Users`

Each document represents a registered user:

```json
{
  "surname": "Anna",
  "lastname": "Andersson",
  "email": "anna@example.com",
  "password": "$2b$12$hashedPasswordHere..."
}
```

### Prerequisites

- Python 3.13 or later
- MongoDB running (local or remote)
- pip package manager

### Installation Steps

1. git clone https://github.com/Magnuskyh/Barcode_scanner_be.git
2. Navigate to the project folder:<br>`cd \your\path\to\barcode_scanner`
3. Open CMD in the project folder.
4. Run the following command to install the required dependencies:<br>`pip install -r requirements.txt`
