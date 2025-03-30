-- Insert users

        INSERT INTO users (
            id, username, role, profile_img, name, city, country,
            email_address, is_email_verified, is_expert, api_key,
            registered_at, last_login_at
        ) VALUES (
            1,
            'user1',
            'MAPPER',
            'https://example.com/profile1.jpg',
            'User 1',
            'City 1',
            'Country 1',
            'user1@example.com',
            false,
            false,
            'api_key_1',
            '2025-03-30 12:02:29.855607+00:00',
            '2025-03-30 12:02:29.855607+00:00'
        );

        INSERT INTO users (
            id, username, role, profile_img, name, city, country,
            email_address, is_email_verified, is_expert, api_key,
            registered_at, last_login_at
        ) VALUES (
            2,
            'user2',
            'MAPPER',
            'https://example.com/profile2.jpg',
            'User 2',
            'City 2',
            'Country 2',
            'user2@example.com',
            true,
            false,
            'api_key_2',
            '2025-03-30 12:02:29.855607+00:00',
            '2025-03-30 12:02:29.855607+00:00'
        );

        INSERT INTO users (
            id, username, role, profile_img, name, city, country,
            email_address, is_email_verified, is_expert, api_key,
            registered_at, last_login_at
        ) VALUES (
            3,
            'user3',
            'MAPPER',
            'https://example.com/profile3.jpg',
            'User 3',
            'City 3',
            'Country 3',
            'user3@example.com',
            false,
            true,
            'api_key_3',
            '2025-03-30 12:02:29.855607+00:00',
            '2025-03-30 12:02:29.855607+00:00'
        );

        INSERT INTO users (
            id, username, role, profile_img, name, city, country,
            email_address, is_email_verified, is_expert, api_key,
            registered_at, last_login_at
        ) VALUES (
            4,
            'user4',
            'MAPPER',
            'https://example.com/profile4.jpg',
            'User 4',
            'City 4',
            'Country 4',
            'user4@example.com',
            true,
            false,
            'api_key_4',
            '2025-03-30 12:02:29.855607+00:00',
            '2025-03-30 12:02:29.855607+00:00'
        );

        INSERT INTO users (
            id, username, role, profile_img, name, city, country,
            email_address, is_email_verified, is_expert, api_key,
            registered_at, last_login_at
        ) VALUES (
            5,
            'user5',
            'MAPPER',
            'https://example.com/profile5.jpg',
            'User 5',
            'City 5',
            'Country 5',
            'user5@example.com',
            false,
            false,
            'api_key_5',
            '2025-03-30 12:02:29.855607+00:00',
            '2025-03-30 12:02:29.855607+00:00'
        );

-- Insert user roles

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (1, 1, 'PROJECT_MANAGER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (1, 2, 'MAPPER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (1, 3, 'VALIDATOR');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (2, 1, 'MAPPER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (2, 2, 'VALIDATOR');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (2, 3, 'PROJECT_MANAGER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (3, 1, 'VALIDATOR');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (3, 2, 'PROJECT_MANAGER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (3, 3, 'MAPPER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (4, 1, 'PROJECT_MANAGER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (4, 2, 'MAPPER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (4, 3, 'VALIDATOR');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (5, 1, 'MAPPER');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (5, 2, 'VALIDATOR');

            INSERT INTO user_roles (user_id, project_id, role)
            VALUES (5, 3, 'PROJECT_MANAGER');
