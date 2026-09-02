"""
测试文件：预订管理（核心业务）
====================================
覆盖的测试点：
    1. 预订成功 + 房间状态流转（空闲 -> 已预订）
    2. 退房 + 房间状态流转（已预订 -> 空闲）
    3. 客人姓名必填
    4. 手机号格式（等价类 + 边界值）
    5. 身份证格式（边界值）
    6. 日期范围（边界值）
    7. 房间冲突（已入住/已预订房间不能预订）

📌 曾经埋过 3 个缺陷（用于演示「测试发现缺陷」），现已在回归阶段全部修复：
    - test_booking_phone[01111111111-...]  -> BUG-03（手机号漏检「1 开头」）
    - test_booking_id_card[18位全字母-...] -> BUG-04（身份证只查长度不查格式）
    - test_booking_same_day_checkout        -> BUG-02（入住=退房当天退房被放行）
    这些用例当前全部通过，缺陷详情与修复记录见 docs/04_缺陷报告.md。
"""
import pytest
from playwright.sync_api import expect


def _fill_valid_booking(page, room_number="101"):
    """填一组合法的预订数据。"""
    page.fill("#guest_name", "李四")
    page.fill("#phone", "13900139000")
    page.fill("#id_card", "110101199505051234")
    page.fill("#checkin", "2026-09-20")
    page.fill("#checkout", "2026-09-22")
    page.select_option("#room_number", room_number)


def test_booking_success(logged_in_page, base_url):
    """TC-30 预订成功：订单出现，且房间 101 状态从「空闲」变「已预订」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page, room_number="101")
    page.click("#save-btn")
    expect(page).to_have_url(f"{base_url}/bookings")
    expect(page.locator("#booking-table")).to_contain_text("李四")
    # 回到房间列表，检查 101 的状态流转
    page.goto(f"{base_url}/rooms")
    row = page.locator("#room-table tbody tr", has_text="101")
    expect(row.locator(".room-status")).to_contain_text("已预订")


def test_booking_checkout(logged_in_page, base_url):
    """TC-31 退房：订单变「已退房」，房间 202 状态变回「空闲」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings")
    # 初始数据里有一条预订：张三订了 202
    row = page.locator("#booking-table tbody tr", has_text="张三")
    row.locator(".checkout-btn").click()
    expect(page).to_have_url(f"{base_url}/bookings")
    expect(page.locator("#booking-table")).to_contain_text("已退房")
    # 房间 202 变回空闲
    page.goto(f"{base_url}/rooms")
    room_row = page.locator("#room-table tbody tr", has_text="202")
    expect(room_row.locator(".room-status")).to_contain_text("空闲")


def test_booking_guest_name_required(logged_in_page, base_url):
    """TC-32 客人姓名为空 -> 报错「客人姓名不能为空」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page)
    page.fill("#guest_name", "")
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("客人姓名不能为空")


@pytest.mark.parametrize("phone,should_succeed", [
    ("13900139000", True),     # 1 开头 11 位：合法
    ("1390013900", False),     # 10 位：非法
    ("139001390000", False),   # 12 位：非法
    ("01111111111", False),    # 0 开头：非法
    ("abcdefghijk", False),    # 非数字：非法
])
def test_booking_phone(logged_in_page, base_url, phone, should_succeed):
    """TC-33~37 手机号格式的等价类 / 边界值测试"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page)
    page.fill("#phone", phone)
    page.click("#save-btn")
    if should_succeed:
        expect(page).to_have_url(f"{base_url}/bookings")
    else:
        expect(page.locator("#error-msg")).to_contain_text("手机号格式不正确")


@pytest.mark.parametrize("id_card,should_succeed", [
    ("110101199505051234", True),   # 18 位合法（前17数字+末位数字）
    ("11010119950505123", False),   # 17 位：非法
    ("ABCDEFGHIJKLMNOPQR", False),  # 18 位全字母：非法
])
def test_booking_id_card(logged_in_page, base_url, id_card, should_succeed):
    """TC-38~40 身份证格式的边界值测试"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page)
    page.fill("#id_card", id_card)
    page.click("#save-btn")
    if should_succeed:
        expect(page).to_have_url(f"{base_url}/bookings")
    else:
        expect(page.locator("#error-msg")).to_contain_text("身份证号格式不正确")


def test_booking_same_day_checkout(logged_in_page, base_url):
    """TC-41 入住日期 = 退房日期 -> 应报错「退房日期必须晚于入住日期」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page)
    page.fill("#checkin", "2026-09-20")
    page.fill("#checkout", "2026-09-20")  # 同一天
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("退房日期必须晚于入住日期")


def test_booking_checkout_before_checkin(logged_in_page, base_url):
    """TC-42 退房日期早于入住日期 -> 报错「退房日期必须晚于入住日期」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page)
    page.fill("#checkin", "2026-09-22")
    page.fill("#checkout", "2026-09-20")  # 退房早于入住
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("退房日期必须晚于入住日期")


def test_booking_occupied_room(logged_in_page, base_url):
    """TC-43 预订已入住房间 102 -> 报错「该房间当前不可预订」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page, room_number="102")  # 102 是「已入住」
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("该房间当前不可预订")


def test_booking_reserved_room(logged_in_page, base_url):
    """TC-44 预订已预订房间 202 -> 报错「该房间当前不可预订」"""
    page = logged_in_page
    page.goto(f"{base_url}/bookings/new")
    _fill_valid_booking(page, room_number="202")  # 202 是「已预订」
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("该房间当前不可预订")
