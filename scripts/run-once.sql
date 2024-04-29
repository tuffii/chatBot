CREATE TABLE IF NOT EXISTS validations (
    validation_id SERIAL PRIMARY KEY,
    validation_datetime TIMESTAMP NOT NULL,
    validation_name VARCHAR(255) NOT NULL,
    validation_description TEXT NOT NULL,
    user_id VARCHAR(255) NOT NULL
);
