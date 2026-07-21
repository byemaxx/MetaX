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
from PyQt5.QtGui import QIcon
import subprocess
import urllib.request
import pathlib
import zipfile
import shutil
import socket
import urllib.error
import importlib.metadata as importlib_metadata

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

try:
    from packaging.markers import default_environment
    from packaging.requirements import InvalidRequirement, Requirement
except ModuleNotFoundError:
    from pip._vendor.packaging.markers import default_environment
    from pip._vendor.packaging.requirements import InvalidRequirement, Requirement



class Updater:
    def __init__(self, MetaXGUI, version, splash, show_message=False, branch='main', is_test_mode=False):
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
        self.dependencies_updated = False
        self.update_log_dialog = None
        self.update_log_browser = None
        self.update_log_close_button = None
        self.branch = branch
        self.is_test_mode = is_test_mode
        
        self.remote_change_log_path = ""
        self.remote_version_path = ""
        self.remote_project_zip_download_path = ""
        self.set_init_path()
        if not self.is_test_mode:
            self.set_current_version_and_api()


    def set_init_path(self):
        self.remote_version_path = f"https://raw.githubusercontent.com/byemaxx/MetaX/{self.branch}/metax/utils/version.py"
        self.remote_change_log_path = f"https://raw.githubusercontent.com/byemaxx/MetaX/{self.branch}/Docs/ChangeLog.md"
        self.remote_project_zip_download_path = f"https://github.com/byemaxx/MetaX/archive/refs/heads/{self.branch}.zip"

    def get_update_workspace_path(self):
        return os.path.join(pathlib.Path.home(), 'MetaX/update')

    def get_downloaded_project_folder_path(self):
        return os.path.join(self.get_update_workspace_path(), f'MetaX-{self.branch}')

    def clear_update_required_flag(self):
        if hasattr(self.metaXGUI, "update_required"):
            self.metaXGUI.update_required = False

    def show_update_log_dialog(self):
        if self.update_log_dialog is not None:
            self.update_log_dialog.show()
            return

        dialog = QtWidgets.QDialog(self.MainWindow)
        dialog.setWindowTitle("Updating MetaX")
        dialog.setWindowIcon(self.MainWindow.windowIcon())
        layout = QtWidgets.QVBoxLayout(dialog)

        text_browser = QtWidgets.QTextBrowser()
        text_browser.setReadOnly(True)
        layout.addWidget(text_browser)

        button_box = QtWidgets.QDialogButtonBox()
        close_button = button_box.addButton(QtWidgets.QDialogButtonBox.Close)
        close_button.setEnabled(False)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.resize(700, 450)
        dialog.show()
        QtWidgets.QApplication.processEvents()

        self.update_log_dialog = dialog
        self.update_log_browser = text_browser
        self.update_log_close_button = close_button

    def append_update_log(self, message):
        print(message)
        if self.update_log_browser is None:
            return

        self.update_log_browser.append(message)
        scrollbar = self.update_log_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        QtWidgets.QApplication.processEvents()

    def finish_update_log_dialog(self):
        if self.update_log_close_button is not None:
            self.update_log_close_button.setEnabled(True)
        QtWidgets.QApplication.processEvents()

    def set_current_version_and_api(self):
        # MetaX folder path is this file's parent and the parent's parent
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        metax_folder_path = os.path.dirname(current_script_path)
        print(f"MetaX folder path: {metax_folder_path}")
        self.metax_folder_path = metax_folder_path
        
        if self.is_test_mode:
            print(f"Test mode: Using version {self.current_version}")
            return
            
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
            if self.is_test_mode:
                return self.current_version == self.remote_version

            version_path = pathlib.Path(self.version_path)
            if not version_path.is_file():
                raise FileNotFoundError(f"File does not exist: {version_path}")
            # get the version from version.py
            with open(version_path, 'r') as file:
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
        metaX_update_path = self.get_update_workspace_path()
        # if the folder exists, delete it first
        if os.path.exists(metaX_update_path):
            self.append_update_log(f"Cleaning update workspace: {metaX_update_path}")
            shutil.rmtree(metaX_update_path)
        # then create it
        os.makedirs(metaX_update_path)

        # download the project zip file
        project_zip_path = os.path.join(metaX_update_path, 'MetaX.zip')
        try:
            self.append_update_log(f"Downloading MetaX from {self.remote_project_zip_download_path}")
            # Adding a timeout to the download process
            with urllib.request.urlopen(self.remote_project_zip_download_path, timeout=60) as response:
                total_size_header = response.headers.get("Content-Length")
                total_size = int(total_size_header) if total_size_header else 0
                downloaded_size = 0
                next_progress_log = 0
                with open(project_zip_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded_size += len(chunk)
                        if downloaded_size >= next_progress_log:
                            downloaded_mb = downloaded_size / (1024 * 1024)
                            if total_size > 0:
                                total_mb = total_size / (1024 * 1024)
                                percent = (downloaded_size / total_size) * 100
                                self.append_update_log(f"Downloaded {downloaded_mb:.1f}/{total_mb:.1f} MB ({percent:.1f}%).")
                            else:
                                self.append_update_log(f"Downloaded {downloaded_mb:.1f} MB.")
                            next_progress_log = downloaded_size + (5 * 1024 * 1024)

            # Unzip the project zip file
            self.append_update_log("Extracting downloaded package...")
            with zipfile.ZipFile(project_zip_path, 'r') as zip_ref:
                members = zip_ref.infolist()
                total_members = len(members)
                for index, member in enumerate(members, start=1):
                    zip_ref.extract(member, metaX_update_path)
                    if index == total_members or index % 50 == 0:
                        self.append_update_log(f"Extracted {index}/{total_members} files.")
                
            # Optionally, delete the project zip file after extraction
            os.remove(project_zip_path)
            self.append_update_log("Download and extraction completed.")
            
            
            return True

        except urllib.error.HTTPError as e:
            self.append_update_log(f"URL Error during download: {e.reason}")
            return False
        except socket.timeout:
            self.append_update_log("Download timed out")
            return False
        except Exception as e:
            self.append_update_log(f"Download project zip failed: {e}")
            return False

    def install_project_dependencies(self):
        project_folder_path = self.get_downloaded_project_folder_path()
        if not os.path.isdir(project_folder_path):
            return False, f"Downloaded project folder does not exist: {project_folder_path}"

        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--no-warn-script-location",
            project_folder_path,
        ]
        self.append_update_log(f"Installing MetaX dependencies with command: {' '.join(command)}")
        output_lines = []
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except Exception as e:
            return False, str(e)

        if process.stdout is not None:
            for line in process.stdout:
                clean_line = line.rstrip()
                output_lines.append(clean_line)
                if clean_line:
                    self.append_update_log(clean_line)

        return_code = process.wait()
        output = "\n".join(output_lines)
        if return_code != 0:
            self.append_update_log(f"Install MetaX dependencies failed with exit code {return_code}.")
            return False, output

        self.append_update_log("Install MetaX dependencies succeeded.")
        self.dependencies_updated = True
        return True, output

    def get_project_dependency_requirements(self, project_folder_path=None):
        if project_folder_path is None:
            project_folder_path = self.get_downloaded_project_folder_path()

        pyproject_path = os.path.join(project_folder_path, "pyproject.toml")
        if os.path.isfile(pyproject_path):
            try:
                with open(pyproject_path, "rb") as file:
                    pyproject_data = tomllib.load(file)
                dependencies = pyproject_data.get("project", {}).get("dependencies", [])
                if dependencies:
                    return list(dependencies)
            except Exception as e:
                self.append_update_log(f"Read dependency metadata from pyproject.toml failed: {e}")

        requirements_path = os.path.join(project_folder_path, "requirements.txt")
        if os.path.isfile(requirements_path):
            requirements = []
            with open(requirements_path, "r", encoding="utf-8") as file:
                for line in file:
                    requirement = line.strip()
                    if not requirement or requirement.startswith("#"):
                        continue
                    if " #" in requirement:
                        requirement = requirement.split(" #", 1)[0].strip()
                    if requirement.startswith(("-r", "--requirement", "-c", "--constraint")):
                        self.append_update_log(f"Skipping nested requirement directive: {requirement}")
                        continue
                    requirements.append(requirement)
            return requirements

        return []

    def find_unsatisfied_project_dependencies(self, project_folder_path=None):
        requirements = self.get_project_dependency_requirements(project_folder_path)
        issues = []
        skipped = []
        checked_count = 0
        environment = default_environment()

        for requirement_text in requirements:
            try:
                requirement = Requirement(requirement_text)
            except InvalidRequirement as e:
                skipped.append(f"{requirement_text}: {e}")
                continue

            if requirement.marker and not requirement.marker.evaluate(environment):
                continue

            checked_count += 1
            try:
                installed_version = importlib_metadata.version(requirement.name)
            except importlib_metadata.PackageNotFoundError:
                requirement_label = str(requirement.specifier) or "installed"
                issues.append(f"{requirement.name}: not installed; requires {requirement_label}")
                continue

            if requirement.specifier and not requirement.specifier.contains(installed_version, prereleases=True):
                issues.append(f"{requirement.name}: installed {installed_version}; requires {requirement.specifier}")

        return issues, skipped, checked_count

    def check_project_dependencies(self, project_folder_path=None):
        issues, skipped, checked_count = self.find_unsatisfied_project_dependencies(project_folder_path)
        if checked_count == 0:
            self.append_update_log("No dependency requirements were found in the downloaded project.")
        else:
            self.append_update_log(f"Checked {checked_count} dependency requirement(s) in the current Python environment.")

        for skipped_requirement in skipped:
            self.append_update_log(f"Skipped dependency requirement: {skipped_requirement}")

        if issues:
            output = "\n".join(issues)
            self.append_update_log("Current Python environment does not satisfy the downloaded dependency requirements:")
            for issue in issues:
                self.append_update_log(f"  - {issue}")
            return False, output

        self.append_update_log("Current Python environment satisfies the downloaded dependency requirements.")
        return True, ""

            
        
    def replace_metax_dir(self):
        # MetaX folder path is this file's parent and the parent's parent
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        metax_folder_path = os.path.dirname(current_script_path)
        metax_folder_path = os.path.dirname(metax_folder_path)
        self.append_update_log(f"Replacing MetaX files in: {metax_folder_path}")
        
        project_folder_path = self.get_downloaded_project_folder_path()
        if not os.path.exists(project_folder_path):
            self.append_update_log(f"Error: Downloaded project folder not found at {project_folder_path}")
            return False

        replaced_count = 0
        try:
            for item in os.listdir(project_folder_path):
                source_item = os.path.join(project_folder_path, item)
                target_item = os.path.join(metax_folder_path, item)
                
                # Exclude .git and other repo-specific files that don't need to be in the local installation
                if item in ['.git', '.github', '.gitignore']:
                    continue

                if os.path.isdir(source_item):
                    if os.path.exists(target_item):
                        shutil.rmtree(target_item, ignore_errors=True)
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                    replaced_count += 1
                else:
                    if os.path.exists(target_item):
                        try:
                            os.remove(target_item)
                        except Exception:
                            pass
                    shutil.copy2(source_item, target_item)
                    replaced_count += 1

            self.append_update_log(f"Updated {replaced_count} files/directories in the MetaX installation.")
            return True

        except Exception as e:
            self.append_update_log(f"An error occurred while replacing files: {e}")
            import traceback
            self.append_update_log(traceback.format_exc())
            return False
            


    def update_metax(self):
        # ask if user wants to update
        try:
            change_log_str = self.get_str()
        except Exception as e:
            print(f"Read change log failed: {e}")
            change_log_str = "No change log."

        api_changed = str(self.current_api) != str(self.remote_api)
        dependency_notice = (
            "\n\nMetaX will check the downloaded version's Python dependency requirements "
            "against the current Python environment."
            "\nIf the API changes or installed packages are missing/outdated, MetaX will run pip "
            "before replacing the local code:"
            f"\n{sys.executable} -m pip install --upgrade --no-warn-script-location "
            "<downloaded MetaX source>"
        )

        reply = self.display_message_in_text_browser("Update", f"MetaX new version is available. Do you want to update?\
                                    {dependency_notice}\
                                    \n\nCurrent version: {self.current_version}\nRemote version: {self.remote_version}\
                                    \nCurrent API: {self.current_api}\nRemote API: {self.remote_api}\n\nChange log:\n{change_log_str}",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.metaXGUI.show_message("Updating MetaX...", "Updating...")
            self.show_update_log_dialog()
            self.append_update_log(f"Starting MetaX update: {self.current_version} -> {self.remote_version}")
            self.append_update_log(f"Current API: {self.current_api}; remote API: {self.remote_api}")
            # set update_required flag to True
            # this flag will stop MainWindow.show()
            self.metaXGUI.update_required = True

            try:
                download_success = self.download_project_zip_and_unzip()
                if not download_success:
                    self.clear_update_required_flag()
                    self.finish_update_log_dialog()
                    QMessageBox.warning(self.MainWindow, "Update", "Download failed. Please try again later or update manually.")
                    return

                dependency_check_success, dependency_check_output = self.check_project_dependencies()
                should_install_dependencies = api_changed or not dependency_check_success
                if should_install_dependencies:
                    self.metaXGUI.show_message("Installing MetaX dependencies...", "Updating...")
                    dependency_success, dependency_output = self.install_project_dependencies()
                    if not dependency_success:
                        dependency_output = dependency_output.strip()
                        if len(dependency_output) > 3000:
                            dependency_output = dependency_output[-3000:]
                        QMessageBox.warning(
                            self.MainWindow,
                            "Update",
                            "MetaX downloaded the new version, but dependency installation failed. "
                            "The local MetaX code was not replaced.\n\n"
                            f"Command:\n{sys.executable} -m pip install --upgrade --no-warn-script-location "
                            f"{self.get_downloaded_project_folder_path()}\n\n"
                            f"Output:\n{dependency_output}"
                        )
                        self.clear_update_required_flag()
                        self.finish_update_log_dialog()
                        return
                    dependency_check_success, dependency_check_output = self.check_project_dependencies()
                    if not dependency_check_success:
                        dependency_check_output = dependency_check_output.strip()
                        if len(dependency_check_output) > 3000:
                            dependency_check_output = dependency_check_output[-3000:]
                        QMessageBox.warning(
                            self.MainWindow,
                            "Update",
                            "MetaX installed dependencies, but the current Python environment still does not "
                            "satisfy the downloaded version's requirements. The local MetaX code was not replaced.\n\n"
                            f"Unsatisfied requirements:\n{dependency_check_output}"
                        )
                        self.clear_update_required_flag()
                        self.finish_update_log_dialog()
                        return

                # replace the old MetaX folder with the new one
                replace_success = self.replace_metax_dir()
                if not replace_success:
                    self.clear_update_required_flag()
                    self.finish_update_log_dialog()
                    QMessageBox.warning(self.MainWindow, "Update", "An error occurred while replacing the MetaX directory. Please try again later or update manually.")
                    return

                # check if the update is successful
                if self.check_update_status():
                    msg = f"MetaX has been updated to {self.remote_version}. Please restart MetaX."
                    if self.dependencies_updated:
                        msg = f"MetaX has been updated to {self.remote_version}, and dependencies were updated. Please restart MetaX."
                    self.append_update_log(msg)
                else:
                    msg = f"Warning: MetaX update failed. Still in version {self.current_version}. Please try again later or update manually."
                    self.append_update_log(msg)

                self.finish_update_log_dialog()
                QMessageBox.information(self.MainWindow, "Update", msg)
                # force close MetaX without triggering closeEvent
                QtWidgets.QApplication.quit()
                # close the QSplashScreen
                self.splash.finish(self.MainWindow)
                sys.exit()

            except Exception as e:
                self.clear_update_required_flag()
                self.append_update_log(f"Update failed: {e}")
                self.finish_update_log_dialog()
                QMessageBox.warning(self.MainWindow, "Update", f'Update failed: {e}')

    def display_message_in_text_browser(self, title, message, buttons=QMessageBox.NoButton, default_button=QMessageBox.NoButton):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(title)
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # set icon as parent's icon
        dialog.setWindowIcon(self.MainWindow.windowIcon())

        text_browser = QtWidgets.QTextBrowser()
        text_browser.setText(message)
        layout.addWidget(text_browser)

        # create button box
        button_box = QtWidgets.QDialogButtonBox()
        # create yes and no buttons
        if buttons & QMessageBox.Yes:
            yes_button = button_box.addButton(QtWidgets.QDialogButtonBox.Yes)
            if default_button == QMessageBox.Yes:
                yes_button.setDefault(True)
        if buttons & QMessageBox.No:
            no_button = button_box.addButton(QtWidgets.QDialogButtonBox.No)
            if default_button == QMessageBox.No:
                no_button.setDefault(True)
        layout.addWidget(button_box)

        # connect signals
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.resize(500, 400) 

        # show dialog and wait for user response
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return QMessageBox.Yes
        else:
            return QMessageBox.No

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
                    print(f"New version is available: {self.current_version} -> {self.remote_version}")
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
class MockMainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.update_required = False
        self._icon = QIcon()

    def windowIcon(self):
        return self._icon

    def show_message(self, title, message):
        print(f"{title}: {message}")

class MockMetaXGUI:
    def __init__(self):
        self.MainWindow = MockMainWindow()
        self.update_required = False

    def show_message(self, title, message):
        print(f"{title}: {message}")

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        mock_gui = MockMetaXGUI()
        
        # Test updater with different scenarios
        print("\nTesting updater with dev branch:")
        test_version = '1.124.0' 
        print(f"Testing with version: {test_version}")
        updater = Updater(mock_gui, test_version, None, show_message=True, branch='dev', is_test_mode=True)
        updater.check_update(show_message=True)
        
        # print("\nTesting updater with main branch:")
        # updater = Updater(mock_gui, test_version, None, show_message=True, branch='main', is_test_mode=True)
        # updater.check_update(show_message=True)

        app.processEvents()
        app.quit()

    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)
    finally:
        # 强制退出程序
        os._exit(0)
