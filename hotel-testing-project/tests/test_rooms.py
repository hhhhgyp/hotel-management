"""
测试文件：房间管理
====================================
覆盖的测试点：
    1. 新增房间成功
    2. 房号必填
    3. 房号唯一性（重复报错）
    4. 楼层边界值（1~30）
    5. 编辑房间
"""
import pytest
from playwright.sync_api import expect


def _fill_valid_room(page, number="808"):
    """填一组合法的房间数据。"""
    page.fill("#number", number)
    page.select_option("#type", "标准间")
    page.fill("#floor", "5")


def test_room_add_success(logged_in_page, base_url):
    """TC-20 新增房间成功，列表出现该房间"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms/new")
    _fill_valid_room(page, number="808")
    page.click("#save-btn")
    expect(page).to_have_url(f"{base_url}/rooms")
    expect(page.locator("#room-table")).to_contain_text("808")


def test_room_number_required(logged_in_page, base_url):
    """TC-21 房号为空 -> 报错「房号不能为空」"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms/new")
    _fill_valid_room(page)
    page.fill("#number", "")
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("房号不能为空")


def test_room_number_duplicate(logged_in_page, base_url):
    """TC-22 房号重复 -> 报错「房号已存在」"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms/new")
    _fill_valid_room(page, number="101")  # 101 已存在
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text("房号已存在")


@pytest.mark.parametrize("floor,message", [
    ("0", "楼层必须在 1 到 30 之间"),   # 下边界-1：非法
    ("31", "楼层必须在 1 到 30 之间"),  # 上边界+1：非法
    ("abc", "楼层必须是数字"),          # 非数字：非法
])
def test_room_floor_invalid(logged_in_page, base_url, floor, message):
    """TC-23~25 楼层的边界值 / 异常输入测试"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms/new")
    _fill_valid_room(page)
    page.fill("#floor", floor)
    page.click("#save-btn")
    expect(page.locator("#error-msg")).to_contain_text(message)


def test_room_edit(logged_in_page, base_url):
    """TC-26 编辑房间：修改房号后列表更新"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms")
    first_row = page.locator("#room-table tbody tr").first
    first_row.locator("a", has_text="编辑").click()
    page.fill("#number", "101A")  # 改房号
    page.click("#save-btn")
    expect(page).to_have_url(f"{base_url}/rooms")
    expect(page.locator("#room-table")).to_contain_text("101A")
