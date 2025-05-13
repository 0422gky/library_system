import sqlite3
from datetime import datetime
import hashlib

def md5_hash(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # conn 是我们得到的数据库连接对象
    # cursor是连接对象的方法，，用来创建游标对象 c， cursor是用来执行SQL语句和获取查询结果的工具
    # 图书表
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        publisher TEXT,
        year INTEGER,
        price REAL,
        total INTEGER,
        available INTEGER)''')
    # 读者表
    c.execute('''CREATE TABLE IF NOT EXISTS readers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, gender TEXT, phone TEXT)''')
    # 借阅表
    c.execute('''CREATE TABLE IF NOT EXISTS borrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER, reader_id INTEGER,
        borrow_date TEXT, return_date TEXT, returned INTEGER)''')
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        realname TEXT,
        job_id TEXT,
        gender TEXT,
        age INTEGER)''')
    # 进货表
    c.execute('''CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        isbn TEXT,
        title TEXT,
        author TEXT,
        publisher TEXT,
        price REAL,
        quantity INTEGER,
        status TEXT)''')
    # 账单表
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        amount REAL,
        description TEXT,
        time TEXT)''')
    # 检查是否有超级管理员，没有则创建一个
    c.execute('SELECT * FROM users WHERE role="superadmin"')
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('root', md5_hash('root123'), 'superadmin'))
# 首次运行时自动创建超级管理员账号：用户名 root，密码 root123。
# 超级管理员登录后可以：
# 添加管理员
# 查看所有用户
# 进行所有图书、读者、借阅管理
# 普通管理员只能进行图书、读者、借阅管理
# 其他角色用户无权限操作
    conn.commit()
    conn.close()

def add_book(title, author, publisher, year, total):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('INSERT INTO books (title, author, publisher, year, total, available) VALUES (?, ?, ?, ?, ?, ?)',
              (title, author, publisher, year, total, total))
    conn.commit()
    conn.close()

def add_reader(name, gender, phone):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('INSERT INTO readers (name, gender, phone) VALUES (?, ?, ?)', (name, gender, phone))
    conn.commit()
    conn.close()

def borrow_book(book_id, reader_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT available FROM books WHERE id=?', (book_id,))
    available = c.fetchone()
    if available and available[0] > 0:
        c.execute('UPDATE books SET available=available-1 WHERE id=?', (book_id,))
        c.execute('INSERT INTO borrows (book_id, reader_id, borrow_date, return_date, returned) VALUES (?, ?, ?, ?, ?)',
                  (book_id, reader_id, datetime.now().strftime('%Y-%m-%d'), None, 0))
        print("借书成功")
    else:
        print("无可借图书")
    conn.commit()
    conn.close()

def return_book(borrow_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT book_id FROM borrows WHERE id=? AND returned=0', (borrow_id,))
    book = c.fetchone()
    if book:
        c.execute('UPDATE books SET available=available+1 WHERE id=?', (book[0],))
        c.execute('UPDATE borrows SET return_date=?, returned=1 WHERE id=?',
                  (datetime.now().strftime('%Y-%m-%d'), borrow_id))
        print("还书成功")
    else:
        print("未找到未归还的借阅记录")
    conn.commit()
    conn.close()

def list_books():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM books')
    books = c.fetchall()
    print("\n所有图书：")
    for book in books:
        print(book)
    conn.close()

def list_readers():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM readers')
    readers = c.fetchall()
    print("\n所有读者：")
    for reader in readers:
        print(reader)
    conn.close()

def list_borrows():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM borrows')
    borrows = c.fetchall()
    print("\n所有借阅记录：")
    for borrow in borrows:
        print(borrow)
    conn.close()

def register_user(username, password, role='user'):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, md5_hash(password), role))
        conn.commit()
        print('注册成功！')
    except sqlite3.IntegrityError:
        print('用户名已存在！')
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, md5_hash(password)))
    user = c.fetchone()
    conn.close()
    if user:
        print('登录成功！')
        return user
    else:
        print('用户名或密码错误！')
        return None

def add_admin(username, password, role='admin'):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, md5_hash(password), role))
        conn.commit()
        print('管理员添加成功！')
    except sqlite3.IntegrityError:
        print('用户名已存在！')
    conn.close()

def list_users():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users')
    users = c.fetchall()
    print('\n所有用户：')
    for user in users:
        print(user)
    conn.close()

def update_book(book_id, isbn=None, title=None, author=None, publisher=None, year=None, price=None, total=None):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # 获取当前信息
    c.execute('SELECT * FROM books WHERE id=?', (book_id,))
    book = c.fetchone()
    if not book:
        print('未找到该图书')
        conn.close()
        return
    # 只更新有输入的字段
    new_isbn = isbn if isbn is not None else book[1]
    new_title = title if title is not None else book[2]
    new_author = author if author is not None else book[3]
    new_publisher = publisher if publisher is not None else book[4]
    new_year = year if year is not None else book[5]
    new_price = price if price is not None else book[6]
    new_total = total if total is not None else book[7]
    # 可用数量自动调整
    available = book[8] + (new_total - book[7])
    c.execute('''UPDATE books SET isbn=?, title=?, author=?, publisher=?, year=?, price=?, total=?, available=? WHERE id=?''',
              (new_isbn, new_title, new_author, new_publisher, new_year, new_price, new_total, available, book_id))
    conn.commit()
    print('图书信息已更新')
    conn.close()

def search_books(book_id=None, isbn=None, title=None, author=None, publisher=None):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    if book_id:
        query += ' AND id=?'
        params.append(book_id)
    if isbn:
        query += ' AND isbn LIKE ?'
        params.append(f'%{isbn}%')
    if title:
        query += ' AND title LIKE ?'
        params.append(f'%{title}%')
    if author:
        query += ' AND author LIKE ?'
        params.append(f'%{author}%')
    if publisher:
        query += ' AND publisher LIKE ?'
        params.append(f'%{publisher}%')
    c.execute(query, params)
    books = c.fetchall()
    print('\n查询结果：')
    for book in books:
        print(book)
    if not books:
        print('未找到相关图书')
    conn.close()

def add_purchase_order(book_id=None, isbn=None, title=None, author=None, publisher=None, price=None, quantity=None):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    if book_id:
        # 已有书，自动补全信息
        c.execute('SELECT * FROM books WHERE id=?', (book_id,))
        book = c.fetchone()
        if not book:
            print('未找到该图书')
            conn.close()
            return
        isbn = book[1]
        title = book[2]
        author = book[3]
        publisher = book[4]
    c.execute('''INSERT INTO purchase_orders (book_id, isbn, title, author, publisher, price, quantity, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (book_id, isbn, title, author, publisher, price, quantity, '未付款'))
    conn.commit()
    print('进货单已添加，状态为未付款')
    conn.close()

def list_unpaid_purchase_orders():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM purchase_orders WHERE status="未付款"')
    orders = c.fetchall()
    print('\n未付款进货单：')
    for order in orders:
        print(order)
    if not orders:
        print('无未付款进货单')
    conn.close()

def pay_purchase_order(order_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM purchase_orders WHERE id=? AND status="未付款"', (order_id,))
    order = c.fetchone()
    if not order:
        print('未找到该未付款进货单')
        conn.close()
        return
    # 更新状态
    c.execute('UPDATE purchase_orders SET status="已付款" WHERE id=?', (order_id,))
    # 增加库存
    if order[1]:
        c.execute('UPDATE books SET total=total+?, available=available+? WHERE id=?', (order[7], order[7], order[1]))
    else:
        # 新书，需插入books表
        c.execute('''INSERT INTO books (isbn, title, author, publisher, year, price, total, available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (order[2], order[3], order[4], order[5], None, order[6], order[7], order[7]))
    conn.commit()
    print('付款成功，库存已更新')
    conn.close()

def return_purchase_order(order_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM purchase_orders WHERE id=? AND status="未付款"', (order_id,))
    order = c.fetchone()
    if not order:
        print('未找到该未付款进货单')
        conn.close()
        return
    c.execute('UPDATE purchase_orders SET status="退货" WHERE id=?', (order_id,))
    conn.commit()
    print('退货成功，进货单状态已更新为退货')
    conn.close()

# 添加新书（对已付款进货单，填写零售价并入库，生成支出账单）
def add_new_book_from_paid_order(order_id, price):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM purchase_orders WHERE id=? AND status="已付款"', (order_id,))
    order = c.fetchone()
    if not order:
        print('未找到该已付款进货单')
        conn.close()
        return
    # 检查是否已入库
    c.execute('SELECT * FROM books WHERE isbn=?', (order[2],))
    book = c.fetchone()
    if book:
        print('该书已在库存中')
        conn.close()
        return
    # 入库
    c.execute('''INSERT INTO books (isbn, title, author, publisher, year, price, total, available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (order[2], order[3], order[4], order[5], None, price, order[7], order[7]))
    # 生成账单（支出）
    c.execute('''INSERT INTO bills (type, amount, description, time) VALUES (?, ?, ?, ?)''',
              ('支出', order[6]*order[7], f'进货单{order_id}入库', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    print('新书已入库，账单已生成')
    conn.close()

# 书籍购买（减少库存，生成收入账单）
def buy_book(book_id, quantity):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM books WHERE id=?', (book_id,))
    book = c.fetchone()
    if not book:
        print('未找到该图书')
        conn.close()
        return
    if book[8] < quantity:
        print('库存不足')
        conn.close()
        return
    c.execute('UPDATE books SET available=available-? WHERE id=?', (quantity, book_id))
    # 生成账单（收入）
    c.execute('''INSERT INTO bills (type, amount, description, time) VALUES (?, ?, ?, ?)''',
              ('收入', book[6]*quantity, f'图书{book_id}售出{quantity}本', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    print('购买成功，账单已生成')
    conn.close()

# 按时间段查询账单
def list_bills_by_time(start_time, end_time):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bills WHERE time>=? AND time<=?', (start_time, end_time))
    bills = c.fetchall()
    print(f'\n{start_time} 至 {end_time} 的账单记录：')
    for bill in bills:
        print(bill)
    if not bills:
        print('无账单记录')
    conn.close()

if __name__ == '__main__':
    init_db()
    current_user = None
    while True:
        if not current_user:
            print('\n===== 用户管理 =====')
            print('1. 注册')
            print('2. 登录')
            print('0. 退出')
            choice = input('请选择操作：')
            if choice == '1':
                username = input('用户名：')
                password = input('密码：')
                register_user(username, password)
            elif choice == '2':
                username = input('用户名：')
                password = input('密码：')
                user = login_user(username, password)
                if user:
                    current_user = user
            elif choice == '0':
                break
            else:
                print('无效选择，请重试。')
        else:
            print(f'\n当前用户：{current_user[1]} (角色: {current_user[3]})')
            if current_user[3] == 'superadmin':
                print("1. 添加管理员")
                print("2. 查看所有用户")
                print("3. 添加图书")
                print("4. 添加读者")
                print("5. 借书")
                print("6. 还书")
                print("7. 查询所有图书")
                print("8. 查询所有读者")
                print("9. 查询所有借阅记录")
                print("10. 退出登录")
                print("11. 修改图书信息")
                print("12. 多条件查询图书")
                print("13. 添加进货单")
                print("14. 查看未付款进货单")
                print("15. 进货付款")
                print("16. 进货退货")
                print("17. 新书入库")
                print("18. 书籍购买")
                print("19. 查询账单")
                print("0. 退出系统")
                choice = input("请选择操作：")
                if choice == '1':
                    username = input('管理员用户名：')
                    password = input('密码：')
                    add_admin(username, password, 'admin')
                elif choice == '2':
                    list_users()
                elif choice == '3':
                    title = input("书名：")
                    author = input("作者：")
                    publisher = input("出版社：")
                    year = int(input("年份："))
                    total = int(input("总数："))
                    add_book(title, author, publisher, year, total)
                    print("添加成功！")
                elif choice == '4':
                    name = input("姓名：")
                    gender = input("性别：")
                    phone = input("电话：")
                    add_reader(name, gender, phone)
                    print("添加成功！")
                elif choice == '5':
                    book_id = int(input("图书ID："))
                    reader_id = int(input("读者ID："))
                    borrow_book(book_id, reader_id)
                elif choice == '6':
                    borrow_id = int(input("借阅记录ID："))
                    return_book(borrow_id)
                elif choice == '7':
                    list_books()
                elif choice == '8':
                    list_readers()
                elif choice == '9':
                    list_borrows()
                elif choice == '10':
                    current_user = None
                elif choice == '11':
                    book_id = int(input("请输入要修改的图书ID："))
                    print("如不修改某项请直接回车")
                    isbn = input("ISBN：") or None
                    title = input("书名：") or None
                    author = input("作者：") or None
                    publisher = input("出版社：") or None
                    year = input("年份：")
                    year = int(year) if year else None
                    price = input("价格：")
                    price = float(price) if price else None
                    total = input("总数：")
                    total = int(total) if total else None
                    update_book(book_id, isbn, title, author, publisher, year, price, total)
                elif choice == '12':
                    print("如不查询某项请直接回车")
                    book_id = input("图书ID：")
                    book_id = int(book_id) if book_id else None
                    isbn = input("ISBN：") or None
                    title = input("书名：") or None
                    author = input("作者：") or None
                    publisher = input("出版社：") or None
                    search_books(book_id, isbn, title, author, publisher)
                elif choice == '13':
                    print("已有图书请输入图书ID，否则直接回车新增图书")
                    book_id = input("图书ID：")
                    book_id = int(book_id) if book_id else None
                    if not book_id:
                        isbn = input("ISBN：") or None
                        title = input("书名：") or None
                        author = input("作者：") or None
                        publisher = input("出版社：") or None
                    else:
                        isbn = title = author = publisher = None
                    price = float(input("进货价格："))
                    quantity = int(input("进货数量："))
                    add_purchase_order(book_id, isbn, title, author, publisher, price, quantity)
                elif choice == '14':
                    list_unpaid_purchase_orders()
                elif choice == '15':
                    order_id = int(input("请输入要付款的进货单ID："))
                    pay_purchase_order(order_id)
                elif choice == '16':
                    order_id = int(input("请输入要退货的进货单ID："))
                    return_purchase_order(order_id)
                elif choice == '17':
                    order_id = int(input("请输入已付款进货单ID："))
                    price = float(input("请输入零售价："))
                    add_new_book_from_paid_order(order_id, price)
                elif choice == '18':
                    book_id = int(input("请输入要购买的图书ID："))
                    quantity = int(input("请输入购买数量："))
                    buy_book(book_id, quantity)
                elif choice == '19':
                    start_time = input("请输入起始时间(YYYY-MM-DD 00:00:00)：")
                    end_time = input("请输入结束时间(YYYY-MM-DD 23:59:59)：")
                    list_bills_by_time(start_time, end_time)
                elif choice == '0':
                    print("退出系统。")
                    break
                else:
                    print("无效选择，请重试。")
            elif current_user[3] == 'admin':
                print("1. 添加图书")
                print("2. 添加读者")
                print("3. 借书")
                print("4. 还书")
                print("5. 查询所有图书")
                print("6. 查询所有读者")
                print("7. 查询所有借阅记录")
                print("8. 退出登录")
                print("9. 修改图书信息")
                print("10. 多条件查询图书")
                print("11. 添加进货单")
                print("12. 查看未付款进货单")
                print("13. 进货付款")
                print("14. 进货退货")
                print("15. 新书入库")
                print("16. 书籍购买")
                print("17. 查询账单")
                print("0. 退出系统")
                choice = input("请选择操作：")
                if choice == '1':
                    title = input("书名：")
                    author = input("作者：")
                    publisher = input("出版社：")
                    year = int(input("年份："))
                    total = int(input("总数："))
                    add_book(title, author, publisher, year, total)
                    print("添加成功！")
                elif choice == '2':
                    name = input("姓名：")
                    gender = input("性别：")
                    phone = input("电话：")
                    add_reader(name, gender, phone)
                    print("添加成功！")
                elif choice == '3':
                    book_id = int(input("图书ID："))
                    reader_id = int(input("读者ID："))
                    borrow_book(book_id, reader_id)
                elif choice == '4':
                    borrow_id = int(input("借阅记录ID："))
                    return_book(borrow_id)
                elif choice == '5':
                    list_books()
                elif choice == '6':
                    list_readers()
                elif choice == '7':
                    list_borrows()
                elif choice == '8':
                    current_user = None
                elif choice == '9':
                    book_id = int(input("请输入要修改的图书ID："))
                    print("如不修改某项请直接回车")
                    isbn = input("ISBN：") or None
                    title = input("书名：") or None
                    author = input("作者：") or None
                    publisher = input("出版社：") or None
                    year = input("年份：")
                    year = int(year) if year else None
                    price = input("价格：")
                    price = float(price) if price else None
                    total = input("总数：")
                    total = int(total) if total else None
                    update_book(book_id, isbn, title, author, publisher, year, price, total)
                elif choice == '10':
                    print("如不查询某项请直接回车")
                    book_id = input("图书ID：")
                    book_id = int(book_id) if book_id else None
                    isbn = input("ISBN：") or None
                    title = input("书名：") or None
                    author = input("作者：") or None
                    publisher = input("出版社：") or None
                    search_books(book_id, isbn, title, author, publisher)
                elif choice == '11':
                    print("已有图书请输入图书ID，否则直接回车新增图书")
                    book_id = input("图书ID：")
                    book_id = int(book_id) if book_id else None
                    if not book_id:
                        isbn = input("ISBN：") or None
                        title = input("书名：") or None
                        author = input("作者：") or None
                        publisher = input("出版社：") or None
                    else:
                        isbn = title = author = publisher = None
                    price = float(input("进货价格："))
                    quantity = int(input("进货数量："))
                    add_purchase_order(book_id, isbn, title, author, publisher, price, quantity)
                elif choice == '12':
                    list_unpaid_purchase_orders()
                elif choice == '13':
                    order_id = int(input("请输入要付款的进货单ID："))
                    pay_purchase_order(order_id)
                elif choice == '14':
                    order_id = int(input("请输入要退货的进货单ID："))
                    return_purchase_order(order_id)
                elif choice == '15':
                    order_id = int(input("请输入已付款进货单ID："))
                    price = float(input("请输入零售价："))
                    add_new_book_from_paid_order(order_id, price)
                elif choice == '16':
                    book_id = int(input("请输入要购买的图书ID："))
                    quantity = int(input("请输入购买数量："))
                    buy_book(book_id, quantity)
                elif choice == '17':
                    start_time = input("请输入起始时间(YYYY-MM-DD 00:00:00)：")
                    end_time = input("请输入结束时间(YYYY-MM-DD 23:59:59)：")
                    list_bills_by_time(start_time, end_time)
                elif choice == '0':
                    print("退出系统。")
                    break
                else:
                    print("无效选择，请重试。")
            else:
                print("无权限操作，请联系管理员。");
                current_user = None
