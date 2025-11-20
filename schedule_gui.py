import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time

# Màu sắc & font mặc định
PRIMARY_COLOR = "#005F69"
BACKGROUND_COLOR = "#FFFFFF"
TEXT_COLOR = "#005F69"
ACCENT_COLOR = "#F26F33"
FONT_FAMILY = "Tahoma"

# IMPORT CÁC CLASS CẦN THIẾT
# Đảm bảo các file này đã được tạo với nội dung mô phỏng ở trên
try:
    # utils.loader được giả định nằm trong thư mục utils/
    from utils.loader import load_all_data 
    from core.backtracking import BacktrackingSolver
    from core.gwo import GWOSolver
    from core.evaluator import ScheduleEvaluator
    from core.constraints import ConstraintChecker
    # THÊM DÒNG NÀY:
    from utils.printer import SchedulePrinter 
except ImportError as e:
    messagebox.showerror("Lỗi Import", f"Không tìm thấy các module cần thiết: {e}. Vui lòng đảm bảo cấu trúc thư mục và các file mô hình đã được tạo.")
    exit()




class ScheduleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Xếp Lịch Môn Học UEH")
        self.root.geometry("1400x900")
        self.root.configure(bg=BACKGROUND_COLOR)
        self._configure_styles()
        
        # Dữ liệu
        self.teachers = None
        self.rooms = None
        self.courses = None
        self.timeslots = None
        self.evaluator = None
        self.constraint_checker = None
        self.current_schedule = None # Schedule() object
        self.printer = None # Đã thêm: Khởi tạo printer
        
        # Khởi tạo giao diện
        self.setup_ui()
        
        # Load dữ liệu
        self.load_data()
    
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure('TNotebook', background=BACKGROUND_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab',
                        font=(FONT_FAMILY, 11, 'bold'),
                        padding=[12, 6],
                        background=BACKGROUND_COLOR,
                        foreground=TEXT_COLOR)
        style.map('TNotebook.Tab',
                  background=[('selected', ACCENT_COLOR)],
                  foreground=[('selected', 'white')])
        style.configure('Treeview',
                        rowheight=25,
                        font=(FONT_FAMILY, 10),
                        background=BACKGROUND_COLOR,
                        fieldbackground=BACKGROUND_COLOR,
                        foreground=TEXT_COLOR)
        style.configure('Treeview.Heading',
                        font=(FONT_FAMILY, 10, 'bold'),
                        background=PRIMARY_COLOR,
                        foreground='white')

    def setup_ui(self):
        """Thiết lập giao diện"""
        # Header
        header_frame = tk.Frame(self.root, bg=PRIMARY_COLOR, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text=" XẾP LỊCH MÔN HỌC UEH",
            font=(FONT_FAMILY, 24, 'bold'),
            bg=PRIMARY_COLOR,
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Control
        left_panel = tk.Frame(main_container, bg=BACKGROUND_COLOR, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.setup_control_panel(left_panel)
        
        # Right panel - Notebook tabs
        right_panel = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Tổng quan lịch
        self.overview_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.overview_tab, text='📊 Tổng Quan Lịch')
        self.setup_overview_tab()
        
        # Tab 2: Lịch theo giáo viên
        self.teacher_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.teacher_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.teacher_tab, text='👨‍🏫 Lịch Giáo Viên')
        self.setup_teacher_tab(self.teacher_frame)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Sẵn sàng",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=PRIMARY_COLOR,
            fg='white',
            font=(FONT_FAMILY, 10)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_control_panel(self, parent):
        """Thiết lập panel điều khiển"""
        control_frame = tk.Frame(parent, bg=BACKGROUND_COLOR)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        tk.Label(
            control_frame,
            text="⚙️ Điều Khiển",
            font=(FONT_FAMILY, 16, 'bold'),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=(0, 20))
        
        # Data info
        info_frame = tk.LabelFrame(
            control_frame,
            text="📋 Thông Tin Dữ Liệu",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.info_text = tk.Text(
            info_frame,
            height=6,
            width=30,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.info_text.pack(padx=10, pady=10)
        self.info_text.config(state=tk.DISABLED)
        
        # Algorithm selection
        algo_frame = tk.LabelFrame(
            control_frame,
            text="🔧 Chọn Thuật Toán",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        algo_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.algo_var = tk.StringVar(value="backtracking")
        
        tk.Radiobutton(
            algo_frame,
            text="Backtracking",
            variable=self.algo_var,
            value="backtracking",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            selectcolor=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR,
            command=self.on_algo_change
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        tk.Radiobutton(
            algo_frame,
            text="GWO (Grey Wolf)",
            variable=self.algo_var,
            value="gwo",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            selectcolor=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR,
            command=self.on_algo_change
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # GWO parameters
        self.gwo_params_frame = tk.LabelFrame(
            control_frame,
            text="🐺 Tham Số GWO",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        self.gwo_params_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            self.gwo_params_frame,
            text="Số lượng sói:",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.population_var = tk.StringVar(value="20")
        tk.Entry(
            self.gwo_params_frame,
            textvariable=self.population_var,
            width=10,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=0
        ).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(
            self.gwo_params_frame,
            text="Số vòng lặp:",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.iterations_var = tk.StringVar(value="100")
        tk.Entry(
            self.gwo_params_frame,
            textvariable=self.iterations_var,
            width=10,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=0
        ).grid(row=1, column=1, padx=10, pady=5)
        
        self.gwo_params_frame.pack_forget() 
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.run_button = tk.Button(
            button_frame,
            text="▶️ Chạy Thuật Toán",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=PRIMARY_COLOR,
            fg='white',
            activebackground=PRIMARY_COLOR,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.run_algorithm
        )
        self.run_button.pack(fill=tk.X, pady=5)
        
        self.compare_button = tk.Button(
            button_frame,
            text="⚖️ So Sánh 2 Thuật Toán",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=ACCENT_COLOR,
            fg='white',
            activebackground=ACCENT_COLOR,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.compare_algorithms
        )
        self.compare_button.pack(fill=tk.X, pady=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="🗑️ Xóa Kết Quả",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=ACCENT_COLOR,
            fg='white',
            activebackground=ACCENT_COLOR,
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.clear_results
        )
        self.clear_button.pack(fill=tk.X, pady=5)
        
        # Results info
        results_frame = tk.LabelFrame(
            control_frame,
            text="📈 Kết Quả",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=10,
            width=30,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.WORD
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_overview_tab(self):
        """Thiết lập tab tổng quan"""
        # Search bar
        search_frame = tk.Frame(self.overview_tab, bg=BACKGROUND_COLOR)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            search_frame,
            text="🔍 Tìm kiếm:",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_overview)
        
        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=(FONT_FAMILY, 10),
            width=40,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief=tk.SOLID,
            bd=1,
            highlightthickness=0
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Treeview for schedule
        tree_frame = tk.Frame(self.overview_tab, bg=BACKGROUND_COLOR)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('Môn Học', 'Giáo Viên', 'Phòng', 'Thời Gian', 'Lớp')
        self.overview_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            height=20
        )
        
        v_scroll.config(command=self.overview_tree.yview)
        h_scroll.config(command=self.overview_tree.xview)
        
        # Column headings
        self.overview_tree.heading('Môn Học', text='Môn Học')
        self.overview_tree.heading('Giáo Viên', text='Giáo Viên')
        self.overview_tree.heading('Phòng', text='Phòng')
        self.overview_tree.heading('Thời Gian', text='Thời Gian')
        self.overview_tree.heading('Lớp', text='Lớp')
        
        # Column widths
        equal_width = 240
        for col in columns:
            self.overview_tree.column(col, width=equal_width, anchor=tk.W, stretch=False)
        
        # Pack
        self.overview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Styling
        # Tag colors
        self.overview_tree.tag_configure('evenrow',
                                         background=BACKGROUND_COLOR,
                                         foreground=TEXT_COLOR)
        self.overview_tree.tag_configure('oddrow',
                                         background=ACCENT_COLOR,
                                         foreground='white')
    
    def setup_teacher_tab(self, parent):
        """Thiết lập tab lịch giáo viên"""
        # Teacher selection
        select_frame = tk.Frame(self.teacher_tab, bg=BACKGROUND_COLOR)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            select_frame,
            text="👨‍🏫 Chọn giáo viên:",
            font=(FONT_FAMILY, 11, 'bold'),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.teacher_combo = ttk.Combobox(
            select_frame,
            font=(FONT_FAMILY, 10),
            state='readonly',
            width=40
        )
        self.teacher_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.teacher_combo.bind('<<ComboboxSelected>>', self.on_teacher_select)
        
        # Teacher schedule display
        schedule_frame = tk.Frame(self.teacher_tab, bg=BACKGROUND_COLOR)
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL)
        h_scroll = ttk.Scrollbar(schedule_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('Thứ', 'Tiết', 'Môn Học', 'Phòng', 'Thời Gian')
        self.teacher_tree = ttk.Treeview(
            schedule_frame,
            columns=columns,
            show='headings',
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            height=25
        )
        
        v_scroll.config(command=self.teacher_tree.yview)
        h_scroll.config(command=self.teacher_tree.xview)
        
        # Column headings
        self.teacher_tree.heading('Thứ', text='Thứ')
        self.teacher_tree.heading('Tiết', text='Tiết')
        self.teacher_tree.heading('Môn Học', text='Môn Học')
        self.teacher_tree.heading('Phòng', text='Phòng')
        self.teacher_tree.heading('Thời Gian', text='Thời Gian')
        
        # Column widths
        teacher_col_width = 200
        for col in columns:
            self.teacher_tree.column(col, width=teacher_col_width, anchor=tk.W, stretch=False)
        
        # Pack
        self.teacher_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Tag colors
        self.teacher_tree.tag_configure('evenrow',
                                        background=BACKGROUND_COLOR,
                                        foreground=TEXT_COLOR)
        self.teacher_tree.tag_configure('oddrow',
                                        background=ACCENT_COLOR,
                                        foreground='white')
        self.teacher_tree.tag_configure('header',
                                        background=PRIMARY_COLOR,
                                        foreground='white',
                                        font=(FONT_FAMILY, 10, 'bold'))
    
    def load_data(self):
        """Load dữ liệu từ file"""
        self.update_status("Đang tải dữ liệu...")
        try:
            self.teachers, self.rooms, self.courses, self.timeslots = load_all_data()
            self.evaluator = ScheduleEvaluator(self.courses, self.rooms, self.teachers, self.timeslots)
            self.constraint_checker = ConstraintChecker(self.courses, self.rooms, self.teachers, self.timeslots)
            # Đã thêm: Khởi tạo SchedulePrinter sau khi dữ liệu được tải
            self.printer = SchedulePrinter(self.courses, self.rooms, self.teachers, self.timeslots)
            
            # Update info
            self.update_info_text()
            self.update_teacher_combo()
            
            self.update_status("✓ Đã tải dữ liệu thành công")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu:\n{str(e)}")
            self.update_status("✗ Lỗi khi tải dữ liệu")
    
    def update_info_text(self):
        """Cập nhật thông tin dữ liệu"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = f"""
📚 Môn học: {len(self.courses)}
👨‍🏫 Giáo viên: {len(self.teachers)}
🏫 Phòng học: {len(self.rooms)}
⏰ Khung giờ: {len(self.timeslots)}
        """
        
        self.info_text.insert(1.0, info.strip())
        self.info_text.config(state=tk.DISABLED)
    
    def update_teacher_combo(self):
        """Cập nhật combobox giáo viên"""
        if self.teachers:
            teacher_names = [f"{t.id} - {t.name}" for t in self.teachers.values()]
            self.teacher_combo['values'] = sorted(teacher_names)
    
    def on_algo_change(self):
        """Xử lý khi thay đổi thuật toán"""
        if self.algo_var.get() == "gwo":
            self.gwo_params_frame.pack(fill=tk.X, pady=(0, 20))
        else:
            self.gwo_params_frame.pack_forget()
    
    def run_algorithm(self):
        """Chạy thuật toán đã chọn"""
        if not self.courses:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu!")
            return
        
        self.run_button.config(state=tk.DISABLED)
        self.compare_button.config(state=tk.DISABLED)
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=self._run_algorithm_thread)
        thread.daemon = True
        thread.start()
    
    def _run_algorithm_thread(self):
        """Thread chạy thuật toán"""
        algo = self.algo_var.get()
        
        try:
            if algo == "backtracking":
                self.update_status("Đang chạy Backtracking...")
                self.update_results("🔄 Đang chạy Backtracking...\n")
                
                solver = BacktrackingSolver(self.courses, self.rooms, self.teachers, self.timeslots)
                start_time = time.time()
                # Sử dụng 'solve' đã được định nghĩa trong BacktrackingSolver
                schedule = solver.solve(verbose=False) 
                elapsed = time.time() - start_time
                
                self._process_result(schedule, elapsed, "BACKTRACKING")
                
            else: # GWO
                try:
                    population = int(self.population_var.get())
                    iterations = int(self.iterations_var.get())
                except ValueError:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", "Tham số GWO không hợp lệ! Vui lòng nhập số nguyên."))
                    # Bật lại nút nếu lỗi
                    self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.compare_button.config(state=tk.NORMAL))
                    return
                
                self.update_status("Đang chạy GWO...")
                self.update_results(f"🔄 Đang chạy GWO...\nPopulation: {population}, Iterations: {iterations}\n")
                
                solver = GWOSolver(self.courses, self.rooms, self.teachers, self.timeslots)
                start_time = time.time()
                # Sử dụng 'solve' đã được định nghĩa trong GWOSolver
                schedule = solver.solve(population_size=population, max_iterations=iterations, verbose=False) 
                elapsed = time.time() - start_time
                
                self._process_result(schedule, elapsed, "GWO")
        
        except Exception as e:
            # Xử lý lỗi chung khi chạy thuật toán
            self.update_results(f"❌ Lỗi xảy ra trong quá trình chạy thuật toán: {str(e)}")
            self.update_status("✗ Lỗi chạy thuật toán")

        finally:
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.compare_button.config(state=tk.NORMAL))
    
    def _process_result(self, schedule, elapsed, algo_name):
        """Xử lý kết quả thuật toán"""
        if schedule and len(schedule.assignments) > 0:
            self.current_schedule = schedule
            
            # Đánh giá
            fitness = self.evaluator.evaluate(schedule)
            is_valid = self.constraint_checker.is_valid_schedule(schedule)
            assigned = len(schedule.assignments)
            total = len(self.courses)
            
            # Hiển thị kết quả
            result_text = f"""
✓ Hoàn thành {algo_name}!
⏱️ Thời gian: {elapsed:.2f}s
📊 Fitness: {fitness:.2f}/100
✅ Hợp lệ: {'Có' if is_valid else 'Không' if assigned < total else 'Có (Kiểm tra lại)'}
📚 Môn đã gán: {assigned}/{total}
            """
            
            self.update_results(result_text.strip())
            self.update_status(f"✓ {algo_name} hoàn thành - Fitness: {fitness:.2f}")
            
            # Hiển thị lịch (gọi từ main thread)
            self.root.after(0, self.display_schedule)
        else:
            self.current_schedule = None # Đảm bảo lịch cũ bị xóa nếu không tìm thấy
            self.update_results(f"✗ {algo_name} không tìm thấy lịch hợp lệ hoặc không gán được môn nào!")
            self.update_status(f"✗ {algo_name} thất bại")
    
    def compare_algorithms(self):
        """So sánh 2 thuật toán"""
        if not self.courses:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu!")
            return
        
        self.run_button.config(state=tk.DISABLED)
        self.compare_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._compare_thread)
        thread.daemon = True
        thread.start()
    
    def _compare_thread(self):
        """Thread so sánh thuật toán"""
        self.update_status("Đang so sánh thuật toán...")
        self.update_results("⚖️ BẮT ĐẦU SO SÁNH\n" + "="*40 + "\n")
        
        results = {}
        total = len(self.courses)
        
        # --- 1. Backtracking ---
        try:
            self.update_results("\n[1/2] Chạy Backtracking...\n")
            solver_bt = BacktrackingSolver(self.courses, self.rooms, self.teachers, self.timeslots)
            start_bt = time.time()
            bt_schedule = solver_bt.solve(verbose=False)
            bt_time = time.time() - start_bt
            
            if bt_schedule and len(bt_schedule.assignments) > 0:
                results['bt'] = {
                    'schedule': bt_schedule,
                    'time': bt_time,
                    'fitness': self.evaluator.evaluate(bt_schedule),
                    'valid': self.constraint_checker.is_valid_schedule(bt_schedule),
                    'assigned': len(bt_schedule.assignments)
                }
                self.update_results(f"Backtracking: Hoàn thành trong {bt_time:.2f}s, Fitness: {results['bt']['fitness']:.2f}\n")
            else:
                self.update_results("Backtracking: Không tìm được lịch.\n")
        except Exception as e:
            self.update_results(f"Lỗi Backtracking: {str(e)}\n")

        # --- 2. GWO ---
        try:
            population = 20
            iterations = 100
            self.update_results(f"\n[2/2] Chạy GWO (Pop={population}, Iter={iterations})...\n")
            solver_gwo = GWOSolver(self.courses, self.rooms, self.teachers, self.timeslots)
            start_gwo = time.time()
            # Giả định tham số GWO là cố định 20, 100 cho so sánh
            gwo_schedule = solver_gwo.solve(population_size=population, max_iterations=iterations, verbose=False) 
            gwo_time = time.time() - start_gwo
            
            if gwo_schedule and len(gwo_schedule.assignments) > 0:
                results['gwo'] = {
                    'schedule': gwo_schedule,
                    'time': gwo_time,
                    'fitness': self.evaluator.evaluate(gwo_schedule),
                    'valid': self.constraint_checker.is_valid_schedule(gwo_schedule),
                    'assigned': len(gwo_schedule.assignments)
                }
                self.update_results(f"GWO: Hoàn thành trong {gwo_time:.2f}s, Fitness: {results['gwo']['fitness']:.2f}\n")
            else:
                 self.update_results("GWO: Không tìm được lịch.\n")
        except Exception as e:
             self.update_results(f"Lỗi GWO: {str(e)}\n")
        
        # --- 3. Hiển thị so sánh ---
        compare_text = f"\n{'='*40}\nKẾT QUẢ SO SÁNH\n{'='*40}\n"
        
        best_algo = ''
        best_fitness = -1.0
        
        if 'bt' in results:
            bt = results['bt']
            compare_text += f"\n**BACKTRACKING**:\n"
            compare_text += f"  ⏱️ Thời gian: {bt['time']:.2f}s\n"
            compare_text += f"  📊 Fitness: {bt['fitness']:.2f}/100\n"
            compare_text += f"  ✅ Hợp lệ: {'Có' if bt['valid'] else 'Không'}\n"
            compare_text += f"  📚 Đã gán: {bt['assigned']}/{total}\n"
            if bt['fitness'] > best_fitness:
                 best_fitness = bt['fitness']
                 self.current_schedule = bt['schedule']
                 best_algo = "Backtracking"
        
        if 'gwo' in results:
            gwo = results['gwo']
            compare_text += f"\n**GWO**:\n"
            compare_text += f"  ⏱️ Thời gian: {gwo['time']:.2f}s\n"
            compare_text += f"  📊 Fitness: {gwo['fitness']:.2f}/100\n"
            compare_text += f"  ✅ Hợp lệ: {'Có' if gwo['valid'] else 'Không'}\n"
            compare_text += f"  📚 Đã gán: {gwo['assigned']}/{total}\n"
            if gwo['fitness'] > best_fitness:
                 best_fitness = gwo['fitness']
                 self.current_schedule = gwo['schedule']
                 best_algo = "GWO"
        
        if best_algo:
            compare_text += f"\n**TỔNG KẾT**: Lịch **{best_algo}** tốt nhất (Fitness: {best_fitness:.2f}) được hiển thị.\n"
        else:
             compare_text += f"\nKhông có thuật toán nào tạo được lịch.\n"


        self.update_results(compare_text)
        self.update_status("✓ So sánh hoàn tất")
        
        if self.current_schedule:
            self.root.after(0, self.display_schedule)
        else:
             self.root.after(0, self.clear_schedule_display)

        self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.compare_button.config(state=tk.NORMAL))

    def clear_schedule_display(self):
        """Xóa hiển thị lịch trên overview và teacher tabs."""
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)
        self.overview_tree.insert('', tk.END, values=('Chưa có lịch được tạo.', '', '', '', ''))

    def display_schedule(self):
        """Hiển thị lịch trong overview tab (Tổng quan lịch)"""
        # Xóa dữ liệu cũ
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)
        
        if not self.current_schedule or not self.current_schedule.assignments:
            self.clear_schedule_display()
            return
        
        # Kiểm tra sự tồn tại của printer (đã được khởi tạo trong load_data)
        if self.printer is None:
            self.overview_tree.insert('', tk.END, values=('Lỗi: Không tìm thấy trình in (printer).', '', '', '', ''))
            return

        # 1. LẤY DỮ LIỆU TỪ SchedulePrinter
        schedule_data = self.printer.get_schedule_data_for_gui(self.current_schedule)
        
        # 2. Thêm vào tree
        for idx, item in enumerate(schedule_data):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            # Đảm bảo thứ tự keys/values khớp với columns đã định nghĩa trong setup_overview_tab:
            # ('Môn Học', 'Giáo Viên', 'Phòng', 'Thời Gian', 'Lớp')
            self.overview_tree.insert('', tk.END, values=(
                item['Môn Học'],
                item['Giáo Viên'],
                item['Phòng'],
                item['Thời Gian'],
                item['Lớp']
            ), tags=(tag,))
        
        # Cập nhật lịch giáo viên nếu có giáo viên đang được chọn
        if self.teacher_combo.get():
             self.on_teacher_select(None)

    def filter_overview(self, *args):
        """Lọc lịch theo từ khóa tìm kiếm (Tên môn, GV, Phòng, Thời gian)"""
        search_text = self.search_var.get().lower()

        # Xóa hiển thị cũ
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)

        if not self.current_schedule or not self.current_schedule.assignments or not self.printer:
            return

        # Lấy toàn bộ dữ liệu đã được sắp xếp và định dạng từ printer
        all_schedule_data = self.printer.get_schedule_data_for_gui(self.current_schedule)
        
        filtered_data = []
        for item in all_schedule_data:
            # Tạo chuỗi tìm kiếm từ các cột hiển thị
            searchable = f"{item['Môn Học']} {item['Giáo Viên']} {item['Phòng']} {item['Thời Gian']} {item['Lớp']} {item['Thứ']}".lower()
            
            if not search_text or search_text in searchable:
                filtered_data.append(item)

        # Hiển thị dữ liệu đã lọc
        for idx, item in enumerate(filtered_data):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.overview_tree.insert('', tk.END, values=(
                item['Môn Học'],
                item['Giáo Viên'],
                item['Phòng'],
                item['Thời Gian'],
                item['Lớp']
            ), tags=(tag,))
    
    def on_teacher_select(self, event):
        """Xử lý khi chọn giáo viên (Lịch theo giáo viên)"""
        selection = self.teacher_combo.get()
        
        # Xóa dữ liệu cũ
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)

        if not selection or not self.current_schedule or not self.current_schedule.assignments:
            self.teacher_tree.insert('', tk.END, values=('', '', 'Chưa có lịch tổng thể được tạo.', '', ''))
            return
        
        # Lấy teacher_id từ selection (ví dụ: "GV01 - Nguyễn Văn A" -> "GV01")
        teacher_id = selection.split(' - ')[0]
        
        # Lọc lịch theo giáo viên
        teacher_schedule = []
        for assignment in self.current_schedule.assignments:
            if assignment.teacher_id == teacher_id:
                course = self.courses.get(assignment.course_id)
                room = self.rooms.get(assignment.room_id)
                timeslot = self.timeslots.get(assignment.timeslot_id)
                
                if not all([course, room, timeslot]): continue
                
                teacher_schedule.append({
                    'day': timeslot.day,
                    'day_num': SchedulePrinter._get_day_number(timeslot.day), # Sửa: dùng static method để sắp xếp
                    'period': timeslot.period,
                    'period_str': f"Tiết {timeslot.period} ({timeslot.session})",
                    'course': course.name,
                    'room': room.name,
                    'time': timeslot.time # Sửa: dùng timeslot.time
                })
        
        if not teacher_schedule:
            self.teacher_tree.insert('', tk.END, values=(
                '', '', 'Giáo viên chưa có lịch dạy', '', ''
            ))
            return
        
        # Sắp xếp theo thứ và tiết (dùng day_num để sắp xếp đúng)
        teacher_schedule.sort(key=lambda x: (x['day_num'], x['period']))
        
        # Thêm vào tree
        for idx, item in enumerate(teacher_schedule):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.teacher_tree.insert('', tk.END, values=(
                item['day'],
                item['period_str'],
                item['course'],
                item['room'],
                item['time']
            ), tags=(tag,))
    
    def clear_results(self):
        """Xóa kết quả"""
        # Xóa lịch hiện tại
        self.current_schedule = None
        
        # Xóa overview
        self.clear_schedule_display()
        
        # Xóa results text
        self.results_text.delete(1.0, tk.END)
        
        # Reset search
        self.search_var.set('')
        
        self.update_status("Đã xóa kết quả")
    
    def update_status(self, message):
        """Cập nhật status bar"""
        self.root.after(0, lambda: self.status_bar.config(text=message))
    
    def update_results(self, text):
        """Cập nhật results text"""
        def _update():
            self.results_text.insert(tk.END, text + "\n")
            self.results_text.see(tk.END)
        self.root.after(0, _update)


def main():
    root = tk.Tk()
    app = ScheduleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()