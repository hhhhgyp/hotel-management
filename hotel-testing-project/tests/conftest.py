"""
conftest.py —— pytest 的公共配置与「夹具（fixture）」

pytest 会自动加载本文件，里面定义的 fixture 供所有测试用例使用。

什么是 fixture？
    测试前后的「准备与清理」工作。例如：
    - 启动被测应用（服务器）
    - 打开浏览器（由 pytest-playwright 提供 page）
    - 每个用例前重置数据
    把重复劳动抽出来放到 fixture，用例里用「参数名」直接取用，不用自己写。
"""
import socket
import threading
import time

import pytest

from app.app import app as flask_app
from app import data


@pytest.fixture(scope="session")
def base_url():
    """被测应用的根地址（session 级：整个测试过程只算一次）。"""
    return "http://127.0.0.1:5000"


def _wait_for_server(host, port, timeout=10):
    """轮询等待服务器就绪（比固定 sleep 更可靠）。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f"服务器在 {timeout} 秒内没有启动成功")


@pytest.fixture(scope="session", autouse=True)
def live_server(base_url):
    """在后台线程启动 Flask 应用，测试结束后自动关闭。

    scope="session"：整个测试过程只启动一次服务器（省时间）。
    autouse=True：不需要在用例里显式声明，自动对所有用例生效。
    """
    host, port = "127.0.0.1", 5000
    server = threading.Thread(
        target=flask_app.run,
        kwargs={"host": host, "port": port, "use_reloader": False, "threaded": True},
        daemon=True,
    )
    server.start()
    _wait_for_server(host, port)
    yield base_url
    # 服务器运行在 daemon 线程里，会随 pytest 进程退出自动结束，无需手动关闭


@pytest.fixture(autouse=True)
def reset_data():
    """每个测试用例前重置数据，保证用例之间互不影响（隔离性）。

    autouse=True：对所有用例自动生效。
    「测试独立性」很重要：用例 A 新增/删除的数据，绝不能影响用例 B 的结果。
    """
    data.reset_all()
    yield


@pytest.fixture
def logged_in_page(page, base_url):
    """返回一个「已经登录」的页面对象，省得每个用例重复写登录步骤。"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click("#login-btn")
    page.wait_for_url(f"{base_url}/rooms")
    return page
