-- ============================================================================
-- SmartLibrary PostgreSQL Database Schema
-- Using SERIAL for auto-incrementing primary keys
-- ============================================================================

-- Create database (run this first in psql)
-- CREATE DATABASE smartlibrary;

-- Connect to the database
-- \c smartlibrary;

-- Enable UUID extension (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- 1. Books Table
CREATE TABLE IF NOT EXISTS books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    category VARCHAR(100),
    publisher VARCHAR(255),
    publication_year INTEGER,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    location_code VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT positive_copies CHECK (total_copies >= 0 AND available_copies >= 0)
);

-- Create indexes for books
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);

-- 2. Members Table
CREATE TABLE IF NOT EXISTS members (
    member_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    membership_number VARCHAR(50) UNIQUE GENERATED ALWAYS AS ('MEM' || LPAD(member_id::text, 4, '0')) STORED,
    membership_type VARCHAR(20) DEFAULT 'Standard',
    membership_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_membership_type CHECK (membership_type IN ('Standard', 'Premium', 'Student')),
    CONSTRAINT valid_status CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

-- Create indexes for members
CREATE INDEX IF NOT EXISTS idx_members_name ON members(first_name, last_name);
CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
CREATE INDEX IF NOT EXISTS idx_members_membership_number ON members(membership_number);
CREATE INDEX IF NOT EXISTS idx_members_status ON members(status);

-- 3. Users Table (Library Staff/Admin)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    role VARCHAR(20) DEFAULT 'Staff',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('Admin', 'Librarian', 'Staff'))
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 4. Borrowed Books Table
CREATE TABLE IF NOT EXISTS borrowed_books (
    borrow_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    borrowed_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    actual_return_date DATE,
    condition_before VARCHAR(50),
    condition_after VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Borrowed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status_borrowed CHECK (status IN ('Borrowed', 'Returned', 'Overdue', 'Lost')),
    CONSTRAINT dates_check CHECK (due_date >= borrow_date AND (return_date IS NULL OR return_date >= borrow_date)),
    CONSTRAINT unique_active_borrow UNIQUE(book_id, member_id) WHERE status = 'Borrowed'
);

-- Create indexes for borrowed_books
CREATE INDEX IF NOT EXISTS idx_borrowed_books_book_id ON borrowed_books(book_id);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_member_id ON borrowed_books(member_id);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_due_date ON borrowed_books(due_date);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_status ON borrowed_books(status);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_dates ON borrowed_books(borrow_date, due_date, return_date);

-- 5. Fines Table
CREATE TABLE IF NOT EXISTS fines (
    fine_id SERIAL PRIMARY KEY,
    borrow_id INTEGER REFERENCES borrowed_books(borrow_id) ON DELETE SET NULL,
    member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    reason VARCHAR(255),
    fine_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    payment_date DATE,
    status VARCHAR(20) DEFAULT 'Pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    waived_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    waived_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT positive_amount CHECK (amount >= 0),
    CONSTRAINT valid_fine_status CHECK (status IN ('Pending', 'Paid', 'Waived', 'Cancelled')),
    CONSTRAINT dates_fine_check CHECK (due_date >= fine_date)
);

-- Create indexes for fines
CREATE INDEX IF NOT EXISTS idx_fines_member_id ON fines(member_id);
CREATE INDEX IF NOT EXISTS idx_fines_status ON fines(status);
CREATE INDEX IF NOT EXISTS idx_fines_due_date ON fines(due_date);

-- ============================================================================
-- AUDIT/LOG TABLES
-- ============================================================================

-- 6. Activity Log Table
CREATE TABLE IF NOT EXISTS activity_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    member_id INTEGER REFERENCES members(member_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for activity_log
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_log_action_type ON activity_log(action_type);

-- 7. System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    setting_id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(user_id)
);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- View for active loans
CREATE OR REPLACE VIEW view_active_loans AS
SELECT 
    bb.borrow_id,
    b.title AS book_title,
    b.isbn,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.membership_number,
    bb.borrow_date,
    bb.due_date,
    bb.status,
    CASE 
        WHEN bb.due_date < CURRENT_DATE THEN CURRENT_DATE - bb.due_date
        ELSE 0
    END AS days_overdue,
    CASE 
        WHEN bb.due_date < CURRENT_DATE THEN (CURRENT_DATE - bb.due_date) * 0.50
        ELSE 0.00
    END AS calculated_fine
FROM borrowed_books bb
JOIN books b ON bb.book_id = b.book_id
JOIN members m ON bb.member_id = m.member_id
WHERE bb.status IN ('Borrowed', 'Overdue');

-- View for member statistics
CREATE OR REPLACE VIEW view_member_stats AS
SELECT 
    m.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.membership_number,
    m.membership_type,
    m.membership_date,
    m.status,
    COUNT(DISTINCT bb.borrow_id) AS total_loans,
    COUNT(DISTINCT CASE WHEN bb.status = 'Borrowed' THEN bb.borrow_id END) AS active_loans,
    COUNT(DISTINCT CASE WHEN bb.status = 'Overdue' THEN bb.borrow_id END) AS overdue_loans,
    COALESCE(SUM(f.amount), 0.00) AS total_fines,
    COALESCE(SUM(CASE WHEN f.status = 'Pending' THEN f.amount ELSE 0 END), 0.00) AS pending_fines
FROM members m
LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id
LEFT JOIN fines f ON m.member_id = f.member_id
GROUP BY m.member_id;

-- View for book statistics
CREATE OR REPLACE VIEW view_book_stats AS
SELECT 
    b.book_id,
    b.title,
    b.author,
    b.category,
    b.total_copies,
    b.available_copies,
    COUNT(DISTINCT bb.borrow_id) AS times_borrowed,
    COUNT(DISTINCT CASE WHEN bb.status = 'Borrowed' THEN bb.borrow_id END) AS currently_borrowed,
    COUNT(DISTINCT CASE WHEN bb.status = 'Overdue' THEN bb.borrow_id END) AS currently_overdue
FROM books b
LEFT JOIN borrowed_books bb ON b.book_id = bb.book_id
GROUP BY b.book_id;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update book availability
CREATE OR REPLACE FUNCTION update_book_availability()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'Borrowed' THEN
        UPDATE books 
        SET available_copies = available_copies - 1
        WHERE book_id = NEW.book_id;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status = 'Borrowed' AND NEW.status = 'Returned' THEN
            UPDATE books 
            SET available_copies = available_copies + 1
            WHERE book_id = NEW.book_id;
        ELSIF OLD.status = 'Returned' AND NEW.status = 'Borrowed' THEN
            UPDATE books 
            SET available_copies = available_copies - 1
            WHERE book_id = NEW.book_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for book availability
CREATE OR REPLACE TRIGGER trg_book_availability
AFTER INSERT OR UPDATE ON borrowed_books
FOR EACH ROW
EXECUTE FUNCTION update_book_availability();

-- Function to update overdue status
CREATE OR REPLACE FUNCTION update_overdue_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.due_date < CURRENT_DATE AND NEW.status = 'Borrowed' THEN
        NEW.status := 'Overdue';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for overdue status
CREATE OR REPLACE TRIGGER trg_overdue_status
BEFORE INSERT OR UPDATE ON borrowed_books
FOR EACH ROW
EXECUTE FUNCTION update_overdue_status();

-- Function to auto-generate fines for overdue books
CREATE OR REPLACE FUNCTION generate_overdue_fines()
RETURNS TRIGGER AS $$
DECLARE
    days_overdue INTEGER;
    fine_amount DECIMAL(10,2);
BEGIN
    IF NEW.status = 'Returned' AND OLD.status IN ('Borrowed', 'Overdue') THEN
        days_overdue := GREATEST(0, NEW.actual_return_date - OLD.due_date);
        IF days_overdue > 0 THEN
            fine_amount := days_overdue * 0.50; -- $0.50 per day
            INSERT INTO fines (borrow_id, member_id, amount, reason, due_date)
            VALUES (NEW.borrow_id, NEW.member_id, fine_amount, 
                   'Overdue fine: ' || days_overdue || ' days', 
                   CURRENT_DATE + INTERVAL '7 days');
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-generating fines
CREATE OR REPLACE TRIGGER trg_generate_fines
AFTER UPDATE ON borrowed_books
FOR EACH ROW
WHEN (OLD.status IN ('Borrowed', 'Overdue') AND NEW.status = 'Returned')
EXECUTE FUNCTION generate_overdue_fines();

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at timestamps
CREATE TRIGGER trg_books_timestamp
BEFORE UPDATE ON books
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_members_timestamp
BEFORE UPDATE ON members
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_borrowed_books_timestamp
BEFORE UPDATE ON borrowed_books
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_fines_timestamp
BEFORE UPDATE ON fines
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Procedure to borrow a book
CREATE OR REPLACE PROCEDURE borrow_book(
    p_book_id INTEGER,
    p_member_id INTEGER,
    p_borrowed_by INTEGER,
    p_due_days INTEGER DEFAULT 14
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_available_copies INTEGER;
BEGIN
    -- Check book availability
    SELECT available_copies INTO v_available_copies
    FROM books WHERE book_id = p_book_id;
    
    IF v_available_copies <= 0 THEN
        RAISE EXCEPTION 'Book is not available for borrowing';
    END IF;
    
    -- Check if member already has this book
    IF EXISTS (
        SELECT 1 FROM borrowed_books 
        WHERE book_id = p_book_id 
        AND member_id = p_member_id 
        AND status = 'Borrowed'
    ) THEN
        RAISE EXCEPTION 'Member already has this book borrowed';
    END IF;
    
    -- Insert borrow record
    INSERT INTO borrowed_books (
        book_id, member_id, borrowed_by, 
        borrow_date, due_date, status
    ) VALUES (
        p_book_id, p_member_id, p_borrowed_by,
        CURRENT_DATE, CURRENT_DATE + p_due_days, 'Borrowed'
    );
    
    -- Log activity
    INSERT INTO activity_log (user_id, member_id, action_type, table_name, record_id, description)
    VALUES (p_borrowed_by, p_member_id, 'BORROW_BOOK', 'borrowed_books', 
           currval('borrowed_books_borrow_id_seq'), 
           'Book borrowed with due date ' || (CURRENT_DATE + p_due_days)::text);
END;
$$;

-- Procedure to return a book
CREATE OR REPLACE PROCEDURE return_book(
    p_borrow_id INTEGER,
    p_returned_by INTEGER,
    p_condition_after VARCHAR DEFAULT 'Good',
    p_notes TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_book_id INTEGER;
    v_member_id INTEGER;
BEGIN
    -- Get book and member info
    SELECT book_id, member_id INTO v_book_id, v_member_id
    FROM borrowed_books WHERE borrow_id = p_borrow_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Borrow record not found';
    END IF;
    
    -- Update borrow record
    UPDATE borrowed_books
    SET status = 'Returned',
        return_date = CURRENT_DATE,
        actual_return_date = CURRENT_DATE,
        condition_after = p_condition_after,
        notes = COALESCE(p_notes, notes)
    WHERE borrow_id = p_borrow_id;
    
    -- Log activity
    INSERT INTO activity_log (user_id, member_id, action_type, table_name, record_id, description)
    VALUES (p_returned_by, v_member_id, 'RETURN_BOOK', 'borrowed_books', 
           p_borrow_id, 'Book returned with condition: ' || p_condition_after);
END;
$$;

-- Procedure to calculate member fines
CREATE OR REPLACE PROCEDURE calculate_member_fines(
    p_member_id INTEGER,
    OUT total_pending DECIMAL,
    OUT total_paid DECIMAL,
    OUT total_waived DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT 
        COALESCE(SUM(CASE WHEN status = 'Pending' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN status = 'Waived' THEN amount ELSE 0 END), 0)
    INTO total_pending, total_paid, total_waived
    FROM fines
    WHERE member_id = p_member_id;
END;
$$;

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password_hash, full_name, email, role) 
VALUES ('admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'System Administrator', 'admin@smartlibrary.com', 'Admin')
ON CONFLICT (username) DO NOTHING;

-- Insert sample books
INSERT INTO books (title, author, isbn, category, publisher, publication_year, total_copies, available_copies) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'Fiction', 'Scribner', 1925, 5, 5),
('1984', 'George Orwell', '9780451524935', 'Fiction', 'Signet Classics', 1949, 3, 3),
('To Kill a Mockingbird', 'Harper Lee', '9780446310789', 'Fiction', 'Grand Central Publishing', 1960, 4, 4),
('The Silent Patient', 'Alex Michaelides', '9781250301697', 'Mystery', 'Celadon Books', 2019, 2, 2),
('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', '9780062316097', 'History', 'Harper', 2015, 5, 5),
('Atomic Habits', 'James Clear', '9780735211292', 'Self-Help', 'Avery', 2018, 3, 3),
('The Da Vinci Code', 'Dan Brown', '9780307474278', 'Mystery', 'Anchor', 2003, 2, 2)
ON CONFLICT (isbn) DO NOTHING;

-- Insert sample members
INSERT INTO members (first_name, last_name, email, phone, address, membership_type, status) VALUES
('John', 'Doe', 'john.doe@email.com', '555-0101', '123 Main St, City', 'Premium', 'Active'),
('Jane', 'Smith', 'jane.smith@email.com', '555-0102', '456 Oak Ave, Town', 'Standard', 'Active'),
('Bob', 'Johnson', 'bob.johnson@email.com', '555-0103', '789 Pine Rd, Village', 'Student', 'Active'),
('Alice', 'Brown', 'alice.brown@email.com', '555-0104', '321 Elm St, County', 'Premium', 'Active')
ON CONFLICT (email) DO NOTHING;

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('library_name', 'SmartLibrary', 'string', 'Name of the library'),
('fine_per_day', '0.50', 'decimal', 'Fine amount per overdue day'),
('max_borrow_days', '14', 'integer', 'Maximum days for borrowing'),
('max_books_per_member', '5', 'integer', 'Maximum books a member can borrow'),
('reservation_period_days', '3', 'integer', 'Days to hold reserved books')
ON CONFLICT (setting_key) DO NOTHING;

-- ============================================================================
-- QUERIES FOR TESTING
-- ============================================================================

-- Test query: Get all active members with their loan count
/*
SELECT 
    m.member_id,
    m.first_name || ' ' || m.last_name AS full_name,
    m.membership_number,
    m.email,
    m.membership_type,
    COUNT(bb.borrow_id) AS active_loans
FROM members m
LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id 
    AND bb.status IN ('Borrowed', 'Overdue')
WHERE m.status = 'Active'
GROUP BY m.member_id
ORDER BY m.last_name, m.first_name;
*/

-- Test query: Get all overdue books
/*
SELECT 
    b.title,
    b.author,
    m.first_name || ' ' || m.last_name AS borrower,
    m.membership_number,
    bb.borrow_date,
    bb.due_date,
    CURRENT_DATE - bb.due_date AS days_overdue,
    (CURRENT_DATE - bb.due_date) * 0.50 AS fine_amount
FROM borrowed_books bb
JOIN books b ON bb.book_id = b.book_id
JOIN members m ON bb.member_id = m.member_id
WHERE bb.status = 'Overdue'
ORDER BY days_overdue DESC;
*/

-- ============================================================================
-- DATABASE BACKUP COMMANDS
-- ============================================================================
/*
-- Backup database:
-- pg_dump -U postgres -d smartlibrary -f smartlibrary_backup.sql

-- Restore database:
-- psql -U postgres -d smartlibrary -f smartlibrary_backup.sql
*/

-- ============================================================================
-- GRANT PERMISSIONS (if needed)
-- ============================================================================
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO library_admin;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO library_admin;