print("=== BACKEND API THU VIEN ===")

from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)  # cho phép frontend gọi API

@app.route("/")
def home():
    return "Backend da run" 
    
# Firebase
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

firebase_key = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)
db = firestore.client()



# LẤY DANH SÁCH SÁCH
@app.route("/api/books", methods=["GET"])
def get_books():
    books_ref = db.collection("books").stream()
    books = []

    for b in books_ref:
        data = b.to_dict()
        data["id"] = b.id
        books.append(data)

    return jsonify(books)


# THÊM SÁCH
@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.json

    db.collection("books").add({
        "title": data["title"],
        "author": data["author"],
        "quantity": int(data["quantity"])
    })

    return jsonify({"message": "Đã thêm sách"}), 201


# SỬA SÁCH
@app.route("/api/books/<book_id>", methods=["PUT"])
def edit_book(book_id):
    data = request.json

    db.collection("books").document(book_id).update({
        "title": data["title"],
        "author": data["author"],
        "quantity": int(data["quantity"])
    })

    return jsonify({"message": "Đã cập nhật sách"})


# XÓA SÁCH
@app.route("/api/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    db.collection("books").document(book_id).delete()
    return jsonify({"message": "Đã xóa sách"})



# MƯỢN SÁCH
@app.route("/api/borrow/<book_id>", methods=["POST"])
def borrow_book(book_id):
    data = request.json
    borrower = data["borrower"]

    book_ref = db.collection("books").document(book_id)
    book = book_ref.get().to_dict()

    if book["quantity"] <= 0:
        return jsonify({"error": "Sách đã hết"}), 400

    db.collection("borrows").add({
        "book_id": book_id,
        "book_title": book["title"],
        "borrower": borrower,
        "status": "borrowing"
    })

    book_ref.update({
        "quantity": book["quantity"] - 1
    })

    return jsonify({"message": "Mượn sách thành công"})



# DANH SÁCH ĐANG MƯỢN
@app.route("/api/borrowings", methods=["GET"])
def get_borrowings():
    borrows_ref = db.collection("borrows").stream()
    borrows = []

    for b in borrows_ref:
        data = b.to_dict()
        data["id"] = b.id
        borrows.append(data)

    return jsonify(borrows)


# TRẢ SÁCH
@app.route("/api/return/<borrow_id>", methods=["POST"])
def return_book(borrow_id):
    borrow_ref = db.collection("borrows").document(borrow_id)
    borrow = borrow_ref.get().to_dict()

    book_ref = db.collection("books").document(borrow["book_id"])
    book = book_ref.get().to_dict()

    borrow_ref.update({"status": "returned"})
    book_ref.update({"quantity": book["quantity"] + 1})

    return jsonify({"message": "Đã trả sách"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
