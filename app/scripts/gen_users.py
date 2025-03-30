from datetime import datetime, timezone
import json

def generate_user_inserts(num_users=5):
    """Generate INSERT statements for users table."""
    inserts = []
    now = datetime.now(timezone.utc)
    
    for i in range(1, num_users + 1):
        sql = f"""
        INSERT INTO users (
            id, username, role, profile_img, name, city, country,
            email_address, is_email_verified, is_expert, api_key,
            registered_at, last_login_at
        ) VALUES (
            {i},
            'user{i}',
            'MAPPER',
            'https://example.com/profile{i}.jpg',
            'User {i}',
            'City {i}',
            'Country {i}',
            'user{i}@example.com',
            {str(i % 2 == 0).lower()},
            {str(i % 3 == 0).lower()},
            'api_key_{i}',
            '{now}',
            '{now}'
        );"""
        inserts.append(sql)
    return inserts

def generate_user_roles_inserts(num_users=5, num_projects=3):
    """Generate INSERT statements for user_roles table."""
    inserts = []
    roles = ['MAPPER', 'VALIDATOR', 'PROJECT_MANAGER']
    
    for user_id in range(1, num_users + 1):
        for project_id in range(1, num_projects + 1):
            role = roles[(user_id + project_id) % len(roles)]
            sql = f"""
            INSERT INTO user_roles (user_id, project_id, role)
            VALUES ({user_id}, {project_id}, '{role}');"""
            inserts.append(sql)
    return inserts

def main():
    # Generate SQL statements
    user_inserts = generate_user_inserts(5)
    role_inserts = generate_user_roles_inserts(5, 3)
    
    # Write to file
    with open('./app/scripts/insert_data.sql', 'w') as f:
        f.write('-- Insert users\n')
        f.write('\n'.join(user_inserts))
        f.write('\n\n-- Insert user roles\n')
        f.write('\n'.join(role_inserts))
        f.write('\n')

if __name__ == '__main__':
    main() 