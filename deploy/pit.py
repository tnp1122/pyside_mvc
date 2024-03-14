import logging
import os
import subprocess
import sys
import winreg
from datetime import datetime

from dulwich.porcelain import fetch, clone, pull
from dulwich.repo import Repo

remote_url = 'https://github.com/tnp1122/pit_deploy.git'
pit_path = os.path.join(os.getcwd(), "pit")
exe_path = os.path.join(pit_path, "main.exe")
git_path = os.path.join(pit_path, ".git")

VERSION = "version"


class SettingManager:
    def __init__(self):
        self.reg_key = winreg.HKEY_CURRENT_USER
        self.reg_path = "Software\\Jen Life\\PIT"

    def _set_value(self, key, value):
        try:
            winreg.CreateKey(self.reg_key, self.reg_path)
            registry_key = winreg.OpenKey(self.reg_key, self.reg_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, key, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
        except Exception as e:
            logging.error(f"An error occurred while setting value: {e}")

    def _get_value(self, key, default_value=None):
        try:
            registry_key = winreg.OpenKey(self.reg_key, self.reg_path, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, key)
            winreg.CloseKey(registry_key)

            return value
        except WindowsError:
            return default_value
        except Exception as e:
            return default_value

    # def _remove_value(self, key):
    #     try:
    #         # 레지스트리 키 열기
    #         reg_key = winreg.OpenKey(self.reg_key, self.reg_path, 0, winreg.KEY_WRITE)
    #
    #         # 값 제거
    #         winreg.DeleteValue(reg_key, key)
    #     except FileNotFoundError:
    #         logging.error("Registry key or value not found.")
    #     except Exception as e:
    #         logging.error(f"An error occurred while removing value: {e}")
    #     finally:
    #         winreg.CloseKey(reg_key)

    def get_pit_version(self):
        return self._get_value(VERSION, "unknown")

    def set_pit_version(self, version_str):
        self._set_value(VERSION, version_str)


def logging_config():
    current_directory = os.getcwd()
    log_folder_path = os.path.join(current_directory, "log")
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)

    now = datetime.now()
    now_str = now.strftime("%y%m%d_%H%M%S")
    file_name = os.path.join(log_folder_path, f"{now_str}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def clone_git_repo():
    logging.info("레포지토리를 클론합니다...")
    clone(remote_url, pit_path)
    logging.info("레포지토리가 클론되었습니다.")


def check_pit_version():
    logging.info("현재 버전을 확인합니다.")
    sm = SettingManager()
    current_version = sm.get_pit_version()
    logging.info(f"현재 버전: {current_version}")

    if current_version == "unknown":
        logging.info("버전이 확인되지 않습니다.")
        clone_git_repo()
    elif not os.path.exists(git_path):
        logging.info("깃이 존재하지 않습니다.")
        clone_git_repo()

    logging.info("커밋 내역을 확인합니다.")

    fetch(pit_path)
    repo = Repo(pit_path)

    refs = repo.get_refs()
    sha = refs[b"refs/remotes/origin/main"]
    commit = repo[sha]
    commit_message = commit.message.decode()

    resent_version = commit_message.split(" ")[1].strip()
    logging.info(f"배포 버전: {resent_version}")

    if current_version == resent_version:
        logging.info("최신 버전입니다.")

    else:
        logging.info("레포지토리를 업데이트합니다...")
        pull(pit_path, "origin", [b"main"])
        sm.set_pit_version(resent_version)
        logging.info("레포지토리 업데이트가 완료되었습니다.")

    logging.info("PIT 분석도구를 실행합니다.")
    subprocess.call([exe_path])


def main():
    logging.basicConfig(level=logging.INFO)
    check_pit_version()


if __name__ == '__main__':
    logging_config()
    sys.excepthook = exception_hook
    main()
