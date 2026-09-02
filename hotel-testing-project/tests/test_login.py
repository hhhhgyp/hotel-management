"""
测试文件：登录功能 + 鉴权
====================================
演示两个核心概念：

1. 断言（expect）
   判断「实际结果」是否等于「预期结果」。这是测试的灵魂。

2. 等价类划分（测试用例设计方法）
   登录有两个输入（用户名、密码），每个输入都分「有效/无效」两类。
   我们不需要穷举所有组合，只需要从每一类里挑一个有代表性的值：
   - 有效类：admin / admin123 -> 成功
   - 无效类：错误密码、不存在的用户、空用户名、空密码
"""
import pytest
from playwright.sync_api import Page, expect


def test_login_success(page, base_url):
    """TC-01 正确的用户名和密码 -> 登录成功并跳转到房间管理页"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click("#login-btn")
    # 断言：URL 变成房间管理页
    expect(page).to_have_url(f"{base_url}/rooms")
    # 断言：页面上出现「房间管理」标题
    expect(page.locator("h1")).to_contain_text("房间管理")


def test_login_wrong_password(page, base_url):
    """TC-02 正确用户名 + 错误密码 -> 登录失败，页面提示错误"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "admin")
    page.fill("#password", "wrong-password")
    page.click("#login-btn")
    expect(page).to_have_url(f"{base_url}/login")  # 仍停留在登录页
    expect(page.locator("#error-msg")).to_contain_text("用户名或密码错误")


def test_login_unknown_user(page, base_url):
    """TC-03 不存在的用户名 -> 登录失败"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "nobody")
    page.fill("#password", "admin123")
    page.click("#login-btn")
    expect(page.locator("#error-msg")).to_contain_text("用户名或密码错误")


@pytest.mark.parametrize("username,password", [
    ("", "admin123"),   # 用户名为空
    ("admin", ""),      # 密码为空
    ("", ""),           # 都为空
])
def test_login_empty_fields(page, base_url, username, password):
    """TC-04/05/06 空用户名或空密码 -> 登录失败

    知识点：参数化 @pytest.mark.parametrize
        同一套测试逻辑，用多组数据分别跑一遍，避免复制粘贴。
        上面 3 组数据会生成 3 个独立的用例。
    """
    page.goto(f"{base_url}/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#login-btn")
    expect(page.locator("#error-msg")).to_contain_text("用户名或密码错误")


def test_requires_login(page, base_url):
    """TC-07 未登录直接访问 /rooms，应跳转到登录页（鉴权）"""
    page.goto(f"{base_url}/rooms")
    expect(page).to_have_url(f"{base_url}/login")
