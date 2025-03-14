import os
import re
import requests
from datetime import datetime


BODY_REG = r"https://github\.com/uazo/cromite/issues/.*\b"

dt = datetime.today().strftime("[%d-%m-%Y | %H:%M:%S UTC] : ")

url = "https://api.github.com/repos/uazo/cromite/releases/latest"

chats = [1413518510, -1001747127529, -1001552719792]


def get_new_release():
    fn = "release.tag"
    req = requests.get(url).json()
    new_release = req["tag_name"]
    with open(fn, "r") as r:
        old_tag = r.read().strip()
    if old_tag == new_release:
        return (None, None)
    html_url = req["html_url"]
    try:
        comment_url = re.findall(BODY_REG, req["body"])[0]
    except IndexError:
        comment_url = None
    with open("releases.log", "a+") as rl:
        rl.write(dt + new_release + "\n")
    with open(fn, "w") as f:
        f.write(new_release)
    return (html_url, comment_url)


def get_changelog(cmtu):
    if not cmtu:
        return None
    cmtn = cmtu.split("/")[-1].split("#")[0]
    api = f"https://api.github.com/repos/uazo/cromite/issues/{cmtn}/comments"
    resp = requests.get(api).json()
    changes = []
    for i in resp:
        if cmtu == i["html_url"]:
            changes = i["body"].split("- ")[1:]
            break
    if not changes:
        return f"see [#{cmtn}]({cmtu})"
    changelog = "*CHANGES:*\n\n"
    for i in changes:
        changelog += f"• {i}"
    return changelog


def release():
    html, comm = get_new_release()
    if not html:
        return None
    dl = html.replace("/tag/", "/download/")
    version = html.split("/")[-1].split("-")[0]
    changes = get_changelog(comm)
    if changes:
        changelog = f"\n{changes}\n`{'_'*20}`\n"
    else:
        changelog = ""


    text = f"""[Cromite {version}]({html})
`{'_'*20}`
{changelog}
*DOWNLOADS:*

[arm64_ChromePublic.apk]({dl}/arm64_ChromePublic.apk)

[arm_ChromePublic.apk]({dl}/arm_ChromePublic.apk)

[x64_ChromePublic.apk]({dl}/x64_ChromePublic.apk)

[chrome-win.zip]({dl}/chrome-win.zip)

[chrome-lin64.tar.gz]({dl}/chrome-lin64.tar.gz)
`{'_'*20}`

[DONATE](https://github.com/uazo/cromite?tab=readme-ov-file#donate)
`{'_'*20}`"""

    return text


def update():
    token = os.getenv("BOT_TOKEN")
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    new_release = release()
    if not new_release:
        return
    for chat in chats:
        data = {
            "chat_id": chat,
            "text": new_release,
            "parse_mode": "MARKDOWN",
            "disable_web_page_preview": True,
        }
        requests.post(api_url, data=data)
    return


update()
