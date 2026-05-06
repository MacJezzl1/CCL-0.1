from flask import Flask,jsonify
app=Flask(__name__)
@app.route("/")
def i(): return jsonify({"app":"HelloCCL","ccl":"0.1"})
if __name__=="__main__": app.run(debug=True)
