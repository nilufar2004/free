-- Database Schema for Sardoba Restaurant Telegram Bot

CREATE DATABASE IF NOT EXISTS sardoba_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE sardoba_bot;

-- Users table to store admin and cashier information
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    phone_number VARCHAR(20),
    role ENUM('admin', 'cashier') NOT NULL,
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Locations table for restaurant branches
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Insert default locations
INSERT INTO locations (name, address) VALUES
('Sardoba (Geofizika)', 'Geofizika district'),
('Sardoba (G\'ijduvon)', 'G\'ijduvon district'),
('Sardoba (Severniy)', 'Severniy district'),
('Sardoba (MK-5)', 'MK-5 district');

-- Shifts table to track cashier shifts
CREATE TABLE shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    opening_amount DECIMAL(10, 2),
    closing_amount DECIMAL(10, 2) DEFAULT NULL,
    is_open BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- Reports table to store daily reports
CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shift_id INT NOT NULL,
    report_type ENUM('shift_opening', 'shift_closing', 'daily_report') NOT NULL,
    sales_amount DECIMAL(10, 2) DEFAULT 0,
    debt_received DECIMAL(10, 2) DEFAULT 0,
    expenses DECIMAL(10, 2) DEFAULT 0,
    uzcard_amount DECIMAL(10, 2) DEFAULT 0,
    humo_amount DECIMAL(10, 2) DEFAULT 0,
    uzcard_refund DECIMAL(10, 2) DEFAULT 0,
    humo_refund DECIMAL(10, 2) DEFAULT 0,
    other_payments DECIMAL(10, 2) DEFAULT 0,
    debt_payments DECIMAL(10, 2) DEFAULT 0,
    debt_refunds DECIMAL(10, 2) DEFAULT 0,
    report_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shift_id) REFERENCES shifts(id)
);

-- Images table to store uploaded images for reports
CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT,
    shift_id INT,
    image_url VARCHAR(500),
    image_type ENUM('workplace_status', 'terminal_power', 'zero_report', 'opening_notification', 'receipt_roll', 'uzcard_payment', 'humo_payment') NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id),
    FOREIGN KEY (shift_id) REFERENCES shifts(id)
);

-- Admin approval requests table
CREATE TABLE approval_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    phone_number VARCHAR(20),
    role ENUM('cashier') NOT NULL, -- Only cashiers need approval
    password_hash VARCHAR(255),
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL
);
