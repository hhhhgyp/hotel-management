"""
测试文件：接口测试（HTTP 层）
====================================
和 UI 测试（test_*.py，用 Playwright 开浏览器）的区别：

    UI 测试   —— 模拟真实用户：打开浏览器 → 点按钮 → 看页面
    接口测试  —— 绕过浏览器，用 requests 直接向服务器发 HTTP 请求，
                 检查「状态码 / 重定向 / 返回内容」，更快、更稳定。

为什么两层都要？
    UI 测试测的是「界面长什么样、能不能点」；
    接口测试测的是「后端逻辑对不对、接口契约对不对」。
    接口测试比 UI 测试快一个数量级，是「测试金字塔」里数量最多的那一层。

本文件用 requests.Session 保持登录 Cookie，直接测后端的增删改查与校验逻辑。
"""
import requests
import pytest


@pytest.fixture
def api_client(base_url):
    """返回一个「已登录」的 requests.Session（自动保存登录 Cookie）。

    等价于 UI 测试里的 logged_in_page：把「登录」这个重复步骤抽出来。
    """
    s = requests.Session()
    resp = s.post(
        f"{base_url}/login",
        data={"username": "admin", "password": "admin123"},
        allow_redirects=False,
    )
    assert resp.status_code == 302, "登录应重定向"
    assert resp.headers["Location"].endswith("/rooms"), "登录后应跳转到房间列表"
    return s


def _booking_payload(**overrides):
    """一组「合法」的预订数据，后面用例用 overrides 改掉某个字段。"""
    data = {
        "guest_name": "王五",
        "phone": "13800138000",
        "id_card": "110101199001011234",
        "checkin": "2026-09-20",
        "checkout": "2026-09-22",
        "room_number": "101",
    }
    data.update(overrides)
    return data


# ================= 登录 / 鉴权 =================

def test_api_login_success(base_url):
    """正确账号密码 -> 302 重定向到 /rooms"""
    s = requests.Session()
    r = s.post(
        f"{base_url}/login",
        data={"username": "admin", "password": "admin123"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/rooms")


def test_api_login_wrong_password(base_url):
    """错误密码 -> 200（留在登录页）且提示「用户名或密码错误」"""
    r = requests.post(
        f"{base_url}/login",
        data={"username": "admin", "password": "wrong"},
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "用户名或密码错误" in r.text


def test_api_requires_login(base_url):
    """未登录访问受保护页面 -> 302 重定向到 /login"""
    r = requests.get(f"{base_url}/rooms", allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/login")


# ================= 房型管理 =================

def test_api_room_type_create_success(api_client, base_url):
    """合法房型 -> 302 重定向，且列表页出现新房型"""
    r = api_client.post(
        f"{base_url}/room-types/new",
        data={"name": "接口测试房型", "price": "299", "capacity": "2"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/room-types")
    assert "接口测试房型" in api_client.get(f"{base_url}/room-types").text


def test_api_room_type_price_zero_rejected(api_client, base_url):
    """价格 = 0 -> 200（留在表单页）且提示「价格必须大于 0」"""
    r = api_client.post(
        f"{base_url}/room-types/new",
        data={"name": "免费房", "price": "0", "capacity": "2"},
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "价格必须大于 0" in r.text


# ================= 房间管理 =================

def test_api_room_create_success(api_client, base_url):
    """合法房间 -> 302 重定向"""
    r = api_client.post(
        f"{base_url}/rooms/new",
        data={"number": "999", "type": "标准间", "floor": "9"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/rooms")


def test_api_room_duplicate_rejected(api_client, base_url):
    """房号重复（101 已存在）-> 200 且提示「房号已存在」"""
    r = api_client.post(
        f"{base_url}/rooms/new",
        data={"number": "101", "type": "标准间", "floor": "1"},
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "房号已存在" in r.text


def test_api_room_floor_invalid(api_client, base_url):
    """楼层 = 0（越界）-> 200 且提示「楼层必须在 1 到 30 之间」"""
    r = api_client.post(
        f"{base_url}/rooms/new",
        data={"number": "888", "type": "标准间", "floor": "0"},
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "楼层必须在 1 到 30 之间" in r.text


# ================= 预订管理 =================

def test_api_booking_success(api_client, base_url):
    """合法预订 -> 302，且房间 101 状态从「空闲」变「已预订」"""
    r = api_client.post(
        f"{base_url}/bookings/new",
        data=_booking_payload(),
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/bookings")
    assert "已预订" in api_client.get(f"{base_url}/rooms").text


def test_api_booking_phone_invalid(api_client, base_url):
    """手机号 0 开头 -> 200 且提示「手机号格式不正确」"""
    r = api_client.post(
        f"{base_url}/bookings/new",
        data=_booking_payload(phone="01111111111"),
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "手机号格式不正确" in r.text


def test_api_booking_same_day_checkout(api_client, base_url):
    """入住 = 退房（当天退房）-> 200 且提示「退房日期必须晚于入住日期」"""
    r = api_client.post(
        f"{base_url}/bookings/new",
        data=_booking_payload(checkin="2026-09-20", checkout="2026-09-20"),
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "退房日期必须晚于入住日期" in r.text


def test_api_booking_occupied_room(api_client, base_url):
    """预订已入住房间 102 -> 200 且提示「该房间当前不可预订」"""
    r = api_client.post(
        f"{base_url}/bookings/new",
        data=_booking_payload(room_number="102"),
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "该房间当前不可预订" in r.text


# ================= 退房 =================

def test_api_checkout(api_client, base_url):
    """对初始预订（张三 / 202）退房 -> 302，订单变「已退房」"""
    r = api_client.post(
        f"{base_url}/bookings/1/checkout",
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert "已退房" in api_client.get(f"{base_url}/bookings").text
