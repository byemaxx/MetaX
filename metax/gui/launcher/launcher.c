#include <windows.h>
#include <stdio.h>

int main() {
    char scriptPath[MAX_PATH];
    char pythonPath[MAX_PATH];

    // get script path
    GetModuleFileName(NULL, scriptPath, MAX_PATH);
    *strrchr(scriptPath, '\\') = '\0';

    // get python path
    snprintf(pythonPath, MAX_PATH, "%s\\pyenv\\python.exe", scriptPath);
    snprintf(scriptPath, MAX_PATH, "%s\\metax\\metax\\gui\\main_gui.py", scriptPath);

    // run python script
    ShellExecute(NULL, "open", pythonPath, scriptPath, NULL, SW_SHOW);

    return 0;
}
