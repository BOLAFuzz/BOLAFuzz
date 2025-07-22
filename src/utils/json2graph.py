# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse
from py2neo import Graph, Node, Relationship

# 连接到Neo4j数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "xxxxxx"))

def clear_neo4j():
    # 删除所有节点和关系
    with graph.begin() as tx:
        tx.run("MATCH (n) DETACH DELETE n")

def load_json_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def create_node(properties, labels):
    node = Node(labels, **{k: v for k, v in properties.items() if v is not None})
    graph.merge(node, **{labels[0]: properties})  # 确保每个节点都有唯一的属性来合并
    return node

def import_data_to_neo4j(data, file_path):
    for domain, users_data in data.items():
        domain_node = create_node({"name": domain}, "Domain")
        
        for username, requests_responses in users_data.items():
            user_node = create_node({"name": username}, "User")
            # 创建Domain和User之间的关系
            relationship = Relationship(domain_node, "HOSTS", user_node)
            graph.merge(relationship, "Domain", "HOSTS", "User")
            
            for data_to_save in requests_responses:
                request_node = create_node({"url": data_to_save["request"]["url"], "method": data_to_save["request"]["method"]}, "Request")
                # 创建User和Request之间的关系
                request_relationship = Relationship(user_node, "MAKES", request_node)
                graph.merge(request_relationship, "User", "MAKES", "Request")
                
                # 处理请求头
                headers_node = create_node({"headers": data_to_save["request"]["headers"]}, "Headers")
                headers_relationship = Relationship(request_node, "HAS_HEADERS", headers_node)
                graph.merge(headers_relationship, "Request", "HAS_HEADERS", "Headers")
                
                # 处理响应头
                response_node = create_node({"url": data_to_save["response"]["url"], "headers": data_to_save["response"]["headers"]}, "Response")
                response_relationship = Relationship(request_node, "RECEIVES", response_node)
                graph.merge(response_relationship, "Request", "RECEIVES", "Response")

def main():
    file_path = "traffic_data.json"  # JSON文件路径
    clear_neo4j()  # 清空Neo4j数据库
    data = load_json_data(file_path)
    import_data_to_neo4j(data, file_path)

if __name__ == "__main__":
    main()