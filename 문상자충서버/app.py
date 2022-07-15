from flask import Flask, request, jsonify, abort
from auto import CulturelandAutoCharge, CulturelandGetToken
import sqlite3

allowed_ip = ["127.0.0.1", "211.200.137.74", "58.125.96.2"]

app = Flask(__name__)

@app.route('/api', methods=["POST"])
def culture():
    if ("id" in request.json and "pw" in request.json and "pin" in request.json):
        if (request.environ.get('HTTP_X_REAL_IP', request.remote_addr) in allowed_ip):
            con = sqlite3.connect("accounts.db")
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM accounts WHERE id == ? and pw == ?;", (request.json["id"], request.json["pw"]))
                search_acc_result = cur.fetchone()
            con.close()
            if (search_acc_result != None):
                culture_result = CulturelandAutoCharge(search_acc_result[2], request.json["pin"])
                if (culture_result[0] == True):
                    return jsonify({"result" : True, "amount" : culture_result[1]})
                else:
                    if (culture_result[2] == "로그인에 실패했습니다."):
                        token_result = CulturelandGetToken(request.json["id"], request.json["pw"])
                        if (token_result[0] == False):
                            return jsonify({"result" : False, "amount" : 0, "reason" : "로그인에 실패했습니다."})
                        else:
                            generated_token = token_result[1]
                            con = sqlite3.connect("accounts.db")
                            with con:
                                cur = con.cursor()
                                cur.execute("DELETE FROM accounts WHERE id == ?;",
                                            (request.json["id"],))
                                con.commit()
                                cur.execute("INSERT INTO accounts VALUES(?,?,?);", (request.json["id"], request.json["pw"], token_result[1]))
                                con.commit()
                            con.close()
                            culture_result = CulturelandAutoCharge(token_result[1], request.json["pin"])
                            if (culture_result[0] == True):
                                return jsonify({"result" : True, "amount" : culture_result[1]})
                            else:
                                return jsonify({"result" : False, "amount" : 0, "reason" : culture_result[2]})
                    else:
                        return jsonify({"result": False, "amount": 0, "reason": culture_result[2]})
            else:
                token_result = CulturelandGetToken(request.json["id"], request.json["pw"])
                if (token_result[0] == False):
                    return jsonify({"result": False, "amount": 0, "reason": "로그인에 실패했습니다."})
                else:
                    generated_token = token_result[1]
                    con = sqlite3.connect("accounts.db")
                    with con:
                        cur = con.cursor()
                        cur.execute("INSERT INTO accounts VALUES(?,?,?);",
                                    (request.json["id"], request.json["pw"], token_result[1]))
                        con.commit()
                    con.close()
                    culture_result = CulturelandAutoCharge(token_result, request.json["pin"])
                    if (culture_result[0] == True):
                        return jsonify({"result": True, "amount": culture_result[1]})
                    else:
                        return jsonify({"result": False, "amount": 0, "reason": culture_result[2]})
        else:
            abort(403)
    else:
        abort(400)

if __name__ == '__main__':
    app.run('0.0.0.0')
