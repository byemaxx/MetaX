# Description: Parse the changelog.md file and return the changes between two versions
# changelog format:
# # Version: 1.88.6
# ## Date: 2024-01-15
# ### Changes:
# - Fixed: the QSplashScreen doesn't colse after update.
# - Add: Add changelog display. when new version avaliable.

class ChangelogParser:
    def __init__(self, file_path):
        self.current_version = None
        self.current_changes = []
        self.changelog_dict = self.parse_changelog_md(file_path)

    def parse_changelog_md(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        self.changelog_dict = {}
        for line in lines:
            line = line.strip()
            if line.startswith('# Version:'):
                if self.current_version:
                    self.changelog_dict[self.current_version] = self.current_changes
                self.current_version = line.split(":")[1].strip()
                self.current_changes = []
            elif line.startswith('-'):
                self.current_changes.append(line[1:].strip())

        if self.current_version:
            self.changelog_dict[self.current_version] = self.current_changes
        return self.changelog_dict

    @staticmethod
    def compare_version(version1, version2):
        return tuple(map(int, version1.split("."))) > tuple(map(int, version2.split(".")))

    def get_updates_between_versions(self, old_version, new_version):
        updates = [(version, changes) for version, changes in self.changelog_dict.items()
                   if self.compare_version(version, old_version) and not self.compare_version(version, new_version)]
        return updates

    def get_str(self, old_version):
        new_version = sorted(self.changelog_dict.keys(), key=lambda v: list(map(int, v.split('.'))))[-1]
        updates = self.get_updates_between_versions(old_version, new_version)
        result = "\n".join(f"Version {version}:\n" + "\n".join(f"  - {change}" for change in changes) for version, changes in updates)
        return result

if __name__ == '__main__':
    log_path = "..//MetaX/ChangeLog.md"
    changelog_parser = ChangelogParser(log_path)
    print(changelog_parser.get_str("1.88.5"))
