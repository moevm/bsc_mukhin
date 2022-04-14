import argparse
from playwright.sync_api import sync_playwright, Cookie


def invite_link_to_web(link: str) -> str:
    left_part = link.split('?')[0]
    meeting_id = left_part.split('/')[-1]
    return f'https://us04web.zoom.us/wc/{meeting_id}/start'


def get_cookies(login: str, password: str, timeout=1000) -> list[Cookie]:
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        page = browser.new_page()
        page.goto('https://zoom.us/signin')
        page.wait_for_timeout(timeout)
        page.click('button#onetrust-accept-btn-handler')
        page.wait_for_timeout(timeout)
        page.fill('#email', login)
        page.wait_for_timeout(timeout)
        page.fill('#password', password)
        page.wait_for_timeout(timeout)

        page.click('button.signin')
        page.wait_for_timeout(timeout*2)
        cookies = page.context.cookies()
        browser.close()
        return cookies


def _change_host(cookies: list[Cookie], link, new_host, timeout=1000):
    counter = 0
    limit = 3
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.context.add_cookies(cookies)
        new_link = invite_link_to_web(link)
        page.goto(new_link)
        while page.query_selector('#email') is not None and counter < limit:
            page.goto(new_link)
            page.wait_for_timeout(timeout)
            print(f'Попытка {counter + 1}/{limit}, не удалось перейти в конференцию')
            counter += 1

        if counter == limit:
            print('Не смогли воспользоваться cookies и выполнить задачу')
            return 1

        page.locator('text=Участники').click()
        page.wait_for_timeout(timeout)
        for person in page.query_selector_all('[role="application"]')[1:]:
            if new_host in person.text_content():
                person.hover()
                person.query_selector('text=Подробнее').click()
                make_organization_button = person.query_selector('text=Сделать организатором')
                if make_organization_button is None:
                    print('Скрипт не является организатором конференции')
                    return 2
                else:
                    make_organization_button.click()
                box = page.query_selector('[aria-label="make host confirm dialog"]')
                box.query_selector('text=Да').click()
                browser.close()
                return 0


def change_host(login: str, password: str, link: str, new_host: str, timeout: int = 1000) -> int:
    cookies = get_cookies(login, password, timeout)
    return _change_host(cookies, link, new_host, timeout)


def main():
    parser = argparse.ArgumentParser(description='host changer')
    parser.add_argument('-l', '--zoom_login', type=str, help='zoom login', required=True)
    parser.add_argument('-p', '--zoom_password', type=str, help='zoom password', required=True)
    parser.add_argument('-i', '--invite', type=str, help='invite link', required=True)
    parser.add_argument('-n', '--new_host', type=str, help='new host name', required=True)

    args = parser.parse_args()
    return change_host(args.zoom_login, args.zoom_password, args.invite, args.new_host)


if __name__ == '__main__':
    # https://us04web.zoom.us/j/5321448993?pwd=aXE4UENQcmFwV2Z4UGI2VW1NTE1LUT09
    # https://us04web.zoom.us/wc/5321448993/start
    main()
