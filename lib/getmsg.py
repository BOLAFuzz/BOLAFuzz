# -*-coding:utf-8 -*-

def login_credential(credentials):
    select_input = input('[>>>>] select username/set credential(username:password)/back: ')

    if 'back' == select_input:
        return
    elif ':' in select_input:
        username, password = select_input.split(':')
        return f"{username}:{password}"
    elif credentials is not None:
        for credential in credentials:
            if credential['username'] == select_input:
                return f"{select_input}:{credential['password']}"

    return


def target_url(urls):
    select_input = input('[>>>>] select url number/set url/back: ')

    if 'back' == select_input:
        return
    elif select_input.strip().startswith('https://') or select_input.strip().startswith('http://'):
        return select_input.strip().lower()
    elif urls is not None:
        for url in urls:
            if urls['url'] == select_input.strip().lower():
                return urls['url']

    return


