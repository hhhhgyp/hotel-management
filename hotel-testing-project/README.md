# 酒店管理系统自动化测试项目（UI + 接口）

一个走完**完整软件测试流程**的练手项目，可直接写进软件测试实习简历。

- **被测对象（SUT）**：用 Flask 写的「酒店管理系统」（登录、房型、房间、预订、筛选）。
- **测试技术栈**：Python + pytest + Playwright（UI 自动化）+ requests（接口自动化）。
- **交付物**：需求说明、测试计划、用例设计、缺陷报告、测试报告，以及 UI + 接口两套自动化脚本（共 56 条用例）。

## 一、这个项目为什么好

1. **不是烂大街的电商系统**，有酒店行业特有的业务规则（日期、手机号、身份证、房间冲突、状态流转），能设计出「有料」的测试用例。
2. **走完了完整测试流程**，六份交付物对应测试工程师的真实工作：
   ```
   ① 需求分析 → ② 测试计划 → ③ 用例设计 → ④ 自动化执行 → ⑤ 缺陷管理 → ⑥ 测试报告
   ```
3. **真实走完「发现缺陷 → 修复 → 回归」闭环**：被测应用曾故意埋 5 个缺陷，首轮测试跑出 5 条失败，定位根因并修复后回归全绿。全过程记录在 `04_缺陷报告.md` / `05_测试报告.md`。
4. **全本地运行**，不依赖外部网站，稳定、可复现、可演示给面试官看。

## 二、目录结构

```
hotel-testing-project/
├── conftest.py                # 让 pytest 能找到被测应用（空文件）
├── app/                       # 被测应用（Flask 后端）
│   ├── __init__.py
│   ├── app.py                 # 路由 + 业务逻辑（含埋的 5 个缺陷）
│   ├── data.py                # 内存数据（模拟数据库）
│   ├── templates/             # 页面模板
│   └── static/style.css       # 样式
├── tests/                     # 自动化测试（重点看这里）
│   ├── conftest.py            # fixture：启动服务器、登录、重置数据
│   ├── test_login.py          # 登录/鉴权（7 条）
│   ├── test_room_types.py     # 房型（9 条）
│   ├── test_rooms.py          # 房间（7 条）
│   ├── test_bookings.py       # 预订（15 条）
│   ├── test_search_filter.py  # 搜索筛选（5 条）
│   └── test_api.py            # 接口测试（13 条，requests）
├── docs/                      # 测试流程文档（完整交付物）
│   ├── 01_需求说明.md
│   ├── 02_测试计划.md
│   ├── 03_测试用例.md
│   ├── 04_缺陷报告.md
│   ├── 05_测试报告.md
│   └── 06_接口测试说明.md
├── requirements.txt
├── pytest.ini
└── README.md
```

## 三、环境准备（Windows）

1. 确认 Python 3.9+：
   ```
   python --version
   ```
2. 在项目目录下创建虚拟环境（推荐，隔离依赖）：
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
4. 安装 Playwright 浏览器（约 150MB，只需一次）：
   ```
   playwright install chromium
   ```

## 四、运行测试

在项目根目录执行：

```
python -m pytest
```

**运行结果预期**：`56 passed`（43 条 UI 用例 + 13 条接口用例，全部通过）。

> 想看「测试怎么找 bug」？项目曾在被测应用里故意埋 5 个缺陷，首轮跑出 5 条失败，定位修复后回归才变全绿——完整过程见 `docs/04_缺陷报告.md`、`docs/05_测试报告.md`。

只跑某个文件 / 用例：

```
python -m pytest tests/test_login.py
python -m pytest tests/test_bookings.py::test_booking_phone
```

## 五、生成 HTML 测试报告

```
python -m pytest --html=report.html --self-contained-html
```

运行后在项目根目录生成 `report.html`，浏览器打开即可看到每个用例的通过/失败情况。

## 六、手动打开被测应用（可选）

```
python -m app.app
```

浏览器访问 http://127.0.0.1:5000 （用户名 `admin` / 密码 `admin123`）。
注意：手动打开会占用 5000 端口，运行测试前先关掉。

## 七、简历怎么写（示例）

> **项目：酒店管理系统 UI 自动化测试**（Python / pytest / Playwright）
> - 独立完成酒店管理系统的完整测试流程，输出需求说明、测试计划、43 条测试用例、缺陷报告、测试报告六类文档。
> - 使用等价类划分、边界值分析设计用例，覆盖登录、房型、房间、预订、搜索筛选 5 大模块。
> - 基于 pytest + Playwright 搭建 UI 自动化测试框架，实现 fixture 复用、参数化、测试数据隔离，用例自动执行并输出 HTML 报告。
> - 补充 pytest + requests 接口自动化测试，绕开浏览器直接验证后端接口的状态码、重定向与校验逻辑，形成 UI + 接口两层测试体系。
> - 通过测试发现并定位 5 个缺陷（含 2 个 P1 严重缺陷），撰写缺陷报告并给出修复建议，修复后回归测试全绿。

**面试可能会问的点（提前准备）**：
- 等价类和边界值分别是什么？各举个例子。
- fixture 的作用？为什么每个用例前要重置数据？
- Playwright 相比 Selenium 有什么优势？（自动等待、更稳定、内置 expect）
- 接口测试和 UI 测试的区别？测试金字塔是什么？
- 你是如何定位缺陷根因的？修复后怎么验证？（回归测试）

## 八、学习地图（每个文件讲了什么）

| 文件 | 你学到的东西 |
|------|-------------|
| `docs/01_需求说明.md` | 如何把需求拆成可测试的规则 |
| `docs/02_测试计划.md` | 测什么、怎么测、何时算通过 |
| `docs/03_测试用例.md` | 等价类、边界值、优先级、用例写法 |
| `tests/test_login.py` | 断言 `expect`、参数化 `@pytest.mark.parametrize` |
| `tests/test_room_types.py` | 边界值分析 |
| `tests/test_bookings.py` | 场景测试、状态流转、冲突校验 |
| `tests/conftest.py` | fixture、测试隔离、服务器启动 |
| `tests/test_api.py` | requests 接口测试、Session 保持登录、状态码断言 |
| `docs/04_缺陷报告.md` | 缺陷的字段、严重程度、复现步骤、根因 |
| `docs/05_测试报告.md` | 测试统计、结论、遗留问题 |
| `docs/06_接口测试说明.md` | 测试金字塔、接口 vs UI 测试 |

## 九、如何继续深入（加分项）

1. ~~修复缺陷 + 回归~~ ✅ 已完成（见 `04_缺陷报告.md` / `05_测试报告.md`）
2. ~~加接口测试~~ ✅ 已完成（见 `tests/test_api.py` / `06_接口测试说明.md`）
3. **接入 GitHub Actions**：push 自动跑测试（CI），非常加分。
4. **加 Allure 报告**：比 HTML 报告更漂亮，更适合面试展示。
5. **加数据驱动**：把测试数据放到 JSON/CSV，用 pytest 读取。

## 十、常见问题

- **报 `Connection refused`**：服务器没起来，重跑一次；或 5000 端口被占用（关掉手动打开的 app）。
- **报浏览器没找到**：忘了执行 `playwright install chromium`。
- **中文乱码**：确保文件是 UTF-8 编码（项目文件已全部是 UTF-8）。
