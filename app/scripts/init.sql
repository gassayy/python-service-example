-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,  -- OSM ID
    username VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50),  -- UserRole enum
    profile_img TEXT,
    name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    email_address VARCHAR(255),
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_expert BOOLEAN DEFAULT FALSE,
    api_key VARCHAR(255),
    registered_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    orgs_managed INTEGER[],
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create user_roles table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,  -- ProjectRole enum
    PRIMARY KEY (user_id, project_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_user_roles_project ON user_roles(project_id);

-- Add tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);