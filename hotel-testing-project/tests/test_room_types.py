"""
测试文件：房型管理
====================================
核心知识点：边界值分析（Boundary Value Analysis）

以「价格」为例，合法范围是「大于 0 的整数」。测试重点看边界：
    - 下边界：0（非法）、1（合法）
    - 再补典型的异常输入：负数、超大值

📌 曾经埋过 1 个缺陷（用于演示「测试发现缺陷」），现已在回归阶段修复：
    test_room_type_price_boundary[0-...] 对应被测应用里的缺陷 BUG-01
    （价格校验用 `price < 0`，导致「价格 = 0」也能通过）。
    这个用例当前已通过，缺陷详情见 docs/04_缺陷报告.md。
"""
import pytest
from playwright.sync_api import expect


def _fill_valid_form(page):
    """往表单里填一组「合法」的数据（后面的用例在此基础上改某个字段）。"""
    page.fill("#name", "家庭房")
    page.fill("#price", "399")
    page.fill("#capacity", "3")


def test_room_type_add_success(logged_in_page, base_url):
    """TC-10 新增房型成功，列表出现该房型"""
    page = logged_in_page
    page.goto(f"{base_url}/room-types/new")
    _fill_valid_form(page)
    page.click("#save-btn")
    expect(page).to_have_url(f"{base_url}/room-types")
    expect(page.locator("#room-type-table")).to_contain_text("家庭房")


def test_room_type_name_required(logged_in_page, base_url):
    """TC-11 房型名称为空 -> 报错「房型名称不能为空」"""
    page = logged_in_page
    page.goto(f"{base_url}/room-types/new")
    _fill_valid_form(page)
    page.fill("#name", "")
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("房型名称不能为空")


@pytest.mark.parametrize("price,should_succeed,message", [
    ("1", True, None),                 # 下边界：合法
    ("0", False, "价格必须大于 0"),      # 下边界-1：非法
    ("-100", False, "价格必须大于 0"),   # 负数：非法
    ("999999", True, None),            # 大额：合法
])
def test_room_type_price_boundary(logged_in_page, base_url, price, should_succeed, message):
    """TC-12~15 价格的边界值测试"""
    page = logged_in_page
    page.goto(f"{base_url}/room-types/new")
    _fill_valid_form(page)
    page.fill("#price", price)
    page.click("#save-btn")
    if should_succeed:
        expect(page).to_have_url(f"{base_url}/room-types")
    else:
        expect(page.locator("#error-msg")).to_contain_text(message)


@pytest.mark.parametrize("capacity,message", [
    ("0", "可住人数必须在 1 到 10 之间"),   # 下边界-1：非法
    ("11", "可住人数必须在 1 到 10 之间"),  # 上边界+1：非法
    ("abc", "可住人数必须是数字"),          # 非数字：非法
])
def test_room_type_capacity_invalid(logged_in_page, base_url, capacity, message):
    """TC-16~18 可住人数的边界值 / 异常输入测试"""
    page = logged_in_page
    page.goto(f"{base_url}/room-types/new")
    _fill_valid_form(page)
    page.fill("#capacity", capacity)
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text(message)
