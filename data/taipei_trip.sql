CREATE TABLE attraction(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    address VARCHAR(255) NOT NULL,
    transport TEXT,
    mrt VARCHAR(255),
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    images JSON
);

CREATE TABLE user(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    KEY email_pwd_index(email, password)
);

CREATE TABLE booking(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    attraction_id INT NOT NULL,
    date DATE NOT NULL,
    time ENUM("morning", "afternoon") NOT NULL,
    price INT NOT NULL,
    pay BOOLEAN NOT NULL DEFAULT false,
    FOREIGN KEY(user_id)
        REFERENCES user(id)
        ON DELETE CASCADE
);

CREATE TABLE orders(
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(255) NOT NULL,
    booking_id INT NOT NULL,
    FOREIGN KEY(booking_id)
        REFERENCES booking(id)
        ON DELETE CASCADE
);