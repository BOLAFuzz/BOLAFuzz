# MySQL配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'xxx',
    'database': 'acfuzz',
    'charset': 'utf8mb4'
}

# 数据库表结构
TABLES = {
    'websites': '''
        CREATE TABLE IF NOT EXISTS websites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            website_name VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            UNIQUE KEY (website_name, username)
        )
    ''',
    'api_routes': '''
        CREATE TABLE IF NOT EXISTS api_routes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            website_id INT NOT NULL,
            route VARCHAR(255) NOT NULL,
            FOREIGN KEY (website_id) REFERENCES websites(id),
            UNIQUE KEY (website_id, route)
        )
    ''',
    'requests': '''
        CREATE TABLE IF NOT EXISTS requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            route_id INT NOT NULL,
            request_data JSON,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (route_id) REFERENCES api_routes(id)
        )
    ''',
    'responses': '''
        CREATE TABLE IF NOT EXISTS responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            route_id INT NOT NULL,
            response_data JSON,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (route_id) REFERENCES api_routes(id)
        )
    '''
}

