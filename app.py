from flask import Flask, jsonify


app = Flask(__name__)



@app.get("/")
def index():
    return "Hello World!!"


@app.get("/hello")
def say_hello():
    # return jsonify({"message":"Hello World!!"})
    return {"message":"Hello World!!"}

