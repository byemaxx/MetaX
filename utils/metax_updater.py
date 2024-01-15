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

class Updater:
    def __init__(self, MetaXGUI, version, splash, show_message=False):
        self.MainWindow = MetaXGUI.MainWindow
        self.metaXGUI = MetaXGUI
        self.splash = splash
        self.show_message = show_message
        self.current_version = version
        self.current_changes = []
        self.remote_path =None
        self.remote_version = None


    def parse_changelog_md(self):
        change_log_path = os.path.join(self.remote_path, "ChangeLog.md")
        print(f"Change log path: {change_log_path}")
        with open(change_log_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        self.changelog_dict = {}
        current__scaned_version = None
        for line in lines:
            line = line.strip()
            if line.startswith('# Version:'):
                if current__scaned_version:
                    self.changelog_dict[current__scaned_version] = self.current_changes
                current__scaned_version = line.split(":")[1].strip()
                self.current_changes = []
            elif line.startswith('-'):
                self.current_changes.append(line[1:].strip())

        if current__scaned_version:
            self.changelog_dict[current__scaned_version] = self.current_changes
        return self.changelog_dict

    @staticmethod
    def compare_version(version1, version2):
        return tuple(map(int, version1.split("."))) > tuple(map(int, version2.split(".")))

    def get_updates_between_versions(self, new_version):
        updates = [(version, changes) for version, changes in self.changelog_dict.items()
                   if self.compare_version(version, self.current_version) and not self.compare_version(version, new_version)]
        return updates

    def get_str(self):
        self.changelog_dict = self.parse_changelog_md()
        new_version = sorted(self.changelog_dict.keys(), key=lambda v: list(map(int, v.split('.'))))[-1]
        updates = self.get_updates_between_versions(new_version)
        result = "\n".join(f"Version {version}:\n" + "\n".join(f"  - {change}" for change in changes) for version, changes in updates)
        return result


    def update_metax(self, remote_version, remote_path):
        # ask if user want to update
        try:
            change_log_str = self.get_str()
            

        except Exception as e:
            print(f"Read change log failed: {e}")
            change_log_str = "No change log."

        reply = QMessageBox.question(self.MainWindow, "Update",
                                     f"MetaX new version is available. Do you want to update?\
                                     \ncurrent version: {self.current_version}\nremote version: {remote_version}\n\nChange log:\n{change_log_str}",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.metaXGUI.show_message("Updating MetaX...", "Updating...")
            # set update_required flag to True
            # this flag will stop MainWindow.show()
            self.metaXGUI.update_required = True

            try:
                # replace remote MetaX folder with local MetaX folder
                local_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # copy all files from remote to local
                for root, dirs, files in os.walk(remote_path):
                    for file in files:
                        remote_file = os.path.join(root, file)
                        local_file = remote_file.replace(remote_path, local_path)
                        os.makedirs(os.path.dirname(local_file), exist_ok=True)
                        with open(remote_file, "rb") as f1:
                            with open(local_file, "wb") as f2:
                                f2.write(f1.read())
                                
                QMessageBox.information(self.MainWindow, "Update", f"MetaX has been updated to {remote_version}. Please restart MetaX.")
                # force close MetaX without triggering closeEvent
                QtWidgets.QApplication.quit()
                # close the QSplashScreen
                self.splash.finish(self.MainWindow)
                sys.exit()
                
                
            except Exception as e:
                QMessageBox.warning(self.MainWindow, "Update", f'Update failed: {e}')


    def check_update(self, show_message=False):
        try:
            remote_path = "Z:/Qing/MetaX"
            # check if remote path exists
            if not os.path.exists(remote_path):
                print("Remote path does not exist.")
                if show_message:
                    QMessageBox.warning(self.MainWindow, "Update", "Remote path does not exist.")
                return
            # Check remote version
            dir_list = os.listdir(remote_path)
            # check if there is a folder named start with "Update_Package_" 
            update_package = [x for x in dir_list if x.startswith("Update_Package_")][0] #Update_Package_1.87.0_(2024-01-12)
            
            remote_path = os.path.join(remote_path, update_package, "MetaX")
            self.remote_path = remote_path
            
            remote_version = update_package.split("_")[2]
            self.remote_version = remote_version
            # compare remote version with current version

            if Updater.compare_version(remote_version, self.current_version):
                print(f"New version is available:\nCurrent version: {self.current_version}\nRemote version: {remote_version}")
                self.update_metax(remote_version, remote_path)
            else:
                print("MetaX is up to date.")
                if show_message:
                    QMessageBox.information(self.MainWindow, "Update", "MetaX is up to date.")
        except Exception as e:
            print(f"Check update failed:\n{e}")
            if show_message:
                QMessageBox.warning(self.MainWindow, "Update", f"Check update failed:\n{e}")


