# Description: Parse the changelog.md file and return the changes between two versions
# changelog format:
# # Version: 1.88.6
# ## Date: 2024-01-15
# ### Changes:
# - Fixed: the QSplashScreen doesn't colse after update.
# - Add: Add changelog display. when new version avaliable.

import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import subprocess
import urllib.request
import pathlib
import zipfile
import shutil
import socket
import urllib.error



class Updater:
    def __init__(self, MetaXGUI, version, splash, show_message=False, branch='main'):
        self.MainWindow = MetaXGUI.MainWindow
        self.metaXGUI = MetaXGUI
        self.splash = splash
        self.show_message = show_message
        self.current_version = version
        self.current_api = 0
        self.current_changes = []
        self.metax_folder_path = None
        self.version_path = None
        self.remote_path =None
        self.remote_version = None
        self.remote_api = None
        self.update_libs = []
        self.install_libs = []
        self.uninstall_libs = []
        self.branch = branch
        
        self.remote_change_log_path = ""
        self.remote_version_path = ""
        self.remote_project_zip_download_path = ""
        self.set_init_path()
        self.set_current_version_and_api()


    def set_init_path(self):
        self.remote_version_path = f"https://raw.githubusercontent.com/byemaxx/MetaX/{self.branch}/utils/version.py"
        self.remote_change_log_path = f"https://raw.githubusercontent.com/byemaxx/MetaX/{self.branch}/Docs/ChangeLog.md"
        self.remote_project_zip_download_path = f"https://github.com/byemaxx/MetaX/archive/refs/heads/{self.branch}.zip"

    def set_current_version_and_api(self):
        # MetaX folder path is this file's parent and the parent's parent
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        metax_folder_path = os.path.dirname(current_script_path)
        print(f"MetaX folder path: {metax_folder_path}")
        self.metax_folder_path = metax_folder_path
        # get the version and API from version.py
        self.version_path = os.path.join(metax_folder_path, 'utils/version.py')
        try:
            with open(self.version_path, 'r') as file:
                local_version_str = file.read()
                self.current_version = local_version_str.split("__version__ = '")[1].split("'")[0]
                self.current_api = local_version_str.split("API_version = '")[1].split("'")[0]
        except Exception as e:
            print(f"Check local API failed: {e}")

            
        print(f"Local version: {self.current_version}. API: {self.current_api}")
        
    def check_update_status(self):
        try:
            # get the version from version.py
            with open(self.version_path, 'r') as file:
                local_version_str = file.read()
                new_local_version = local_version_str.split("__version__ = '")[1].split("'")[0]

            if new_local_version == self.remote_version:
                return True
            else:
                return False
        except Exception as e:
            print(f"Check update status failed: {e}")
            return False
            
        
    
    def parse_changelog_md(self):
        # change_log_path = os.path.join(self.remote_path, "ChangeLog.md")
        change_log_re = urllib.request.urlopen(self.remote_change_log_path)
        
        if change_log_re.status != 200:
            raise Exception(f"Read change log failed: {change_log_re.status}")
        
        change_log = change_log_re.read().decode("utf-8")
        lines = change_log.split("\n")
        # with open(change_log_path, 'r', encoding='utf-8') as file:
        #     lines = file.readlines()
        self.changelog_dict = {}
        current_scanned_version = None
        for line in lines:
            line = line.strip()
            if line.startswith('# Version:'):
                if current_scanned_version:
                    self.changelog_dict[current_scanned_version] = self.current_changes
                current_scanned_version = line.split(":")[1].strip()
                self.current_changes = []
            elif line.startswith('-'):
                self.current_changes.append(line[1:].strip())

        if current_scanned_version:
            self.changelog_dict[current_scanned_version] = self.current_changes
        return self.changelog_dict

    @staticmethod
    def compare_version(version1, version2):
        return tuple(map(int, version1.split("."))) > tuple(map(int, version2.split(".")))

    def get_updates_between_versions(self, new_version: str|None = None):
        if new_version is None:
            new_version = self.remote_version
        updates = [(version, changes) for version, changes in self.changelog_dict.items()
                   if self.compare_version(version, self.current_version) and not self.compare_version(version, new_version)]
        return updates

    def get_str(self):
        self.changelog_dict = self.parse_changelog_md()
        new_version = sorted(self.changelog_dict.keys(), key=lambda v: list(map(int, v.split('.'))))[-1]
        updates = self.get_updates_between_versions(new_version)
        result = "\n".join(f"Version {version}:\n" + "\n".join(f"  - {change}" for change in changes) for version, changes in updates)
        return result



    def download_project_zip_and_unzip(self):
        home_path = pathlib.Path.home()
        # if 'MetaX/update' not in home_path, create it
        metaX_update_path = os.path.join(home_path, 'MetaX/update')
        # if the folder exists, delete it first
        if os.path.exists(metaX_update_path):
            shutil.rmtree(metaX_update_path)
        # then create it
        os.makedirs(metaX_update_path)

        # download the project zip file
        project_zip_path = os.path.join(metaX_update_path, 'MetaX.zip')
        try:
            # Adding a timeout to the download process
            with urllib.request.urlopen(self.remote_project_zip_download_path, timeout=60) as response:
                with open(project_zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)

            # Unzip the project zip file
            with zipfile.ZipFile(project_zip_path, 'r') as zip_ref:
                zip_ref.extractall(metaX_update_path)
                
            # Optionally, delete the project zip file after extraction
            os.remove(project_zip_path)
            
            
            return True

        except urllib.error.HTTPError as e:
            print(f"URL Error during download: {e.reason}")
            return False
        except socket.timeout:
            print("Download timed out")
            return False
        except Exception as e:
            print(f"Download project zip failed: {e}")
            return False

            
        
    def replace_metax_dir(self):
            # MetaX folder path is this file's parent and the parent's parent
            current_script_path = os.path.dirname(os.path.abspath(__file__))
            metax_folder_path = os.path.dirname(current_script_path)
            print(f"MetaX folder path: {metax_folder_path}")
            
            #remove all files in the metax folder, except the __pycache__ folder and data folder and tsv files
            for root, dirs, files in os.walk(metax_folder_path):
                for file in files:
                    # if file != '__init__.py' and file != '__pycache__' and not file.endswith('.tsv'):
                    if file != '__init__.py' and file != '__pycache__' and not file.endswith('.pyc'):
                        os.remove(os.path.join(root, file))
                for dir in dirs:
                    # if dir not in ['__pycache__', 'data', 'example_data']:
                    if dir not in ['__pycache__']:
                        shutil.rmtree(os.path.join(root, dir))

            # move the new MetaX folder to the old MetaX folder
            home_path = pathlib.Path.home()
            metaX_update_path = os.path.join(home_path, 'MetaX/update')
            project_folder_path = os.path.join(metaX_update_path, f'MetaX-{self.branch}') # /home/user/MetaX/update/MetaX-main or /home/user/MetaX/update/MetaX-dev
            for root, dirs, files in os.walk(project_folder_path):
                for file in files:
                    shutil.move(os.path.join(root, file), os.path.join(metax_folder_path, file))
                for dir in dirs:
                    shutil.move(os.path.join(root, dir), os.path.join(metax_folder_path, dir))
            


    def update_metax(self):
        # ask if user want to update
        try:
            change_log_str = self.get_str()
            
        except Exception as e:
            print(f"Read change log failed: {e}")
            change_log_str = "No change log."
            
        if self.current_api != self.remote_api:
            QMessageBox.warning(self.MainWindow, "Update", f"MetaX new version is available with a new API. Please download the new version manually.\n\n\
            current version: {self.current_version}\nremote version: {self.remote_version}\n\nChange log:\n{change_log_str}")
            return

        reply = QMessageBox.question(self.MainWindow, "Update",
                                     f"MetaX new version is available. Do you want to update?\
                                     \ncurrent version: {self.current_version}\nremote version: {self.remote_version}\n\nChange log:\n{change_log_str}",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.metaXGUI.show_message("Updating MetaX...", "Updating...")
            # set update_required flag to True
            # this flag will stop MainWindow.show()
            self.metaXGUI.update_required = True

            try:
                download_success = self.download_project_zip_and_unzip()
                if download_success is False:
                    QMessageBox.warning(self.MainWindow, "Update", "Download failed. Please try again later or update manually.")
                    return
                # replace the old MetaX folder with the new one
                replace_success = self.replace_metax_dir()
                if replace_success is False:
                    QMessageBox.warning(self.MainWindow, "Update", "An error occurred while replacing the MetaX directory. Please try again later or update manually.")
                    return
                
                # check if the update is successful
                if self.check_update_status():
                    msg = f"MetaX has been updated to {self.remote_version}. Please restart MetaX."
                else:
                    msg = f"Warning: MetaX update failed. Still in version {self.current_version}. Please try again later or update manually."
                
                QMessageBox.information(self.MainWindow, "Update", msg)
                # force close MetaX without triggering closeEvent
                QtWidgets.QApplication.quit()
                # close the QSplashScreen
                self.splash.finish(self.MainWindow)
                sys.exit()
                
                
            except Exception as e:
                QMessageBox.warning(self.MainWindow, "Update", f'Update failed: {e}')


    def check_update(self, show_message=False):
        print(f"Checking update from {self.branch} branch...")
        # check if remote path available
        try:
            # check if remote path available
            # __version__ = '1.102.10'
            # API = 1
            remote_version_re= urllib.request.urlopen(self.remote_version_path)
            if remote_version_re.status != 200:
                print(f"Check update failed: {remote_version_re.status}")
                return
            else:
                remote_version_str = remote_version_re.read().decode("utf-8")
                self.remote_version = remote_version_str.split("__version__ = '")[1].split("'")[0]
                try:
                    remote_version_api = remote_version_str.split("API_version = '")[1].split("'")[0]
                except Exception as e:
                    print(f"Check API failed: {e}")
                    # set API to 0 if failed
                    remote_version_api = 0
                    
                print(f"Remote version: {self.remote_version}. Remote API: {remote_version_api}")

                self.remote_api = remote_version_api    
                
                if self.compare_version(self.remote_version, self.current_version): # return True if remote_version > current_version
                    print(f"New version is available:\nCurrent version: {self.current_version}\nRemote version: {self.remote_version}")
                    self.update_metax()
                else:
                    print("MetaX is up to date.")
                    if show_message:
                        QMessageBox.information(self.MainWindow, "Update", f"MetaX is up to date.\n\nCheck version: {self.branch}\n\nCurrent version: {self.current_version}\nRemote version: {self.remote_version}")

        except Exception as e:
            print(f"Check update failed:\n{e}")
            if show_message:
                QMessageBox.warning(self.MainWindow, "Update", "Warning: Github is not available for now. Please try again later or update manually.")
            return
            

    #! Have not tested this function
    def change_libs(self):
        if len(self.update_libs) > 0:
            for lib in self.update_libs:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", lib])
                except Exception as e:
                    print(f"Update {lib} failed: {e}")
        if len(self.install_libs) > 0:
            for lib in self.install_libs:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                except Exception as e:
                    print(f"Install {lib} failed: {e}")
        if len(self.uninstall_libs) > 0:
            for lib in self.uninstall_libs:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", lib, "-y"])
                except Exception as e:
                    print(f"Uninstall {lib} failed: {e}")
                    
                    
# TEST CODE
class MockMainWindow:
    def __init__(self):
        self.update_required = False

    def show_message(self, title, message):
        print(f"{title}: {message}")

class MockMetaXGUI:
    def __init__(self):
        self.MainWindow = MockMainWindow()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  #
    mock_gui = MockMetaXGUI()
    
    updater = Updater(mock_gui, '1.101.5', None, show_message=True, branch='dev')
    updater.check_update(show_message=True)
    

    sys.exit(app.exec_())  # 启动事件循环
