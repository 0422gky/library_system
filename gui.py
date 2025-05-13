from test import (register_user, login_user, add_book, list_books, add_reader, list_readers,
                 borrow_book, return_book, list_borrows, add_admin, list_users, update_book,
                 search_books, add_purchase_order, list_unpaid_purchase_orders, pay_purchase_order,
                 return_purchase_order, add_new_book_from_paid_order, buy_book, list_bills_by_time)
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime

current_user = None

def set_fullscreen(window):
    window.attributes('-fullscreen', True)
    window.bind('<Escape>', lambda e: window.attributes('-fullscreen', False))

def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)

def show_warning(title, message):
    messagebox.showwarning(title, message)

def show_confirm(title, message):
    return messagebox.askyesno(title, message)

def capture_output(func, *args):
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    func(*args)
    sys.stdout = old_stdout
    return mystdout.getvalue()

# 登录窗口
def show_login():
    def do_login():
        global current_user
        username = entry_username.get()
        password = entry_password.get()
        user = login_user(username, password)
        if user:
            current_user = user
            login_win.destroy()
            show_main_menu()
        else:
            show_error("登录失败", "用户名或密码错误！")

    login_win = tk.Tk()
    login_win.title("登录")
    set_fullscreen(login_win)
    
    # 创建主框架并居中
    main_frame = tk.Frame(login_win)
    main_frame.place(relx=0.5, rely=0.5, anchor='center')
    
    tk.Label(main_frame, text="图书馆管理系统", font=('Arial', 20)).pack(pady=20)
    tk.Label(main_frame, text="用户名:").pack()
    entry_username = tk.Entry(main_frame)
    entry_username.pack(pady=5)
    tk.Label(main_frame, text="密码:").pack()
    entry_password = tk.Entry(main_frame, show="*")
    entry_password.pack(pady=5)
    
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="登录", command=do_login, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="注册", command=lambda:[login_win.destroy(), show_register()], width=10).pack(side=tk.LEFT, padx=5)
    
    login_win.mainloop()

# 注册窗口
def show_register():
    def do_register():
        username = entry_username.get()
        password = entry_password.get()
        if not username or not password:
            show_warning("注册", "用户名和密码不能为空！")
            return
        register_user(username, password)
        show_info("注册", "注册成功！请登录。")
        reg_win.destroy()
        show_login()

    reg_win = tk.Tk()
    reg_win.title("注册")
    set_fullscreen(reg_win)
    
    main_frame = tk.Frame(reg_win)
    main_frame.place(relx=0.5, rely=0.5, anchor='center')
    
    tk.Label(main_frame, text="用户注册", font=('Arial', 20)).pack(pady=20)
    tk.Label(main_frame, text="用户名:").pack()
    entry_username = tk.Entry(main_frame)
    entry_username.pack(pady=5)
    tk.Label(main_frame, text="密码:").pack()
    entry_password = tk.Entry(main_frame, show="*")
    entry_password.pack(pady=5)
    
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="注册", command=do_register, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回登录", command=lambda:[reg_win.destroy(), show_login()], width=10).pack(side=tk.LEFT, padx=5)
    
    reg_win.mainloop()

# 图书管理窗口
def show_book_management():
    book_win = tk.Toplevel()
    book_win.title("图书管理")
    set_fullscreen(book_win)
    
    def add_book_gui():
        def do_add():
            try:
                title = entry_title.get()
                author = entry_author.get()
                publisher = entry_publisher.get()
                year = int(entry_year.get())
                total = int(entry_total.get())
                if all([title, author, publisher, year, total]):
                    add_book(title, author, publisher, year, total)
                    show_info("添加图书", "添加成功！")
                    add_window.destroy()
                    refresh_book_list()
                else:
                    show_warning("添加图书", "所有字段都必须填写！")
            except ValueError:
                show_error("添加图书", "年份和总数必须是数字！")
        
        add_window = tk.Toplevel(book_win)
        add_window.title("添加图书")
        add_window.geometry("400x300")
        
        tk.Label(add_window, text="书名:").pack()
        entry_title = tk.Entry(add_window)
        entry_title.pack()
        tk.Label(add_window, text="作者:").pack()
        entry_author = tk.Entry(add_window)
        entry_author.pack()
        tk.Label(add_window, text="出版社:").pack()
        entry_publisher = tk.Entry(add_window)
        entry_publisher.pack()
        tk.Label(add_window, text="年份:").pack()
        entry_year = tk.Entry(add_window)
        entry_year.pack()
        tk.Label(add_window, text="总数:").pack()
        entry_total = tk.Entry(add_window)
        entry_total.pack()
        
        tk.Button(add_window, text="添加", command=do_add).pack(pady=10)
    
    def search_book_gui():
        def do_search():
            book_id = entry_id.get() or None
            if book_id:
                try:
                    book_id = int(book_id)
                except ValueError:
                    show_error("搜索", "图书ID必须是数字！")
                    return
            
            isbn = entry_isbn.get() or None
            title = entry_title.get() or None
            author = entry_author.get() or None
            publisher = entry_publisher.get() or None
            
            result = capture_output(search_books, book_id, isbn, title, author, publisher)
            show_info("搜索结果", result)
        
        search_window = tk.Toplevel(book_win)
        search_window.title("搜索图书")
        search_window.geometry("400x300")
        
        tk.Label(search_window, text="图书ID:").pack()
        entry_id = tk.Entry(search_window)
        entry_id.pack()
        tk.Label(search_window, text="ISBN:").pack()
        entry_isbn = tk.Entry(search_window)
        entry_isbn.pack()
        tk.Label(search_window, text="书名:").pack()
        entry_title = tk.Entry(search_window)
        entry_title.pack()
        tk.Label(search_window, text="作者:").pack()
        entry_author = tk.Entry(search_window)
        entry_author.pack()
        tk.Label(search_window, text="出版社:").pack()
        entry_publisher = tk.Entry(search_window)
        entry_publisher.pack()
        
        tk.Button(search_window, text="搜索", command=do_search).pack(pady=10)
    
    def update_book_gui():
        def do_update():
            try:
                book_id = int(entry_id.get())
                isbn = entry_isbn.get() or None
                title = entry_title.get() or None
                author = entry_author.get() or None
                publisher = entry_publisher.get() or None
                year = entry_year.get()
                year = int(year) if year else None
                price = entry_price.get()
                price = float(price) if price else None
                total = entry_total.get()
                total = int(total) if total else None
                
                update_book(book_id, isbn, title, author, publisher, year, price, total)
                show_info("更新图书", "更新成功！")
                update_window.destroy()
                refresh_book_list()
            except ValueError:
                show_error("更新图书", "请输入有效的数字！")
        
        update_window = tk.Toplevel(book_win)
        update_window.title("更新图书")
        update_window.geometry("400x400")
        
        tk.Label(update_window, text="图书ID:").pack()
        entry_id = tk.Entry(update_window)
        entry_id.pack()
        tk.Label(update_window, text="ISBN:").pack()
        entry_isbn = tk.Entry(update_window)
        entry_isbn.pack()
        tk.Label(update_window, text="书名:").pack()
        entry_title = tk.Entry(update_window)
        entry_title.pack()
        tk.Label(update_window, text="作者:").pack()
        entry_author = tk.Entry(update_window)
        entry_author.pack()
        tk.Label(update_window, text="出版社:").pack()
        entry_publisher = tk.Entry(update_window)
        entry_publisher.pack()
        tk.Label(update_window, text="年份:").pack()
        entry_year = tk.Entry(update_window)
        entry_year.pack()
        tk.Label(update_window, text="价格:").pack()
        entry_price = tk.Entry(update_window)
        entry_price.pack()
        tk.Label(update_window, text="总数:").pack()
        entry_total = tk.Entry(update_window)
        entry_total.pack()
        
        tk.Button(update_window, text="更新", command=do_update).pack(pady=10)
    
    def refresh_book_list():
        result = capture_output(list_books)
        text_books.delete(1.0, tk.END)
        text_books.insert(tk.END, result)
    
    # 创建主框架
    main_frame = tk.Frame(book_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(button_frame, text="添加图书", command=add_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="搜索图书", command=search_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="更新图书", command=update_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="刷新列表", command=refresh_book_list).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回主菜单", command=book_win.destroy).pack(side=tk.RIGHT, padx=5)
    
    # 图书列表
    text_books = tk.Text(main_frame, height=20)
    text_books.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 初始显示图书列表
    refresh_book_list()

# 读者管理窗口
def show_reader_management():
    reader_win = tk.Toplevel()
    reader_win.title("读者管理")
    set_fullscreen(reader_win)
    
    def add_reader_gui():
        def do_add():
            name = entry_name.get()
            gender = entry_gender.get()
            phone = entry_phone.get()
            if all([name, gender, phone]):
                add_reader(name, gender, phone)
                show_info("添加读者", "添加成功！")
                add_window.destroy()
                refresh_reader_list()
            else:
                show_warning("添加读者", "所有字段都必须填写！")
        
        add_window = tk.Toplevel(reader_win)
        add_window.title("添加读者")
        add_window.geometry("300x200")
        
        tk.Label(add_window, text="姓名:").pack()
        entry_name = tk.Entry(add_window)
        entry_name.pack()
        tk.Label(add_window, text="性别:").pack()
        entry_gender = tk.Entry(add_window)
        entry_gender.pack()
        tk.Label(add_window, text="电话:").pack()
        entry_phone = tk.Entry(add_window)
        entry_phone.pack()
        
        tk.Button(add_window, text="添加", command=do_add).pack(pady=10)
    
    def refresh_reader_list():
        result = capture_output(list_readers)
        text_readers.delete(1.0, tk.END)
        text_readers.insert(tk.END, result)
    
    # 创建主框架
    main_frame = tk.Frame(reader_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(button_frame, text="添加读者", command=add_reader_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="刷新列表", command=refresh_reader_list).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回主菜单", command=reader_win.destroy).pack(side=tk.RIGHT, padx=5)
    
    # 读者列表
    text_readers = tk.Text(main_frame, height=20)
    text_readers.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 初始显示读者列表
    refresh_reader_list()

# 借阅管理窗口
def show_borrow_management():
    borrow_win = tk.Toplevel()
    borrow_win.title("借阅管理")
    set_fullscreen(borrow_win)
    
    def borrow_book_gui():
        def do_borrow():
            try:
                book_id = int(entry_book_id.get())
                reader_id = int(entry_reader_id.get())
                borrow_book(book_id, reader_id)
                show_info("借书", "借书成功！")
                borrow_window.destroy()
                refresh_borrow_list()
            except ValueError:
                show_error("借书", "请输入有效的ID！")
        
        borrow_window = tk.Toplevel(borrow_win)
        borrow_window.title("借书")
        borrow_window.geometry("300x150")
        
        tk.Label(borrow_window, text="图书ID:").pack()
        entry_book_id = tk.Entry(borrow_window)
        entry_book_id.pack()
        tk.Label(borrow_window, text="读者ID:").pack()
        entry_reader_id = tk.Entry(borrow_window)
        entry_reader_id.pack()
        
        tk.Button(borrow_window, text="借书", command=do_borrow).pack(pady=10)
    
    def return_book_gui():
        def do_return():
            try:
                borrow_id = int(entry_borrow_id.get())
                return_book(borrow_id)
                show_info("还书", "还书成功！")
                return_window.destroy()
                refresh_borrow_list()
            except ValueError:
                show_error("还书", "请输入有效的借阅ID！")
        
        return_window = tk.Toplevel(borrow_win)
        return_window.title("还书")
        return_window.geometry("300x150")
        
        tk.Label(return_window, text="借阅记录ID:").pack()
        entry_borrow_id = tk.Entry(return_window)
        entry_borrow_id.pack()
        
        tk.Button(return_window, text="还书", command=do_return).pack(pady=10)
    
    def refresh_borrow_list():
        result = capture_output(list_borrows)
        text_borrows.delete(1.0, tk.END)
        text_borrows.insert(tk.END, result)
    
    # 创建主框架
    main_frame = tk.Frame(borrow_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(button_frame, text="借书", command=borrow_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="还书", command=return_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="刷新列表", command=refresh_borrow_list).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回主菜单", command=borrow_win.destroy).pack(side=tk.RIGHT, padx=5)
    
    # 借阅列表
    text_borrows = tk.Text(main_frame, height=20)
    text_borrows.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 初始显示借阅列表
    refresh_borrow_list()

# 进货管理窗口
def show_purchase_management():
    purchase_win = tk.Toplevel()
    purchase_win.title("进货管理")
    set_fullscreen(purchase_win)
    
    def add_purchase_gui():
        def do_add():
            try:
                book_id = entry_book_id.get()
                book_id = int(book_id) if book_id else None
                
                if not book_id:
                    isbn = entry_isbn.get() or None
                    title = entry_title.get() or None
                    author = entry_author.get() or None
                    publisher = entry_publisher.get() or None
                else:
                    isbn = title = author = publisher = None
                
                price = float(entry_price.get())
                quantity = int(entry_quantity.get())
                
                add_purchase_order(book_id, isbn, title, author, publisher, price, quantity)
                show_info("添加进货单", "添加成功！")
                add_window.destroy()
                refresh_purchase_list()
            except ValueError:
                show_error("添加进货单", "请输入有效的数字！")
        
        add_window = tk.Toplevel(purchase_win)
        add_window.title("添加进货单")
        add_window.geometry("400x400")
        
        tk.Label(add_window, text="图书ID (可选):").pack()
        entry_book_id = tk.Entry(add_window)
        entry_book_id.pack()
        tk.Label(add_window, text="ISBN (新书必填):").pack()
        entry_isbn = tk.Entry(add_window)
        entry_isbn.pack()
        tk.Label(add_window, text="书名 (新书必填):").pack()
        entry_title = tk.Entry(add_window)
        entry_title.pack()
        tk.Label(add_window, text="作者 (新书必填):").pack()
        entry_author = tk.Entry(add_window)
        entry_author.pack()
        tk.Label(add_window, text="出版社 (新书必填):").pack()
        entry_publisher = tk.Entry(add_window)
        entry_publisher.pack()
        tk.Label(add_window, text="进货价格:").pack()
        entry_price = tk.Entry(add_window)
        entry_price.pack()
        tk.Label(add_window, text="进货数量:").pack()
        entry_quantity = tk.Entry(add_window)
        entry_quantity.pack()
        
        tk.Button(add_window, text="添加", command=do_add).pack(pady=10)
    
    def pay_purchase_gui():
        def do_pay():
            try:
                order_id = int(entry_order_id.get())
                pay_purchase_order(order_id)
                show_info("付款", "付款成功！")
                pay_window.destroy()
                refresh_purchase_list()
            except ValueError:
                show_error("付款", "请输入有效的订单ID！")
        
        pay_window = tk.Toplevel(purchase_win)
        pay_window.title("进货付款")
        pay_window.geometry("300x150")
        
        tk.Label(pay_window, text="订单ID:").pack()
        entry_order_id = tk.Entry(pay_window)
        entry_order_id.pack()
        
        tk.Button(pay_window, text="付款", command=do_pay).pack(pady=10)
    
    def return_purchase_gui():
        def do_return():
            try:
                order_id = int(entry_order_id.get())
                return_purchase_order(order_id)
                show_info("退货", "退货成功！")
                return_window.destroy()
                refresh_purchase_list()
            except ValueError:
                show_error("退货", "请输入有效的订单ID！")
        
        return_window = tk.Toplevel(purchase_win)
        return_window.title("进货退货")
        return_window.geometry("300x150")
        
        tk.Label(return_window, text="订单ID:").pack()
        entry_order_id = tk.Entry(return_window)
        entry_order_id.pack()
        
        tk.Button(return_window, text="退货", command=do_return).pack(pady=10)
    
    def add_new_book_gui():
        def do_add():
            try:
                order_id = int(entry_order_id.get())
                price = float(entry_price.get())
                add_new_book_from_paid_order(order_id, price)
                show_info("新书入库", "入库成功！")
                add_window.destroy()
                refresh_purchase_list()
            except ValueError:
                show_error("新书入库", "请输入有效的数字！")
        
        add_window = tk.Toplevel(purchase_win)
        add_window.title("新书入库")
        add_window.geometry("300x150")
        
        tk.Label(add_window, text="订单ID:").pack()
        entry_order_id = tk.Entry(add_window)
        entry_order_id.pack()
        tk.Label(add_window, text="零售价:").pack()
        entry_price = tk.Entry(add_window)
        entry_price.pack()
        
        tk.Button(add_window, text="入库", command=do_add).pack(pady=10)
    
    def refresh_purchase_list():
        result = capture_output(list_unpaid_purchase_orders)
        text_purchases.delete(1.0, tk.END)
        text_purchases.insert(tk.END, result)
    
    # 创建主框架
    main_frame = tk.Frame(purchase_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(button_frame, text="添加进货单", command=add_purchase_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="进货付款", command=pay_purchase_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="进货退货", command=return_purchase_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="新书入库", command=add_new_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="刷新列表", command=refresh_purchase_list).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回主菜单", command=purchase_win.destroy).pack(side=tk.RIGHT, padx=5)
    
    # 进货单列表
    text_purchases = tk.Text(main_frame, height=20)
    text_purchases.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 初始显示进货单列表
    refresh_purchase_list()

# 账单管理窗口
def show_bill_management():
    bill_win = tk.Toplevel()
    bill_win.title("账单管理")
    set_fullscreen(bill_win)
    
    def search_bills_gui():
        def do_search():
            try:
                start_time = entry_start.get()
                end_time = entry_end.get()
                result = capture_output(list_bills_by_time, start_time, end_time)
                show_info("账单查询", result)
                search_window.destroy()
            except Exception as e:
                show_error("账单查询", str(e))
        
        search_window = tk.Toplevel(bill_win)
        search_window.title("查询账单")
        search_window.geometry("400x200")
        
        tk.Label(search_window, text="起始时间 (YYYY-MM-DD 00:00:00):").pack()
        entry_start = tk.Entry(search_window)
        entry_start.pack()
        tk.Label(search_window, text="结束时间 (YYYY-MM-DD 23:59:59):").pack()
        entry_end = tk.Entry(search_window)
        entry_end.pack()
        
        tk.Button(search_window, text="查询", command=do_search).pack(pady=10)
    
    # 创建主框架
    main_frame = tk.Frame(bill_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(button_frame, text="查询账单", command=search_bills_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回主菜单", command=bill_win.destroy).pack(side=tk.RIGHT, padx=5)

# 用户管理窗口
def show_user_management():
    user_win = tk.Toplevel()
    user_win.title("用户管理")
    set_fullscreen(user_win)
    
    def add_admin_gui():
        def do_add():
            username = entry_username.get()
            password = entry_password.get()
            if username and password:
                add_admin(username, password)
                show_info("添加管理员", "添加成功！")
                add_window.destroy()
                refresh_user_list()
            else:
                show_warning("添加管理员", "用户名和密码不能为空！")
        
        add_window = tk.Toplevel(user_win)
        add_window.title("添加管理员")
        add_window.geometry("300x200")
        
        tk.Label(add_window, text="用户名:").pack()
        entry_username = tk.Entry(add_window)
        entry_username.pack()
        tk.Label(add_window, text="密码:").pack()
        entry_password = tk.Entry(add_window, show="*")
        entry_password.pack()
        
        tk.Button(add_window, text="添加", command=do_add).pack(pady=10)
    
    def refresh_user_list():
        result = capture_output(list_users)
        text_users.delete(1.0, tk.END)
        text_users.insert(tk.END, result)
    
    # 创建主框架
    main_frame = tk.Frame(user_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=5)
    
    tk.Button(button_frame, text="添加管理员", command=add_admin_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="刷新列表", command=refresh_user_list).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="返回主菜单", command=user_win.destroy).pack(side=tk.RIGHT, padx=5)
    
    # 用户列表
    text_users = tk.Text(main_frame, height=20)
    text_users.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 初始显示用户列表
    refresh_user_list()

# 主菜单
def show_main_menu():
    def logout():
        global current_user
        current_user = None
        main_win.destroy()
        show_login()

    def exit_system():
        if show_confirm("退出系统", "确定要退出系统吗？"):
            main_win.destroy()
            main_win.quit()

    main_win = tk.Tk()
    main_win.title("图书馆管理系统 - 主菜单")
    set_fullscreen(main_win)
    
    # 创建主框架
    main_frame = tk.Frame(main_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 欢迎信息
    welcome_frame = tk.Frame(main_frame)
    welcome_frame.pack(fill=tk.X, pady=10)
    tk.Label(welcome_frame, text=f"欢迎，{current_user[1]}", font=('Arial', 16)).pack(side=tk.LEFT)
    tk.Label(welcome_frame, text=f"角色: {current_user[3]}", font=('Arial', 12)).pack(side=tk.RIGHT)
    
    # 功能按钮框架
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 根据用户角色显示不同的功能按钮
    if current_user[3] == 'superadmin':
        # 超级管理员功能
        tk.Button(button_frame, text="用户管理", command=show_user_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="图书管理", command=show_book_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="读者管理", command=show_reader_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="借阅管理", command=show_borrow_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="进货管理", command=show_purchase_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="账单管理", command=show_bill_management, height=2).pack(fill=tk.X, pady=5)
    elif current_user[3] == 'admin':
        # 管理员功能
        tk.Button(button_frame, text="图书管理", command=show_book_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="读者管理", command=show_reader_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="借阅管理", command=show_borrow_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="进货管理", command=show_purchase_management, height=2).pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="账单管理", command=show_bill_management, height=2).pack(fill=tk.X, pady=5)
    else:
        # 普通用户功能
        tk.Label(button_frame, text="无权限操作，请联系管理员。", font=('Arial', 12)).pack(pady=20)
    
    # 底部按钮框架
    bottom_frame = tk.Frame(main_frame)
    bottom_frame.pack(fill=tk.X, pady=10)
    tk.Button(bottom_frame, text="退出登录", command=logout).pack(side=tk.LEFT, padx=5)
    tk.Button(bottom_frame, text="退出系统", command=exit_system).pack(side=tk.RIGHT, padx=5)
    
    main_win.mainloop()

if __name__ == '__main__':
    show_login()
