#!/usr/bin/env python3
"""
SmartLibrary Management System - Complete GUI Application
Professional library management system with modern interface
Single-file implementation with all components included
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import sys
import os

# Try to import optional dependencies with fallbacks
try:
    from tkcalendar import DateEntry

    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False
    print("Warning: tkcalendar not installed. Date pickers will use simple entry fields.")

try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *

    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False
    print("Warning: ttkbootstrap not installed. Using standard tkinter.")
    # Create dummy constants for compatibility
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"


# ============================================================================
# MOCK DATABASE FOR DEMONSTRATION
# ============================================================================

class MockDatabase:
    class DatabaseConnection:
        def __init__(self):
            self.config = {
                'host': 'localhost',
                'user': 'postgressql',
                'password': 'ADMIN123',  # Change this
                'database': 'smartlibrary',
                'port': 5432  # Default MySQL port
            }
    """Mock database for demonstration purposes"""

    # Sample data for demonstration
    SAMPLE_BOOKS = [
        (1, "The Great Gatsby", "F. Scott Fitzgerald", "978074323565", 3, 5, "Available", "Fiction"),
        (2, "1984", "Georgy Orwell", "97804514935", 0, 3, "Borrowed", "Fiction"),
        (3, "Kill a Mockingbird", "Harper Lee", "80061120084", 2, 4, "Available", "Fiction"),
        (4, "The Silent Patients", "Alex Michaelides", "97810301697", 1, 2, "Available", "Mystery"),
        (5, "Educated", "Tara Westover", "9780399590504", 0, 1, "Borrowed", "Biography"),
        (6, "Sapiens", "Yuval Novah Harari", "9780062316097", 4, 5, "Available", "History"),
        (7, "Atomic Habits", "James Clear", "9780735211292", 2, 3, "Available", "Self-Help"),
        (8, "The Vinci Code", "Dan Brown", "9780307278", 0, 2, "Borrowed", "Mystery"),
        (9, "The Great Gatsby", "F. Scott Fitzgerald", "978074323565", 3, 5, "Available", "Fiction"),
        (10, "1985", "George Orwell", "978045152435", 0, 3, "Borrowed", "Fiction"),
        (11, "To Kill Mockingbird", "Harper Lee", "97800611284", 2, 4, "Available", "Fiction"),
        (12, "The Silence Patient", "Alex Michaelides", "978125301697", 1, 2, "Available", "Mystery"),
        (13, "Educate", "Tara Westover", "97399590504", 0, 1, "Borrowed", "Biography"),
        (14, "Sapiens", "Yuval Noah Harari", "97800316097", 4, 5, "Available", "History"),
        (15, "Atomic Habits", "James Clear", "9780735211292", 2, 3, "Available", "Self-Help"),
        (16, "The Da Vinci Coode", "Dan Brown", "978030474278", 0, 2, "Borrowed", "Mystery"),
        (17, "Sapiens", "Yuval Noah Harari", "97800316097", 4, 5, "Available", "History"),
        (18, "Atomic Habits", "James Clear", "9780735211292", 2, 3, "Available", "Self-Help"),
        (19, "The Da Vinci Coode", "Dan Brown", "978030474278", 0, 2, "Borrowed", "Mystery"),
        (20, "The Da Vinci Coode", "Dan Brown", "978030474278", 0, 2, "Borrowed", "Mystery"),
    ]

    SAMPLE_MEMBERS = [
        (1, "John Doe", "MEM1001", "john@example.com", "555-0101", "Premium", 2, "Active"),
        (2, "Jane Smith", "MEM1002", "jane@example.com", "555-0102", "Standard", 0, "Active"),
        (3, "Bob Johnson", "MEM1003", "bob@example.com", "555-0103", "Student", 1, "Active"),
        (4, "Alice Brown", "MEM1004", "alice@example.com", "555-0104", "Premium", 3, "Active"),
        (5, "Charlie Wilson", "MEM1005", "charlie@example.com", "555-0105", "Standard", 2, "Inactive"),
        (6, "Diana Miller", "MEM1006", "diana@example.com", "555-0106", "Student", 0, "Active"),
        (7, "John Doe", "MEM1001", "john@example.com", "555-0101", "Premium", 2, "Active"),
        (8, "Jane Smith", "MEM1002", "jane@example.com", "555-0102", "Standard", 0, "Active"),
        (9, "Bob Johnson", "MEM1003", "bob@example.com", "555-0103", "Student", 1, "Active"),
        (10, "Alice Brown", "MEM1004", "alice@example.com", "555-0104", "Premium", 3, "Active"),
        (11, "Charlie Wilson", "MEM1005", "charlie@example.com", "555-0105", "Standard", 2, "Inactive"),
        (12, "Diana Miller", "MEM1006", "diana@example.com", "555-0106", "Student", 0, "Active"),
    ]

    SAMPLE_ACTIVE_LOANS = [
        (101, "The Great Gatsby", "John Doe", "2025-12-01", "2025-12-15", "Active", "$0.00"),
        (102, "1984", "Jane Smith", "2025-11-28", "2025-12-12", "Active", "$0.00"),
        (103, "The Great Gatsby", "John Doe", "2025-12-01", "2025-12-15", "Active", "$0.00"),
        (104, "1984", "Jane Smith", "2025-11-28", "2025-12-12", "Active", "$0.00"),
        (105, "The Great Gatsby", "John Doe", "2025-12-01", "2025-12-15", "Active", "$0.00"),
        (106, "1984", "Jane Smith", "2025-11-28", "2025-12-12", "Active", "$0.00"),
        (107, "The Great Gatsby", "John Doe", "2025-12-01", "2025-12-15", "Active", "$0.00"),
        (108, "1984", "Jane Smith", "2025-11-28", "2025-12-12", "Active", "$0.00"),
        (109, "The Great Gatsby", "John Doe", "2025-12-01", "2025-12-15", "Active", "$0.00"),
        (110, "1984", "Jane Smith", "2025-11-28", "2025-12-12", "Active", "$0.00"),
    ]

    SAMPLE_OVERDUE_LOANS = [
        (201, "To Kill a Mockingbird", "Bob Johnson", "2025-11-15", "2025-11-29", "Overdue", "$8.00"),
        (202, "The Silent Patient", "Alice Brown", "2025-11-20", "2025-12-04", "Overdue", "$0.50"),
        (203, "To Kill a Mockingbird", "Bob Johnson", "2025-11-15", "2025-11-29", "Overdue", "$8.00"),
        (204, "The Silent Patient", "Alice Brown", "2025-11-20", "2025-12-04", "Overdue", "$0.50"),
        (205, "To Kill a Mockingbird", "Bob Johnson", "2025-11-15", "2025-11-29", "Overdue", "$8.00"),
        (206, "The Silent Patient", "Alice Brown", "2025-11-20", "2025-12-04", "Overdue", "$0.50"),
        (207, "To Kill a Mockingbird", "Bob Johnson", "2025-11-15", "2025-11-29", "Overdue", "$8.00"),
        (208, "The Silent Patient", "Alice Brown", "2025-11-20", "2025-12-04", "Overdue", "$0.50"),
    ]

    SAMPLE_FINES = [
        (1, "Joe Doe", "The Great Gatsby", "$5.50", "2025-12-01", "2025-12-15", "Pending"),
        (2, "Jan Smith", "1984", "$3.00", "2025-11-28", "2025-12-12", "Paid"),
        (3, "Bobi Johnson", "To Kill a Mockingbird", "$8.00", "2025-11-15", "2025-11-29", "Pending"),
        (4, "Alie Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (5, "Charlie Wilsson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (6, "Alice Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (7, "Charlie Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (8, "Charlie Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (9, "Alice Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (10, "Charlie Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (11, "Charles Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (12, "Alima Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (13, "Chrise Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (14, "Charlie Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (15, "Alic Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (16, "Charie Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (18, "foday Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (19, "Moses Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (20, "pastor Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (21, "Alusine Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),
        (22, "Koroma Brown", "The Silent Patient", "$0.50", "2025-11-20", "2025-12-04", "Waived"),
        (23, "saffa Wilson", "Sapiens", "$12.00", "2025-10-10", "2025-10-24", "Paid"),


    ]

    @staticmethod
    def get_connection():
        return MockConnection()

    @staticmethod
    def return_connection(conn):
        pass


class MockConnection:
    def cursor(self):
        return MockCursor()

    def commit(self):
        pass

    def rollback(self):
        pass


class MockCursor:
    def __init__(self):
        self._rowcount = 0

    def execute(self, query, params=None):
        print(f"Executing: {query}")
        if params:
            print(f"Params: {params}")
        return self

    def fetchall(self):
        # Return appropriate sample data based on query
        query = str(getattr(self, '_last_query', ''))
        if 'books' in query.lower() and 'author' in query.lower():
            return MockDatabase.SAMPLE_BOOKS
        elif 'users' in query.lower():
            return [('admin', 'admin')]
        elif 'count' in query.lower():
            return [(42,)]  # Sample count
        return []

    def fetchone(self):
        # For authentication
        return ('admin', 'admin')

    @property
    def rowcount(self):
        return self._rowcount


# Use mock database for demonstration
DatabaseConnection = MockDatabase


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class SmartLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartLibrary Management System")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)

        # Configure style based on available packages
        if HAS_TTKBOOTSTRAP:
            self.style = tb.Style(theme="flatly")
        else:
            self.style = None

        self.setup_styles()

        # User session
        self.current_user = None
        self.user_role = None

        # Setup main application
        self.setup_main_window()

    def setup_styles(self):
        """Configure custom styles"""
        if HAS_TTKBOOTSTRAP:
            self.style.configure("Title.TLabel", font=("Helvetica", 25, "bold"))
            self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
            self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))
            self.style.configure("Success.TLabel", foreground="#28a745")
            self.style.configure("Warning.TLabel", foreground="#ffc107")
            self.style.configure("Danger.TLabel", foreground="#dc3545")
            self.style.configure("Info.TLabel", foreground="#17a2b8")

    def setup_main_window(self):
        """Setup the main application window with navigation"""
        # Create main container
        if HAS_TTKBOOTSTRAP:
            self.main_container = tb.Frame(self.root)
        else:
            self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Show login screen initially
        self.show_login_screen()

    def show_login_screen(self):
        """Display login screen"""
        self.clear_main_container()

        # Login frame
        if HAS_TTKBOOTSTRAP:
            login_frame = tb.Frame(self.main_container, padding=50)
        else:
            login_frame = tk.Frame(self.main_container, padx=50, pady=50)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Logo/Title
        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                login_frame,
                text="SmartLibrary",
                font=("Helvetica", 36, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                login_frame,
                text="SmartLibrary",
                font=("Helvetica", 36, "bold"),
                fg="blue"
            )
        title_label.pack(pady=(0, 40))

        if HAS_TTKBOOTSTRAP:
            subtitle_label = tb.Label(
                login_frame,
                text="Management System",
                font=("Helvetica", 16)
            )
        else:
            subtitle_label = tk.Label(
                login_frame,
                text="Management System",
                font=("Helvetica", 16)
            )
        subtitle_label.pack(pady=(0, 40))

        # Username
        username_label = tk.Label(login_frame, text="Username", font=("Helvetica", 11))
        username_label.pack(anchor=tk.W, pady=(0, 5))

        if HAS_TTKBOOTSTRAP:
            self.username_entry = tb.Entry(login_frame, width=30, font=("Helvetica", 11))
        else:
            self.username_entry = tk.Entry(login_frame, width=30, font=("Helvetica", 11))
        self.username_entry.pack(pady=(0, 20))
        self.username_entry.insert(0, "admin")

        # Password
        password_label = tk.Label(login_frame, text="Password", font=("Helvetica", 11))
        password_label.pack(anchor=tk.W, pady=(0, 5))

        if HAS_TTKBOOTSTRAP:
            self.password_entry = tb.Entry(login_frame, width=30, show="*", font=("Helvetica", 11))
        else:
            self.password_entry = tk.Entry(login_frame, width=30, show="*", font=("Helvetica", 11))
        self.password_entry.pack(pady=(0, 30))
        self.password_entry.insert(0, "admin123")

        # Login button
        if HAS_TTKBOOTSTRAP:
            login_btn = tb.Button(
                login_frame,
                text="Login",
                command=self.login,
                width=20,
                bootstyle=PRIMARY
            )
        else:
            login_btn = tk.Button(
                login_frame,
                text="Login",
                command=self.login,
                width=20,
                bg="blue",
                fg="gray"
            )
        login_btn.pack(pady=(0, 20))

        # Demo credentials
        if HAS_TTKBOOTSTRAP:
            demo_label = tb.Label(
                login_frame,
                text="Demo: admin / FICT123",
                font=("Helvetica", 9),
                bootstyle=SECONDARY
            )
        else:
            demo_label = tk.Label(
                login_frame,
                text="Demo: admin / FICT123",
                font=("Helvetica", 9),
                fg="gray"
            )
        demo_label.pack()

        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())

    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        # Simple authentication for demo
        if username == "GROUP E" and password == "FICT123":
            self.current_user = "admin"
            self.user_role = "admin"
            self.show_main_interface()
        elif username == "librarian" and password == "librarian123":
            self.current_user = "librarian"
            self.user_role = "librarian"
            self.show_main_interface()
        elif username == "member" and password == "member123":
            self.current_user = "member"
            self.user_role = "member"
            self.show_main_interface()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_main_interface(self):
        """Show main application interface after login"""
        self.clear_main_container()
        self.root.unbind('<Return>')

        # Create header
        self.create_header()

        # Create main content area
        self.create_main_content()

        # Create footer
        self.create_footer()

        # Show dashboard by default
        self.show_dashboard()

    def create_header(self):
        """Create application header"""
        if HAS_TTKBOOTSTRAP:
            header_frame = tb.Frame(self.main_container, bootstyle=PRIMARY)
        else:
            header_frame = tk.Frame(self.main_container, bg="blue")
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        # Logo/Title
        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                header_frame,
                text="SmartLibrary",
                font=("Helvetica", 20, "bold"),
                bootstyle="inverse-primary"
            )
        else:
            title_label = tk.Label(
                header_frame,
                text="SmartLibrary",
                font=("Helvetica", 20, "bold"),
                fg="white",
                bg="blue"
            )
        title_label.pack(side=tk.LEFT, padx=10)

        # Navigation menu
        nav_frame = tk.Frame(header_frame)
        nav_frame.pack(side=tk.LEFT, padx=50)

        # Dashboard button
        if HAS_TTKBOOTSTRAP:
            dashboard_btn = tb.Button(
                nav_frame,
                text="Dashboard",
                command=self.show_dashboard,
                bootstyle="link"
            )
        else:
            dashboard_btn = tk.Button(
                nav_frame,
                text="Dashboard",
                command=self.show_dashboard,
                bg="blue",
                fg="gray",
                relief=tk.FLAT
            )
        dashboard_btn.pack(side=tk.LEFT, padx=10)

        # Books button
        if HAS_TTKBOOTSTRAP:
            books_btn = tb.Button(
                nav_frame,
                text="Books",
                command=self.show_books,
                bootstyle="link"
            )
        else:
            books_btn = tk.Button(
                nav_frame,
                text="Books",
                command=self.show_books,
                bg="blue",
                fg="white",
                relief=tk.FLAT
            )
        books_btn.pack(side=tk.LEFT, padx=10)

        # Members button (only for admin/librarian)
        if self.user_role in ['admin', 'librarian']:
            if HAS_TTKBOOTSTRAP:
                members_btn = tb.Button(
                    nav_frame,
                    text="Members",
                    command=self.show_members,
                    bootstyle="link"
                )
            else:
                members_btn = tk.Button(
                    nav_frame,
                    text="Members",
                    command=self.show_members,
                    bg="blue",
                    fg="white",
                    relief=tk.FLAT
                )
            members_btn.pack(side=tk.LEFT, padx=10)

        # Loans button
        if HAS_TTKBOOTSTRAP:
            loans_btn = tb.Button(
                nav_frame,
                text="Loans",
                command=self.show_loans,
                bootstyle="link"
            )
        else:
            loans_btn = tk.Button(
                nav_frame,
                text="Loans",
                command=self.show_loans,
                bg="blue",
                fg="white",
                relief=tk.FLAT
            )
        loans_btn.pack(side=tk.LEFT, padx=10)

        # Fines button
        if HAS_TTKBOOTSTRAP:
            fines_btn = tb.Button(
                nav_frame,
                text="Fines",
                command=self.show_fines,
                bootstyle="link"
            )
        else:
            fines_btn = tk.Button(
                nav_frame,
                text="Fines",
                command=self.show_fines,
                bg="blue",
                fg="white",
                relief=tk.FLAT
            )
        fines_btn.pack(side=tk.LEFT, padx=10)

        # Reports button (only for admin/librarian)
        if self.user_role in ['admin', 'librarian']:
            if HAS_TTKBOOTSTRAP:
                reports_btn = tb.Button(
                    nav_frame,
                    text="Reports",
                    command=self.show_reports,
                    bootstyle="link"
                )
            else:
                reports_btn = tk.Button(
                    nav_frame,
                    text="Reports",
                    command=self.show_reports,
                    bg="blue",
                    fg="white",
                    relief=tk.FLAT
                )
            reports_btn.pack(side=tk.LEFT, padx=10)

        # User info and logout
        user_frame = tk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT, padx=10)

        if HAS_TTKBOOTSTRAP:
            user_label = tb.Label(
                user_frame,
                text=f"{self.current_user} ({self.user_role})",
                font=("Helvetica", 10),
                bootstyle="inverse-primary"
            )
            logout_btn = tb.Button(
                user_frame,
                text="Logout",
                command=self.logout,
                bootstyle="outline-danger"
            )
        else:
            user_label = tk.Label(
                user_frame,
                text=f"{self.current_user} ({self.user_role})",
                font=("Helvetica", 10),
                fg="white",
                bg="blue"
            )
            logout_btn = tk.Button(
                user_frame,
                text="Logout",
                command=self.logout,
                bg="red",
                fg="yellow"
            )
        user_label.pack(side=tk.LEFT, padx=10)
        logout_btn.pack(side=tk.LEFT)

    def create_main_content(self):
        """Create main content area"""
        if HAS_TTKBOOTSTRAP:
            self.content_frame = tb.Frame(self.main_container)
        else:
            self.content_frame = tk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def create_footer(self):
        """Create application footer"""
        if HAS_TTKBOOTSTRAP:
            footer_frame = tb.Frame(self.main_container, bootstyle=SECONDARY)
        else:
            footer_frame = tk.Frame(self.main_container, bg="gray")
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

        if HAS_TTKBOOTSTRAP:
            status_label = tb.Label(
                footer_frame,
                text="SmartLibrary Management System v1.0",
                font=("Helvetica", 9),
                bootstyle="inverse-secondary"
            )
            time_label = tb.Label(
                footer_frame,
                text="",
                font=("Helvetica", 9),
                bootstyle="inverse-secondary"
            )
        else:
            status_label = tk.Label(
                footer_frame,
                text="SmartLibrary Management System v1.0",
                font=("Helvetica", 9),
                fg="white",
                bg="gray"
            )
            time_label = tk.Label(
                footer_frame,
                text="",
                font=("Helvetica", 9),
                fg="white",
                bg="gray"
            )
        status_label.pack(side=tk.LEFT, padx=10)
        time_label.pack(side=tk.RIGHT, padx=10)

        # Update time
        def update_time():
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_label.config(text=current_time)
            self.root.after(1000, update_time)

        update_time()

    def clear_main_container(self):
        """Clear all widgets from main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def clear_content_frame(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Show dashboard with statistics"""
        self.clear_content_frame()

        # Dashboard title
        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                self.content_frame,
                text="Dashboard",
                font=("Helvetica", 24, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                self.content_frame,
                text="Dashboard",
                font=("Helvetica", 24, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Statistics cards
        stats_frame = tk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 30))

        # Statistics data
        stats_data = [
            ("Total Books", "20", "books", PRIMARY),
            ("Available Books", "20", "books", SUCCESS),
            ("Active Loans", "10", "loans", INFO),
            ("Overdue Loans", "10", "loans", WARNING),
            ("Active Members", "12", "members", SECONDARY),
            ("Pending Fines", "18", "fines", DANGER)
        ]

        for i, (title, value, unit, style) in enumerate(stats_data):
            if HAS_TTKBOOTSTRAP:
                card_frame = tb.Frame(stats_frame, bootstyle="light", padding=20)
            else:
                card_frame = tk.Frame(stats_frame, relief=tk.RAISED, borderwidth=1, padx=20, pady=20)
            card_frame.grid(row=0, column=i, padx=10, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)

            title_label = tk.Label(card_frame, text=title, font=("Helvetica", 11))
            title_label.pack(anchor=tk.W)

            # Set color based on style
            colors = {
                PRIMARY: "blue",
                SUCCESS: "green",
                INFO: "#17a2b8",
                WARNING: "orange",
                SECONDARY: "gray",
                DANGER: "red"
            }
            color = colors.get(style, "black")

            value_label = tk.Label(card_frame, text=value, font=("Helvetica", 28, "bold"), fg=color)
            value_label.pack(anchor=tk.W, pady=(5, 0))

            unit_label = tk.Label(card_frame, text=unit, font=("Helvetica", 10), fg="gray")
            unit_label.pack(anchor=tk.W)

        # Quick actions frame
        if HAS_TTKBOOTSTRAP:
            actions_frame = tb.LabelFrame(
                self.content_frame,
                text="Quick Actions",
                padding=20,
                bootstyle=INFO
            )
        else:
            actions_frame = tk.LabelFrame(
                self.content_frame,
                text="Quick Actions",
                padx=20,
                pady=20,
                relief=tk.RAISED,
                borderwidth=2
            )
        actions_frame.pack(fill=tk.X, pady=(0, 30))

        action_buttons = []

        if self.user_role in ['admin', 'librarian']:
            action_buttons.extend([
                ("📚 Add New Book", self.add_new_book),
                ("👥 Register Member", self.register_member),
                ("📖 Issue Loan", self.issue_loan),
                ("↩️ Return Book", self.return_book)
            ])

        if self.user_role == 'member':
            action_buttons.extend([
                ("🔍 Search Books", self.show_books),
                ("📚 My Loans", self.show_my_loans),
                ("💰 My Fines", self.show_my_fines)
            ])

        action_buttons.append(("📊 View Reports", self.show_reports))

        for i, (text, command) in enumerate(action_buttons):
            if HAS_TTKBOOTSTRAP:
                btn = tb.Button(
                    actions_frame,
                    text=text,
                    command=command,
                    width=20,
                    bootstyle="outline-primary"
                )
            else:
                btn = tk.Button(
                    actions_frame,
                    text=text,
                    command=command,
                    width=20
                )
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=10, sticky="w")

        # Recent activity table
        if HAS_TTKBOOTSTRAP:
            activity_frame = tb.LabelFrame(
                self.content_frame,
                text="Recent Activity",
                padding=20,
                bootstyle=SECONDARY
            )
        else:
            activity_frame = tk.LabelFrame(
                self.content_frame,
                text="Recent Activity",
                padx=20,
                pady=20,
                relief=tk.RAISED,
                borderwidth=2
            )
        activity_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview for activity
        columns = ("Time", "User", "Action", "Details")
        tree = ttk.Treeview(activity_frame, columns=columns, show="headings", height=8)

        # Configure columns
        tree.heading("Time", text="Time")
        tree.heading("User", text="User")
        tree.heading("Action", text="Action")
        tree.heading("Details", text="Details")

        tree.column("Time", width=150)
        tree.column("User", width=100)
        tree.column("Action", width=150)
        tree.column("Details", width=400)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add sample activity data
        sample_activity = [
            ("2025-12-05 10:30", "admin", "Added Book", "The Great Gatsby - F. Scott Fitzgerald"),
            ("2025-12-05 09:15", "librarian", "Issued Loan", "Member #1001 borrowed '1984'"),
            ("2025-12-05 08:45", "system", "Daily Maintenance", "Updated 42 overdue loans"),
            ("2024-12-04 16:20", "member", "Returned Book", "To Kill a Mockingbird"),
            ("2025-12-04 14:10", "admin", "Updated Member", "Updated membership for John Doe")
            ("2027-12-05 10:30", "admin", "Added Book", "The Greatest Gatsby - F. Scott Fitzgerald"),
            ("2029-12-05 09:15", "librarian", "Issued Loan", "Member #1001 borrowed '1984'"),
            ("2020-12-05 08:45", "system", "Daily Maintenance", "Updated 42 overdue loans"),
            ("2011-12-04 16:20", "member", "Returned Book", "To Kill a Mockingbird"),
            ("2026-12-04 14:10", "admin", "Updated Member", "Updated membership for John Doe"),
        ]

        for activity in sample_activity:
            tree.insert("", tk.END, values=activity)

    def show_books(self):
        """Show books management interface"""
        self.clear_content_frame()

        # Title and search bar
        title_frame = tk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                title_frame,
                text="Books Management",
                font=("Helvetica", 24, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                title_frame,
                text="Books Management",
                font=("Helvetica", 24, "bold"),
                fg="blue"
            )
        title_label.pack(side=tk.LEFT)

        # Search frame
        search_frame = tk.Frame(title_frame)
        search_frame.pack(side=tk.RIGHT)

        self.book_search_var = tk.StringVar()
        if HAS_TTKBOOTSTRAP:
            search_entry = tb.Entry(
                search_frame,
                textvariable=self.book_search_var,
                width=30,
                placeholder="Search books..."
            )
        else:
            search_entry = tk.Entry(
                search_frame,
                textvariable=self.book_search_var,
                width=30
            )
            search_entry.insert(0, "Search books...")
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_books())

        if HAS_TTKBOOTSTRAP:
            search_btn = tb.Button(
                search_frame,
                text="Search",
                command=self.search_books,
                bootstyle=INFO
            )
        else:
            search_btn = tk.Button(
                search_frame,
                text="Search",
                command=self.search_books,
                bg="#17a2b8",
                fg="white"
            )
        search_btn.pack(side=tk.LEFT)

        # Add book button for admin/librarian
        if self.user_role in ['admin', 'librarian']:
            if HAS_TTKBOOTSTRAP:
                add_btn = tb.Button(
                    search_frame,
                    text="+ Add New Book",
                    command=self.add_new_book,
                    bootstyle=SUCCESS
                )
            else:
                add_btn = tk.Button(
                    search_frame,
                    text="+ Add New Book",
                    command=self.add_new_book,
                    bg="green",
                    fg="white"
                )
            add_btn.pack(side=tk.LEFT, padx=(20, 0))

        # Filter frame
        filter_frame = tk.Frame(self.content_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=(0, 10))

        self.filter_status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_status_var,
            values=["all", "available", "borrowed", "overdue"],
            state="readonly",
            width=15
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 20))

        self.filter_genre_var = tk.StringVar(value="all")
        genre_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_genre_var,
            values=["all", "fiction", "non-fiction", "science", "technology"],
            state="readonly",
            width=15
        )
        genre_combo.pack(side=tk.LEFT, padx=(0, 20))

        if HAS_TTKBOOTSTRAP:
            filter_btn = tb.Button(
                filter_frame,
                text="Apply Filter",
                command=self.filter_books,
                bootstyle="outline-primary"
            )
        else:
            filter_btn = tk.Button(
                filter_frame,
                text="Apply Filter",
                command=self.filter_books
            )
        filter_btn.pack(side=tk.LEFT)

        # Books table
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ("ID", "Title", "Author", "ISBN", "Available", "Total", "Status", "Genre")
        self.books_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)

        self.books_tree.column("Title", width=200)
        self.books_tree.column("Author", width=150)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.books_tree.xview)
        self.books_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.books_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Action buttons frame
        action_frame = tk.Frame(self.content_frame)
        action_frame.pack(fill=tk.X, pady=(20, 0))

        if self.user_role in ['admin', 'librarian']:
            if HAS_TTKBOOTSTRAP:
                edit_btn = tb.Button(
                    action_frame,
                    text="Edit Selected",
                    command=self.edit_book,
                    bootstyle="outline-warning"
                )
                delete_btn = tb.Button(
                    action_frame,
                    text="Delete Selected",
                    command=self.delete_book,
                    bootstyle="outline-danger"
                )
            else:
                edit_btn = tk.Button(
                    action_frame,
                    text="Edit Selected",
                    command=self.edit_book,
                    bg="orange",
                    fg="white"
                )
                delete_btn = tk.Button(
                    action_frame,
                    text="Delete Selected",
                    command=self.delete_book,
                    bg="red",
                    fg="white"
                )
            edit_btn.pack(side=tk.LEFT, padx=(0, 10))
            delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        if self.user_role != 'member':
            if HAS_TTKBOOTSTRAP:
                borrow_btn = tb.Button(
                    action_frame,
                    text="Borrow Selected",
                    command=self.borrow_book,
                    bootstyle="outline-success"
                )
            else:
                borrow_btn = tk.Button(
                    action_frame,
                    text="Borrow Selected",
                    command=self.borrow_book,
                    bg="green",
                    fg="white"
                )
            borrow_btn.pack(side=tk.LEFT)

        # Load books
        self.load_books()

    def load_books(self):
        """Load books from database"""
        # Clear existing items
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        # Load sample data
        for book in DatabaseConnection.SAMPLE_BOOKS:
            tags = ('success',) if book[4] > 0 else ('warning',)
            self.books_tree.insert("", tk.END, values=book, tags=tags)

        # Configure tag colors
        self.books_tree.tag_configure('success', foreground='green')
        self.books_tree.tag_configure('warning', foreground='orange')

    def search_books(self):
        """Search books based on search term"""
        search_term = self.book_search_var.get().lower()
        if not search_term or search_term == "search books...":
            self.load_books()
            return

        # Filter displayed books
        for item in self.books_tree.get_children():
            values = self.books_tree.item(item)['values']
            # Search in title, author, and ISBN
            if (search_term in str(values[1]).lower() or
                    search_term in str(values[2]).lower() or
                    search_term in str(values[3]).lower()):
                self.books_tree.item(item, tags=())
            else:
                self.books_tree.item(item, tags=('hidden',))

        self.books_tree.tag_configure('hidden', foreground='gray')

    def filter_books(self):
        """Filter books based on criteria"""
        status = self.filter_status_var.get()
        genre = self.filter_genre_var.get()

        for item in self.books_tree.get_children():
            values = self.books_tree.item(item)['values']
            show = True

            # Filter by status
            if status != "all":
                if status == "available" and values[6] != "Available":
                    show = False
                elif status == "borrowed" and values[6] != "Borrowed":
                    show = False

            # Filter by genre (simplified)
            if show and genre != "all" and genre.lower() not in str(values[7]).lower():
                show = False

            self.books_tree.item(item, tags=() if show else ('hidden',))

        self.books_tree.tag_configure('hidden', foreground='gray')

    def show_members(self):
        """Show members management interface"""
        if self.user_role not in ['admin', 'librarian']:
            messagebox.showerror("Access Denied", "Only administrators and librarians can access this section.")
            return

        self.clear_content_frame()

        # Title and add button
        title_frame = tk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                title_frame,
                text="Members Management",
                font=("Helvetica", 24, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                title_frame,
                text="Members Management",
                font=("Helvetica", 24, "bold"),
                fg="blue"
            )
        title_label.pack(side=tk.LEFT)

        if HAS_TTKBOOTSTRAP:
            add_btn = tb.Button(
                title_frame,
                text="+ Register New Member",
                command=self.register_member,
                bootstyle=SUCCESS
            )
        else:
            add_btn = tk.Button(
                title_frame,
                text="+ Register New Member",
                command=self.register_member,
                bg="green",
                fg="white"
            )
        add_btn.pack(side=tk.RIGHT)

        # Members table
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ("ID", "Name", "Membership #", "Email", "Phone", "Type", "Active Loans", "Status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column("Name", width=150)
        tree.column("Email", width=200)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Load sample members data
        for member in DatabaseConnection.SAMPLE_MEMBERS:
            tags = ('success',) if member[7] == "Active" else ('warning',)
            tree.insert("", tk.END, values=member, tags=tags)

        tree.tag_configure('success', foreground='green')
        tree.tag_configure('warning', foreground='orange')

    def show_loans(self):
        """Show loans management interface"""
        self.clear_content_frame()

        # Title
        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                self.content_frame,
                text="Loans Management",
                font=("Helvetica", 24, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                self.content_frame,
                text="Loans Management",
                font=("Helvetica", 24, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Tabs for different loan types
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Active loans tab
        active_frame = tk.Frame(notebook)
        notebook.add(active_frame, text="Active Loans")
        self.create_loans_table(active_frame, "active")

        # Overdue loans tab
        overdue_frame = tk.Frame(notebook)
        notebook.add(overdue_frame, text="Overdue Loans")
        self.create_loans_table(overdue_frame, "overdue")

        # Returned loans tab
        returned_frame = tk.Frame(notebook)
        notebook.add(returned_frame, text="Returned Loans")
        self.create_loans_table(returned_frame, "returned")

        # Issue new loan button
        if self.user_role in ['admin', 'librarian']:
            issue_frame = tk.Frame(self.content_frame)
            issue_frame.pack(fill=tk.X, pady=(20, 0))

            if HAS_TTKBOOTSTRAP:
                issue_btn = tb.Button(
                    issue_frame,
                    text="Issue New Loan",
                    command=self.issue_loan,
                    bootstyle=SUCCESS,
                    width=20
                )
            else:
                issue_btn = tk.Button(
                    issue_frame,
                    text="Issue New Loan",
                    command=self.issue_loan,
                    bg="green",
                    fg="white",
                    width=20
                )
            issue_btn.pack(side=tk.RIGHT)

    def create_loans_table(self, parent, loan_type):
        """Create loans table for specific type"""
        table_frame = tk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create treeview
        columns = ("Loan ID", "Book Title", "Member", "Loan Date", "Due Date", "Status", "Fine")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column("Book Title", width=200)
        tree.column("Member", width=150)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Load sample data
        sample_data = {
            "active": DatabaseConnection.SAMPLE_ACTIVE_LOANS,
            "overdue": DatabaseConnection.SAMPLE_OVERDUE_LOANS,
            "returned": [
                (301, "Sapiens", "Charlie Wilson", "2025-10-10", "2025-10-24", "Returned", "$0.00"),
                (302, "Atomic Habits", "Diana Miller", "2025-10-15", "2025-10-29", "Returned", "$0.00"),
                (301, "Mathematics", "Charlie Wilson", "2025-10-10", "2025-10-24", "Returned", "$0.00"),
                (303, "Atomical", "Diana Miller", "2025-10-15", "2025-10-29", "Returned", "$0.00"),
                (303, "Sapien", "Charlie Wilson", "2025-10-10", "2025-10-24", "Returned", "$0.00"),
                (304, "Habits", "Diana Miller", "2025-10-15", "2025-10-29", "Returned", "$0.00"),
                (306, "Sapians", "Charlie Wilson", "2025-10-10", "2025-10-24", "Returned", "$0.00"),
                (300, "Database", "Diana Miller", "2025-10-15", "2025-10-29", "Returned", "$0.00"),
            ]
        }

        for loan in sample_data.get(loan_type, []):
            tags = ()
            if loan_type == "overdue":
                tags = ('danger',)
            elif loan_type == "active":
                tags = ('success',)
            tree.insert("", tk.END, values=loan, tags=tags)

        tree.tag_configure('danger', foreground='red')
        tree.tag_configure('success', foreground='green')

    def show_fines(self):
        """Show fines management interface"""
        self.clear_content_frame()

        # Title
        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                self.content_frame,
                text="Fines Management",
                font=("Helvetica", 24, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                self.content_frame,
                text="Fines Management",
                font=("Helvetica", 24, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Statistics frame
        stats_frame = tk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        stats_data = [
            ("Total Pending", "$245.50", DANGER),
            ("Total Paid", "$1,250.75", SUCCESS),
            ("Total Waived", "$150.00", WARNING),
            ("Average Fine", "$8.50", INFO)
        ]

        for i, (title, value, style) in enumerate(stats_data):
            if HAS_TTKBOOTSTRAP:
                card = tb.Frame(stats_frame, bootstyle="light", padding=15)
            else:
                card = tk.Frame(stats_frame, relief=tk.RAISED, borderwidth=1, padx=15, pady=15)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=("Helvetica", 11)).pack(anchor=tk.W)

            colors = {
                DANGER: "red",
                SUCCESS: "green",
                WARNING: "orange",
                INFO: "#17a2b8"
            }
            color = colors.get(style, "black")

            tk.Label(card, text=value, font=("Helvetica", 20, "bold"), fg=color).pack(anchor=tk.W, pady=(5, 0))

        # Fines table
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ("Fine ID", "Member", "Book", "Amount", "Issued Date", "Due Date", "Status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column("Member", width=150)
        tree.column("Book", width=150)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Load sample fines data
        for fine in DatabaseConnection.SAMPLE_FINES:
            tags = ()
            if fine[6] == "Pending":
                tags = ('danger',)
            elif fine[6] == "Paid":
                tags = ('success',)
            elif fine[6] == "Waived":
                tags = ('warning',)
            tree.insert("", tk.END, values=fine, tags=tags)

        tree.tag_configure('danger', foreground='red')
        tree.tag_configure('success', foreground='green')
        tree.tag_configure('warning', foreground='orange')

        # Action buttons
        action_frame = tk.Frame(self.content_frame)
        action_frame.pack(fill=tk.X, pady=(20, 0))

        if self.user_role in ['admin', 'librarian']:
            if HAS_TTKBOOTSTRAP:
                paid_btn = tb.Button(
                    action_frame,
                    text="Mark as Paid",
                    command=lambda: self.update_fine_status("Paid"),
                    bootstyle="outline-success"
                )
                waive_btn = tb.Button(
                    action_frame,
                    text="Waive Fine",
                    command=lambda: self.update_fine_status("Waived"),
                    bootstyle="outline-warning"
                )
            else:
                paid_btn = tk.Button(
                    action_frame,
                    text="Mark as Paid",
                    command=lambda: self.update_fine_status("Paid"),
                    bg="green",
                    fg="white"
                )
                waive_btn = tk.Button(
                    action_frame,
                    text="Waive Fine",
                    command=lambda: self.update_fine_status("Waived"),
                    bg="orange",
                    fg="white"
                )
            paid_btn.pack(side=tk.LEFT, padx=(0, 10))
            waive_btn.pack(side=tk.LEFT)

    def show_reports(self):
        """Show reports interface"""
        self.clear_content_frame()

        # Title
        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                self.content_frame,
                text="Reports & Analytics",
                font=("Helvetica", 24, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                self.content_frame,
                text="Reports & Analytics",
                font=("Helvetica", 24, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Report selection frame
        if HAS_TTKBOOTSTRAP:
            report_frame = tb.LabelFrame(
                self.content_frame,
                text="Generate Report",
                padding=20,
                bootstyle=INFO
            )
        else:
            report_frame = tk.LabelFrame(
                self.content_frame,
                text="Generate Report",
                padx=20,
                pady=20,
                relief=tk.RAISED,
                borderwidth=2
            )
        report_frame.pack(fill=tk.X, pady=(0, 20))

        # Report type selection
        tk.Label(report_frame, text="Report Type:", font=("Helvetica", 11)).grid(row=0, column=0, sticky=tk.W,
                                                                                 padx=(0, 10))

        self.report_type_var = tk.StringVar(value="overdue")
        report_combo = ttk.Combobox(
            report_frame,
            textvariable=self.report_type_var,
            values=[
                "Overdue Books Report",
                "Monthly Circulation",
                "Member Activity",
                "Popular Genres",
                "Fine Collection",
                "Book Inventory"
            ],
            state="readonly",
            width=25
        )
        report_combo.grid(row=0, column=1, padx=(0, 20))

        # Date range
        tk.Label(report_frame, text="From:", font=("Helvetica", 11)).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        if HAS_TKCALENDAR:
            from_date = DateEntry(
                report_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
        else:
            from_date = tk.Entry(report_frame, width=12)
            from_date.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        from_date.grid(row=0, column=3, padx=(0, 20))

        tk.Label(report_frame, text="To:", font=("Helvetica", 11)).grid(row=0, column=4, sticky=tk.W, padx=(0, 10))

        if HAS_TKCALENDAR:
            to_date = DateEntry(
                report_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
        else:
            to_date = tk.Entry(report_frame, width=12)
            to_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        to_date.grid(row=0, column=5, padx=(0, 20))

        # Generate button
        if HAS_TTKBOOTSTRAP:
            generate_btn = tb.Button(
                report_frame,
                text="Generate Report",
                command=self.generate_report,
                bootstyle=SUCCESS
            )
        else:
            generate_btn = tk.Button(
                report_frame,
                text="Generate Report",
                command=self.generate_report,
                bg="green",
                fg="white"
            )
        generate_btn.grid(row=0, column=6, padx=(20, 0))

        # Report output area
        output_frame = tk.Frame(self.content_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)

        # Text area for report
        self.report_text = scrolledtext.ScrolledText(
            output_frame,
            width=80,
            height=20,
            font=("Courier", 10)
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add sample report
        sample_report = """OVERDUE BOOKS REPORT
Generated: 2025-12-05
Period: 2025-11-01 to 2025-12-05
==================================================

Total Overdue Books: 42
Total Fines Due: $245.50

DETAILED LIST:
--------------------------------------------------
1. Member: John Doe (MEM1001)
   Book: To Kill a Mockingbird
   Due Date: 2025-11-29
   Days Overdue: 6
   Fine: $3.00

2. Member: Alice Brown (MEM1004)
   Book: The Silent Patient
   Due Date: 2025-12-04
   Days Overdue: 1
   Fine: $0.50
   
3. Member: Alice Brown (MEM1004)
   Book: The Silent Patient
   Due Date: 2025-12-04
   Days Overdue: 1
   Fine: $0.50

3. Member: Bob Johnson (MEM1003)
   Book: 1984
   Due Date: 2025-11-25
   Days Overdue: 10
   Fine: $5.00

4. Member: Alice Brown (MEM1004)
   Book: The Silent Patient
   Due Date: 2025-12-04
   Days Overdue: 1
   Fine: $0.50
... (39 more records)

5. Member: Alice Brown (MEM1004)
   Book: The Silent Patient
   Due Date: 2025-12-04
   Days Overdue: 1
   Fine: $0.50

SUMMARY:
- Most overdue book: 1984 (10 days)
- Highest fine: $12.00
- Member with most overdue books: Alice Brown (3 books)
"""

        self.report_text.insert(tk.END, sample_report)
        self.report_text.config(state=tk.DISABLED)

        # Export buttons
        export_frame = tk.Frame(self.content_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))

        if HAS_TTKBOOTSTRAP:
            csv_btn = tb.Button(
                export_frame,
                text="Export as CSV",
                command=lambda: self.export_report("csv"),
                bootstyle="outline-primary"
            )
            pdf_btn = tb.Button(
                export_frame,
                text="Export as PDF",
                command=lambda: self.export_report("pdf"),
                bootstyle="outline-danger"
            )
            print_btn = tb.Button(
                export_frame,
                text="Print Report",
                command=self.print_report,
                bootstyle="outline-info"
            )
        else:
            csv_btn = tk.Button(
                export_frame,
                text="Export as CSV",
                command=lambda: self.export_report("csv")
            )
            pdf_btn = tk.Button(
                export_frame,
                text="Export as PDF",
                command=lambda: self.export_report("pdf")
            )
            print_btn = tk.Button(
                export_frame,
                text="Print Report",
                command=self.print_report
            )
        csv_btn.pack(side=tk.LEFT, padx=(0, 10))
        pdf_btn.pack(side=tk.LEFT, padx=(0, 10))
        print_btn.pack(side=tk.LEFT)

    def add_new_book(self):
        """Open dialog to add a new book"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()

        # Form frame
        if HAS_TTKBOOTSTRAP:
            form_frame = tb.Frame(dialog, padding=30)
        else:
            form_frame = tk.Frame(dialog, padx=30, pady=30)
        form_frame.pack(fill=tk.BOTH, expand=True)

        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                form_frame,
                text="Add New Book",
                font=("Helvetica", 18, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                form_frame,
                text="Add New Book",
                font=("Helvetica", 18, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Book details form
        fields = [
            ("ISBN *", "isbn"),
            ("Title *", "title"),
            ("Author *", "author"),
            ("Publisher", "publisher"),
            ("Publication Year", "year"),
            ("Genre", "genre"),
            ("Total Copies *", "copies"),
            ("Location Code", "location"),
            ("Description", "description")
        ]

        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))

            if key == "description":
                entry = scrolledtext.ScrolledText(form_frame, height=4, width=50)
                entry.pack(fill=tk.X, pady=(0, 10))
            elif key == "genre":
                entry = ttk.Combobox(
                    form_frame,
                    values=["Fiction", "Non-Fiction", "Science", "Technology", "Biography", "History", "Mystery"]
                )
                entry.pack(fill=tk.X, pady=(0, 10))
            else:
                if HAS_TTKBOOTSTRAP:
                    entry = tb.Entry(form_frame, width=50)
                else:
                    entry = tk.Entry(form_frame, width=50)
                entry.pack(fill=tk.X, pady=(0, 10))

            entries[key] = entry

        # Button frame
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        def save_book():
            # Validate required fields
            if not entries["isbn"].get().strip():
                messagebox.showerror("Error", "ISBN is required")
                return
            if not entries["title"].get().strip():
                messagebox.showerror("Error", "Title is required")
                return
            if not entries["author"].get().strip():
                messagebox.showerror("Error", "Author is required")
                return
            if not entries["copies"].get().strip():
                messagebox.showerror("Error", "Total copies is required")
                return

            # Save to database (mock)
            messagebox.showinfo("Success", "Book added successfully!")
            dialog.destroy()
            self.load_books()  # Refresh book list

        if HAS_TTKBOOTSTRAP:
            save_btn = tb.Button(
                button_frame,
                text="Save Book",
                command=save_book,
                bootstyle=SUCCESS,
                width=15
            )
            cancel_btn = tb.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                bootstyle="outline-secondary",
                width=15
            )
        else:
            save_btn = tk.Button(
                button_frame,
                text="Save Book",
                command=save_book,
                bg="green",
                fg="white",
                width=15
            )
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=15
            )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        cancel_btn.pack(side=tk.LEFT)

    def register_member(self):
        """Open dialog to register a new member"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New Member")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()

        if HAS_TTKBOOTSTRAP:
            form_frame = tb.Frame(dialog, padding=30)
        else:
            form_frame = tk.Frame(dialog, padx=30, pady=30)
        form_frame.pack(fill=tk.BOTH, expand=True)

        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                form_frame,
                text="Register New Member",
                font=("Helvetica", 18, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                form_frame,
                text="Register New Member",
                font=("Helvetica", 18, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Member registration form
        fields = [
            ("First Name *", "first_name"),
            ("Last Name *", "last_name"),
            ("Email *", "email"),
            ("Phone Number", "phone"),
            ("Address", "address"),
            ("Membership Type", "membership_type"),
            ("Username *", "username"),
            ("Password *", "password")
        ]

        entries = {}

        for label, key in fields:
            tk.Label(form_frame, text=label, font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))

            if key == "address":
                entry = scrolledtext.ScrolledText(form_frame, height=3, width=40)
                entry.pack(fill=tk.X, pady=(0, 10))
            elif key == "membership_type":
                entry = ttk.Combobox(
                    form_frame,
                    values=["Standard", "Premium", "Student"]
                )
                entry.pack(fill=tk.X, pady=(0, 10))
                entry.set("Standard")
            elif key == "password":
                if HAS_TTKBOOTSTRAP:
                    entry = tb.Entry(form_frame, width=40, show="*")
                else:
                    entry = tk.Entry(form_frame, width=40, show="*")
                entry.pack(fill=tk.X, pady=(0, 10))
            else:
                if HAS_TTKBOOTSTRAP:
                    entry = tb.Entry(form_frame, width=40)
                else:
                    entry = tk.Entry(form_frame, width=40)
                entry.pack(fill=tk.X, pady=(0, 10))

            entries[key] = entry

        def save_member():
            # Validate required fields
            required = ["first_name", "last_name", "email", "username", "password"]
            for field in required:
                if not entries[field].get().strip():
                    messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required")
                    return

            # Save member (mock)
            messagebox.showinfo("Success",
                                "Member registered successfully!\nMembership Number: MEM" + str(1000 + len(entries)))
            dialog.destroy()

        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        if HAS_TTKBOOTSTRAP:
            register_btn = tb.Button(
                button_frame,
                text="Register",
                command=save_member,
                bootstyle=SUCCESS,
                width=15
            )
            cancel_btn = tb.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                bootstyle="outline-secondary",
                width=15
            )
        else:
            register_btn = tk.Button(
                button_frame,
                text="Register",
                command=save_member,
                bg="green",
                fg="white",
                width=15
            )
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=15
            )
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        cancel_btn.pack(side=tk.LEFT)

    def issue_loan(self):
        """Open dialog to issue a new loan"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Issue New Loan")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        if HAS_TTKBOOTSTRAP:
            form_frame = tb.Frame(dialog, padding=30)
        else:
            form_frame = tk.Frame(dialog, padx=30, pady=30)
        form_frame.pack(fill=tk.BOTH, expand=True)

        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                form_frame,
                text="Issue New Loan",
                font=("Helvetica", 18, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                form_frame,
                text="Issue New Loan",
                font=("Helvetica", 18, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Member selection
        tk.Label(form_frame, text="Select Member:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))
        member_combo = ttk.Combobox(
            form_frame,
            values=["John Doe (MEM1001)", "Jane Smith (MEM1002)", "Bob Johnson (MEM1003)"],
            state="readonly"
        )
        member_combo.pack(fill=tk.X, pady=(0, 10))
        member_combo.set("John Doe (MEM1001)")

        # Book selection
        tk.Label(form_frame, text="Select Book:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))
        book_combo = ttk.Combobox(
            form_frame,
            values=["The Great Gatsby (Available)", "Sapiens (Available)", "Atomic Habits (Available)"],
            state="readonly"
        )
        book_combo.pack(fill=tk.X, pady=(0, 10))
        book_combo.set("The Great Gatsby (Available)")

        # Loan duration
        tk.Label(form_frame, text="Loan Duration:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))
        duration_frame = tk.Frame(form_frame)
        duration_frame.pack(fill=tk.X, pady=(0, 10))

        duration_var = tk.StringVar(value="14")
        tk.Radiobutton(duration_frame, text="7 days", variable=duration_var, value="7").pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(duration_frame, text="14 days", variable=duration_var, value="14").pack(side=tk.LEFT,
                                                                                               padx=(0, 20))
        tk.Radiobutton(duration_frame, text="21 days", variable=duration_var, value="21").pack(side=tk.LEFT)

        def issue_loan_action():
            due_date = datetime.now() + timedelta(days=int(duration_var.get()))
            messagebox.showinfo(
                "Loan Issued",
                f"Loan issued successfully!\nDue Date: {due_date.strftime('%Y-%m-%d')}"
            )
            dialog.destroy()

        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        if HAS_TTKBOOTSTRAP:
            issue_btn = tb.Button(
                button_frame,
                text="Issue Loan",
                command=issue_loan_action,
                bootstyle=SUCCESS,
                width=15
            )
            cancel_btn = tb.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                bootstyle="outline-secondary",
                width=15
            )
        else:
            issue_btn = tk.Button(
                button_frame,
                text="Issue Loan",
                command=issue_loan_action,
                bg="green",
                fg="white",
                width=15
            )
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=15
            )
        issue_btn.pack(side=tk.LEFT, padx=(0, 10))
        cancel_btn.pack(side=tk.LEFT)

    def return_book(self):
        """Open dialog to return a book"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Return Book")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        if HAS_TTKBOOTSTRAP:
            form_frame = tb.Frame(dialog, padding=30)
        else:
            form_frame = tk.Frame(dialog, padx=30, pady=30)
        form_frame.pack(fill=tk.BOTH, expand=True)

        if HAS_TTKBOOTSTRAP:
            title_label = tb.Label(
                form_frame,
                text="Return Book",
                font=("Helvetica", 18, "bold"),
                bootstyle=PRIMARY
            )
        else:
            title_label = tk.Label(
                form_frame,
                text="Return Book",
                font=("Helvetica", 18, "bold"),
                fg="blue"
            )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Loan ID input
        tk.Label(form_frame, text="Enter Loan ID:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))
        if HAS_TTKBOOTSTRAP:
            loan_id_entry = tb.Entry(form_frame, width=30)
        else:
            loan_id_entry = tk.Entry(form_frame, width=30)
        loan_id_entry.pack(fill=tk.X, pady=(0, 10))

        # Condition
        tk.Label(form_frame, text="Book Condition:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(10, 5))
        condition_combo = ttk.Combobox(
            form_frame,
            values=["Good", "Fair", "Damaged", "Lost"],
            state="readonly"
        )
        condition_combo.pack(fill=tk.X, pady=(0, 10))
        condition_combo.set("Good")

        def return_book_action():
            loan_id = loan_id_entry.get().strip()
            if not loan_id:
                messagebox.showerror("Error", "Please enter a Loan ID")
                return

            # Check for fines
            if condition_combo.get() == "Damaged":
                fine = 25.00
                messagebox.showwarning(
                    "Damage Fine",
                    f"Book returned in damaged condition.\nFine applied: ${fine:.2f}"
                )
            elif condition_combo.get() == "Lost":
                fine = 50.00
                messagebox.showwarning(
                    "Lost Book",
                    f"Book marked as lost.\nReplacement fine: ${fine:.2f}"
                )
            else:
                messagebox.showinfo("Success", "Book returned successfully!")

            dialog.destroy()

        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        if HAS_TTKBOOTSTRAP:
            return_btn = tb.Button(
                button_frame,
                text="Return Book",
                command=return_book_action,
                bootstyle=SUCCESS,
                width=15
            )
            cancel_btn = tb.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                bootstyle="outline-secondary",
                width=15
            )
        else:
            return_btn = tk.Button(
                button_frame,
                text="Return Book",
                command=return_book_action,
                bg="green",
                fg="white",
                width=15
            )
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=15
            )
        return_btn.pack(side=tk.LEFT, padx=(0, 10))
        cancel_btn.pack(side=tk.LEFT)

    def edit_book(self):
        """Edit selected book"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return

        # Get book details
        item = self.books_tree.item(selection[0])
        book_id = item['values'][0]

        messagebox.showinfo("Edit Book", f"Edit book ID: {book_id}\n\nFeature under development.")

    def delete_book(self):
        """Delete selected book"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return

        item = self.books_tree.item(selection[0])
        book_title = item['values'][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n'{book_title}'?\n\nThis action cannot be undone."
        )

        if confirm:
            # Delete from database (mock)
            self.books_tree.delete(selection[0])
            messagebox.showinfo("Success", "Book deleted successfully")

    def borrow_book(self):
        """Borrow selected book"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to borrow")
            return

        item = self.books_tree.item(selection[0])
        book_title = item['values'][1]
        available = item['values'][4]

        if available <= 0:
            messagebox.showerror("Not Available", f"'{book_title}' is not available for borrowing.")
            return

        self.issue_loan()

    def update_fine_status(self, status):
        """Update selected fine status"""
        messagebox.showinfo("Update Fine", f"Mark fine as {status}\n\nFeature under development.")

    def generate_report(self):
        """Generate report based on selection"""
        report_type = self.report_type_var.get()
        messagebox.showinfo("Generate Report", f"Generating {report_type}...\n\nFeature under development.")

    def export_report(self, format):
        """Export report in specified format"""
        messagebox.showinfo("Export Report", f"Exporting report as {format.upper()}...\n\nFeature under development.")

    def print_report(self):
        """Print current report"""
        messagebox.showinfo("Print Report", "Printing report...\n\nFeature under development.")

    def show_my_loans(self):
        """Show current user's loans (for members)"""
        messagebox.showinfo("My Loans", "Showing your current loans...\n\nFeature under development.")

    def show_my_fines(self):
        """Show current user's fines (for members)"""
        messagebox.showinfo("My Fines", "Showing your fines...\n\nFeature under development.")

    def logout(self):
        """Logout current user"""
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.current_user = None
            self.user_role = None
            self.show_login_screen()


# ============================================================================
# MAIN FUNCTION AND APPLICATION LAUNCH
# ============================================================================

def main():
    """Main application entry point"""
    # Create root window with appropriate styling
    if HAS_TTKBOOTSTRAP:
        root = tb.Window(themename="flatly")
    else:
        root = tk.Tk()

    # Set window icon and title
    root.title(" Welcome to SmartLibrary Management System")

    # Create and run application
    app = SmartLibraryApp(root)

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()