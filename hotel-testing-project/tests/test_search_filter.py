"""
测试文件：房间搜索与筛选
====================================
覆盖的测试点：
    1. 按房号搜索（有结果 / 无结果）
    2. 按状态筛选
    3. 按房型筛选

📌 曾经埋过 1 个缺陷（用于演示「测试发现缺陷」），现已在回归阶段修复：
    test_filter_status_repair 对应被测应用里的缺陷 BUG-05
    （按「维修中」筛选时，筛选逻辑漏掉了这个状态，返回了全部房间）。
    这个用例当前已通过，缺陷详情见 docs/04_缺陷报告.md。
"""
from playwright.sync_api import expect


def test_search_room_number(logged_in_page, base_url):
    """TC-50 按房号搜索：只显示匹配的房间"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms")
    page.fill("#q", "201")
    page.click("#search-btn")
    # expect 会自动等待，直到断言满足或超时
    expect(page.locator("#room-table")).to_contain_text("201")
    expect(page.locator("#room-table")).not_to_contain_text("101")


def test_search_room_no_result(logged_in_page, base_url):
    """TC-51 搜索不存在的房号：显示「暂无房间」"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms")
    page.fill("#q", "999")
    page.click("#search-btn")
    expect(page.locator(".empty")).to_be_visible()
    expect(page.locator(".empty")).to_contain_text("暂无房间")


def test_filter_status_free(logged_in_page, base_url):
    """TC-52 按「空闲」筛选：只显示空闲房间（101、201、301 共 3 间）"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms")
    page.select_option("#status", "空闲")
    page.click("#search-btn")
    expect(page.locator("#room-table tbody tr")).to_have_count(3)
    texts = page.locator(".room-status").all_inner_texts()
    assert texts == ["空闲", "空闲", "空闲"]


def test_filter_status_repair(logged_in_page, base_url):
    """TC-53 按「维修中」筛选：应只显示 302 一间"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms")
    page.select_option("#status", "维修中")
    page.click("#search-btn")
    expect(page.locator("#room-table tbody tr")).to_have_count(1)
    expect(page.locator("#room-table")).to_contain_text("302")


def test_filter_by_type(logged_in_page, base_url):
    """TC-54 按「豪华套房」筛选：只显示 301、302 两间"""
    page = logged_in_page
    page.goto(f"{base_url}/rooms")
    page.select_option("#type", "豪华套房")
    page.click("#search-btn")
    expect(page.locator("#room-table tbody tr")).to_have_count(2)
    expect(page.locator("#room-table")).to_contain_text("301")
    expect(page.locator("#room-table")).to_contain_text("302")
