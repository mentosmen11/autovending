from flask import Flask, render_template, request, session, redirect, abort
import sqlite3, os, uuid, licensing
import funcs as fc

def alert(msg, href):
    return f"<script>alert('{msg}'); location.href = `{href}`;</script>"

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

@app.route("/", methods=["GET"])
def index():
    if  "id" in session:
        return redirect("/main")
    else:
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if  "id" in session:
        return redirect("/main")
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not ("username" in request.form and "password" in request.form):
            abort(400)
        username = request.form["username"]
        password = request.form["password"]
        if not username.isdigit():
            return alert("로그인 정보가 틀렸습니다.", "/login")
        if not fc.is_guild_valid(username)[0]:
            return alert("로그인 정보가 틀렸습니다..", "/login")
        if not fc.guild_info(username)[1] == password:
            return alert("로그인 정보가 틀렸습니다.", "/login")
        session["id"] = username
        return redirect("/main")

@app.route("/main", methods=["GET", "POST"])
def main():
    if  not "id" in session:
        return redirect("/login")
    if request.method == "GET":
        guild_infos = fc.guild_info(session["id"])
        return render_template("main.html", guild_infos=guild_infos)
    else:
        form = request.form
        if not ("cultureid" in form and "culturepw" in form and "adminlog" in form and "buylog" in form):
            abort(400)
        con,cur = fc.start_db(session["id"])
        cur.execute("UPDATE configs SET cultureid = ?, culturepw = ?, buylog = ?, adminlog = ?;", (form["cultureid"], form["culturepw"], form["buylog"], form["adminlog"]))
        con.commit()
        con.close()
        return "ok"

@app.route("/users", methods=["GET"])
def users():
    if  not "id" in session:
        return redirect("/login")
    return render_template("users.html", users=fc.guild_users(session["id"]))

@app.route("/users/<userid>", methods=["GET", "POST"])
def user(userid):
    if  not "id" in session:
        return redirect("/login")
    if request.method == "GET":
        user_info = fc.guild_user(session["id"], userid)
        if user_info == None:
            abort(404)
        return render_template("user.html", user=user_info)
    else:
        user_info = fc.guild_user(session["id"], userid)
        if user_info == None:
            abort(404)
        form = request.form
        if not "balance" in form:
            abort(400)
        if not form["balance"].isdigit():
            return "잔액은 숫자로만 입력해주세요."
        if not (0 < int(form["balance"]) <= 10000000):
            return "잔액은 1000만원까지 입력 가능합니다."
        con,cur = fc.start_db(session["id"])
        cur.execute("UPDATE users SET balance = ? WHERE id == ?;", (form["balance"], userid))
        con.commit()
        con.close()
        return "ok"

@app.route("/products", methods=["GET", "POST"])
def products():
    if  not "id" in session:
        return redirect("/login")
    if request.method == "GET":
        return render_template("products.html", products=fc.guild_products(session["id"]))
    else:
        if len(fc.guild_products(session["id"])) >= 25:
            return "제품은 25개까지 생성 가능합니다."
        new_prod_id = str(uuid.uuid4())
        con,cur = fc.start_db(session["id"])
        cur.execute("INSERT INTO products VALUES(?, ?, ?, ?);", (new_prod_id, "없음", 0, ""))
        con.commit()
        con.close()
        return f"ok|{new_prod_id}"

@app.route("/products/<productid>", methods=["GET", "POST", "DELETE"])
def product(productid):
    if  not "id" in session:
        return redirect("/login")
    if request.method == "GET":
        product_info = fc.guild_product(session["id"], productid)
        if product_info == None:
            abort(404)
        return render_template("product.html", product=product_info)
    elif request.method == "POST":
        product_info = fc.guild_product(session["id"], productid)
        if product_info == None:
            abort(404)
        form = request.form
        if not "name" in form and "price" in form and "stocks" in form:
            abort(400)
        if not form["price"].isdigit():
            return "가격은 숫자로만 입력해주세요."
        if not (0 < int(form["price"]) <= 1000000):
            return "가격은 100만원까지 입력 가능합니다."
        if not (0 < len(form["name"]) <= 25):
            return "제품명은 1자 이상 25자 이하여야 합니다."
        con,cur = fc.start_db(session["id"])
        cur.execute("UPDATE products SET name = ?, price = ?, stocks = ? WHERE id == ?;", (form["name"], form["price"], form["stocks"], productid))
        con.commit()
        con.close()
        return "ok"
    else:
        con,cur = fc.start_db(session["id"])
        cur.execute("DELETE FROM products WHERE id == ?;", (productid,))
        con.commit()
        con.close()
        return "ok"

@app.route("/license", methods=["GET", "POST"])
def license():
    if  not "id" in session:
        return redirect("/login")
    if request.method == "GET":
        license_remaining = licensing.get_remaining_string(fc.guild_info(session["id"])[0]) if fc.is_guild_valid(session["id"])[1] == True else "0일 0시간 0분 [ 만료 ]"
        return render_template("license.html", license_remaining=license_remaining)
    else:
        form = request.form
        if not "license" in form:
            abort(400)
        con,cur = fc.start_db()
        cur.execute("SELECT * FROM keys WHERE key == ?;", (form["license"],))
        key_info = cur.fetchone()
        if key_info == None:
            con.close()
            return "존재하지 않는 코드입니다."
        cur.execute("DELETE FROM keys WHERE key == ?;", (form["license"],))
        con.commit()
        con.close()
        guild_info = fc.guild_info(session["id"])
        new_license_remaining = licensing.add_time(guild_info[0], key_info[1]) if licensing.is_expired(guild_info[0]) == False else licensing.make_new_expiringdate(key_info[1])
        con,cur = fc.start_db(session["id"])
        cur.execute("UPDATE configs SET expiringdate = ? ;", (new_license_remaining,))
        con.commit()
        con.close()
        return f"ok|{licensing.get_remaining_string(new_license_remaining)}"

@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.before_request
def before_request():
    session.permanent = True

app.run(debug=False, host="0.0.0.0", port=80)