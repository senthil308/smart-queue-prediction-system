-- database/schema.sql
CREATE DATABASE IF NOT EXISTS smart_queue_db;
USE smart_queue_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL, -- Unique ID (e.g., SQ-1234)
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE queues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    average_service_time INT DEFAULT 5, -- Time in minutes per token
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_number INT NOT NULL,
    queue_id INT NOT NULL,
    user_id INT NOT NULL,
    status ENUM('waiting', 'serving', 'completed', 'cancelled') DEFAULT 'waiting',
    estimated_time DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (queue_id) REFERENCES queues(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE transfers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_id INT NOT NULL,
    from_user_id INT NOT NULL,
    to_user_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (token_id) REFERENCES tokens(id),
    FOREIGN KEY (from_user_id) REFERENCES users(id),
    FOREIGN KEY (to_user_id) REFERENCES users(id)
);
