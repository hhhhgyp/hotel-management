"""
被测应用的数据层：用内存列表模拟数据库。

为什么用内存列表而不是数据库？
    1. 让项目容易跑起来（不用装 MySQL）
    2. UI 测试关注界面行为，数据存储方式不影响测试方法
    真实项目中，这里会换成数据库操作（SQLAlchemy 等）。
"""

# ============ 初始房型数据 ============
# 字段：id, name(名称), price(价格/元), capacity(可住人数)
_INITIAL_ROOM_TYPES = [
    {"id": 1, "name": "标准间", "price": 199, "capacity": 2},
    {"id": 2, "name": "大床房", "price": 299, "capacity": 2},
    {"id": 3, "name": "豪华套房", "price": 599, "capacity": 4},
]

# ============ 初始房间数据 ============
# 字段：id, number(房号), type(房型名), floor(楼层), status(状态)
# status 取值：空闲 / 已预订 / 已入住 / 维修中
_INITIAL_ROOMS = [
    {"id": 1, "number": "101", "type": "标准间", "floor": 1, "status": "空闲"},
    {"id": 2, "number": "102", "type": "标准间", "floor": 1, "status": "已入住"},
    {"id": 3, "number": "201", "type": "大床房", "floor": 2, "status": "空闲"},
    {"id": 4, "number": "202", "type": "大床房", "floor": 2, "status": "已预订"},
    {"id": 5, "number": "301", "type": "豪华套房", "floor": 3, "status": "空闲"},
    {"id": 6, "number": "302", "type": "豪华套房", "floor": 3, "status": "维修中"},
]

# ============ 初始预订数据 ============
# 字段：id, guest_name(客人姓名), phone(手机号), id_card(身份证),
#       checkin(入住日期), checkout(退房日期), room_number(房号), status(状态)
_INITIAL_BOOKINGS = [
    {
        "id": 1, "guest_name": "张三", "phone": "13800138000",
        "id_card": "110101199001011234",
        "checkin": "2026-09-10", "checkout": "2026-09-12",
        "room_number": "202", "status": "已预订",
    },
]

# ============ 当前数据（运行中会被增删改） ============
ROOM_TYPES = [dict(t) for t in _INITIAL_ROOM_TYPES]
ROOMS = [dict(r) for r in _INITIAL_ROOMS]
BOOKINGS = [dict(b) for b in _INITIAL_BOOKINGS]


def reset_all():
    """把数据恢复到初始状态。

    测试里每个用例前都会调用它，保证用例之间互不影响（隔离性）。
    用切片赋值 [:] = 原地更新，让所有引用这些列表的地方都能看到变化。
    """
    ROOM_TYPES[:] = [dict(t) for t in _INITIAL_ROOM_TYPES]
    ROOMS[:] = [dict(r) for r in _INITIAL_ROOMS]
    BOOKINGS[:] = [dict(b) for b in _INITIAL_BOOKINGS]
