"""
被测应用（System Under Test）—— 酒店管理系统

一个用 Flask 写的酒店管理后台，包含：
    - 登录 / 退出
    - 房型管理（新增、列表、删除）
    - 房间管理（新增、编辑、删除、搜索、按状态/房型筛选）
    - 预订管理（新增预订、退房）
    - 表单校验（必填、价格、手机号、身份证、日期、房间冲突）

（说明：本项目曾故意埋入 5 个缺陷用于演示「测试发现缺陷」的流程，
  现已在回归阶段全部修复，缺陷详情与修复记录见 docs/04_缺陷报告.md。）
"""
import re
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort,
)

from . import data

app = Flask(__name__)
app.secret_key = "hotel-secret-key-123"  # 用于加密 session，生产环境要改成随机值

# 简单用户表（模拟）
USERS = {"admin": "admin123"}

# 房间状态枚举
VALID_ROOM_STATUS = ["空闲", "已预订", "已入住", "维修中"]


def login_required(view):
    """装饰器：要求登录后才能访问，未登录跳转到登录页。"""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


# ================= 登录 / 退出 =================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if USERS.get(username) == password:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("rooms"))
        error = "用户名或密码错误"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return redirect(url_for("rooms"))


# ================= 房型管理 =================

@app.route("/room-types")
@login_required
def room_types():
    return render_template("room_types.html", room_types=data.ROOM_TYPES)


@app.route("/room-types/new", methods=["GET", "POST"])
@login_required
def room_type_new():
    if request.method == "POST":
        ok, err = _validate_room_type(request.form)
        if ok:
            new_id = max((t["id"] for t in data.ROOM_TYPES), default=0) + 1
            data.ROOM_TYPES.append({
                "id": new_id,
                "name": request.form.get("name", "").strip(),
                "price": int(request.form.get("price", "0")),
                "capacity": int(request.form.get("capacity", "0")),
            })
            flash("房型添加成功", "success")
            return redirect(url_for("room_types"))
        return render_template("room_type_form.html", title="添加房型", form=request.form, error=err)
    return render_template("room_type_form.html", title="添加房型", form=None, error=None)


@app.route("/room-types/<int:type_id>/delete", methods=["POST"])
@login_required
def room_type_delete(type_id):
    for i, t in enumerate(data.ROOM_TYPES):
        if t["id"] == type_id:
            data.ROOM_TYPES.pop(i)
            break
    flash("房型删除成功", "success")
    return redirect(url_for("room_types"))


def _validate_room_type(form):
    """房型表单校验，返回 (是否合法, 错误信息)。"""
    name = form.get("name", "").strip()
    price_raw = form.get("price", "").strip()
    capacity_raw = form.get("capacity", "").strip()

    if not name:
        return False, "房型名称不能为空"
    if not price_raw:
        return False, "价格不能为空"
    try:
        price = int(price_raw)
    except ValueError:
        return False, "价格必须是数字"
    # 价格必须大于 0
    if price <= 0:
        return False, "价格必须大于 0"
    if not capacity_raw:
        return False, "可住人数不能为空"
    try:
        capacity = int(capacity_raw)
    except ValueError:
        return False, "可住人数必须是数字"
    if capacity < 1 or capacity > 10:
        return False, "可住人数必须在 1 到 10 之间"
    return True, ""


# ================= 房间管理 =================

@app.route("/rooms")
@login_required
def rooms():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    type_ = request.args.get("type", "").strip()
    room_list = data.ROOMS
    if q:
        room_list = [r for r in room_list if q in r["number"]]
    # 按状态筛选（覆盖全部 4 种状态）
    if status in VALID_ROOM_STATUS:
        room_list = [r for r in room_list if r["status"] == status]
    if type_:
        room_list = [r for r in room_list if r["type"] == type_]
    room_types = [t["name"] for t in data.ROOM_TYPES]
    return render_template(
        "rooms.html", rooms=room_list, q=q, status=status, type=type_,
        room_types=room_types, all_statuses=VALID_ROOM_STATUS,
    )


@app.route("/rooms/new", methods=["GET", "POST"])
@login_required
def room_new():
    if request.method == "POST":
        ok, err = _validate_room(request.form)
        if ok:
            new_id = max((r["id"] for r in data.ROOMS), default=0) + 1
            data.ROOMS.append({
                "id": new_id,
                "number": request.form.get("number", "").strip(),
                "type": request.form.get("type", ""),
                "floor": int(request.form.get("floor", "0")),
                "status": "空闲",
            })
            flash("房间添加成功", "success")
            return redirect(url_for("rooms"))
        return render_template("room_form.html", title="添加房间", form=request.form,
                               error=err, room_types=_type_names())
    return render_template("room_form.html", title="添加房间", form=None,
                           error=None, room_types=_type_names())


@app.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
@login_required
def room_edit(room_id):
    room = next((r for r in data.ROOMS if r["id"] == room_id), None)
    if room is None:
        abort(404)
    if request.method == "POST":
        ok, err = _validate_room(request.form, exclude_id=room_id)
        if ok:
            room["number"] = request.form.get("number", "").strip()
            room["type"] = request.form.get("type", "")
            room["floor"] = int(request.form.get("floor", "0"))
            flash("房间更新成功", "success")
            return redirect(url_for("rooms"))
        return render_template("room_form.html", title="编辑房间", form=request.form,
                               error=err, room_types=_type_names())
    return render_template("room_form.html", title="编辑房间", form=room,
                           error=None, room_types=_type_names())


@app.route("/rooms/<int:room_id>/delete", methods=["POST"])
@login_required
def room_delete(room_id):
    for i, r in enumerate(data.ROOMS):
        if r["id"] == room_id:
            data.ROOMS.pop(i)
            break
    flash("房间删除成功", "success")
    return redirect(url_for("rooms"))


def _validate_room(form, exclude_id=None):
    """房间表单校验，返回 (是否合法, 错误信息)。"""
    number = form.get("number", "").strip()
    type_ = form.get("type", "").strip()
    floor_raw = form.get("floor", "").strip()

    if not number:
        return False, "房号不能为空"
    # 房号唯一性校验（编辑时排除自己）
    for r in data.ROOMS:
        if r["number"] == number and r["id"] != exclude_id:
            return False, "房号已存在"
    if type_ not in _type_names():
        return False, "请选择合法的房型"
    if not floor_raw:
        return False, "楼层不能为空"
    try:
        floor = int(floor_raw)
    except ValueError:
        return False, "楼层必须是数字"
    if floor < 1 or floor > 30:
        return False, "楼层必须在 1 到 30 之间"
    return True, ""


# ================= 预订管理 =================

@app.route("/bookings")
@login_required
def bookings():
    return render_template("bookings.html", bookings=data.BOOKINGS)


@app.route("/bookings/new", methods=["GET", "POST"])
@login_required
def booking_new():
    if request.method == "POST":
        ok, err = _validate_booking(request.form)
        if ok:
            new_id = max((b["id"] for b in data.BOOKINGS), default=0) + 1
            room_number = request.form.get("room_number", "")
            data.BOOKINGS.append({
                "id": new_id,
                "guest_name": request.form.get("guest_name", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "id_card": request.form.get("id_card", "").strip(),
                "checkin": request.form.get("checkin", "").strip(),
                "checkout": request.form.get("checkout", "").strip(),
                "room_number": room_number,
                "status": "已预订",
            })
            # 预订成功后，房间状态从「空闲」变为「已预订」
            _set_room_status(room_number, "已预订")
            flash("预订成功", "success")
            return redirect(url_for("bookings"))
        return render_template("booking_form.html", form=request.form, error=err,
                               rooms=data.ROOMS)
    return render_template("booking_form.html", form=None, error=None,
                           rooms=data.ROOMS)


@app.route("/bookings/<int:booking_id>/checkout", methods=["POST"])
@login_required
def booking_checkout(booking_id):
    """退房：预订状态变为「已退房」，房间状态变为「空闲」。"""
    for b in data.BOOKINGS:
        if b["id"] == booking_id and b["status"] != "已退房":
            b["status"] = "已退房"
            _set_room_status(b["room_number"], "空闲")
            break
    flash("退房成功", "success")
    return redirect(url_for("bookings"))


def _validate_booking(form):
    """预订表单校验，返回 (是否合法, 错误信息)。"""
    guest_name = form.get("guest_name", "").strip()
    phone = form.get("phone", "").strip()
    id_card = form.get("id_card", "").strip()
    checkin = form.get("checkin", "").strip()
    checkout = form.get("checkout", "").strip()
    room_number = form.get("room_number", "").strip()

    if not guest_name:
        return False, "客人姓名不能为空"
    if not phone:
        return False, "手机号不能为空"
    # 手机号：11 位数字且以 1 开头
    if not re.match(r"^1\d{10}$", phone):
        return False, "手机号格式不正确"
    if not id_card:
        return False, "身份证号不能为空"
    # 身份证号：18 位，前 17 位数字，末位数字或 X
    if not re.match(r"^\d{17}[\dXx]$", id_card):
        return False, "身份证号格式不正确"
    if not checkin or not checkout:
        return False, "请选择入住和退房日期"
    # 退房日期必须晚于入住日期（至少住一晚）
    if checkout <= checkin:
        return False, "退房日期必须晚于入住日期"
    room = _find_room(room_number)
    if room is None:
        return False, "请选择有效的房间"
    if room["status"] != "空闲":
        return False, "该房间当前不可预订"
    return True, ""


# ================= 内部工具函数 =================

def _type_names():
    """所有房型的名称列表（用于下拉框和校验）。"""
    return [t["name"] for t in data.ROOM_TYPES]


def _find_room(number):
    """按房号查找房间，找不到返回 None。"""
    return next((r for r in data.ROOMS if r["number"] == number), None)


def _set_room_status(number, status):
    """修改指定房号的房间状态。"""
    room = _find_room(number)
    if room:
        room["status"] = status


if __name__ == "__main__":
    # 手动运行：在项目根目录执行 python -m app.app
    app.run(host="127.0.0.1", port=5000, debug=True)
