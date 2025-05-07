#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

// Function to find Python console window
BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam) {
    DWORD processId;
    GetWindowThreadProcessId(hwnd, &processId);
    
    if (processId == *((DWORD*)lParam)) {
        char className[256];
        GetClassName(hwnd, className, 256);
        
        // Check if this is a console window
        if (strcmp(className, "ConsoleWindowClass") == 0) {
            *((HWND*)lParam) = hwnd;  // Store the found window handle
            return FALSE;  // Stop enumeration
        }
    }
    return TRUE;  // Continue enumeration
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    char basePath[MAX_PATH];
    char pythonPath[MAX_PATH];
    char metaxPath[MAX_PATH];
    char cmdExePath[MAX_PATH];
    char commandLine[MAX_PATH*4]; // Increased size for longer command
    
    // Get base path
    GetModuleFileName(NULL, basePath, MAX_PATH);
    *strrchr(basePath, '\\') = '\0';
    
    // Use python.exe
    snprintf(pythonPath, MAX_PATH, "%s\\pyenv\\python.exe", basePath);
    snprintf(metaxPath, MAX_PATH, "%s\\metax", basePath);
    
    // Get system directory for cmd.exe
    GetSystemDirectory(cmdExePath, MAX_PATH);
    snprintf(cmdExePath, MAX_PATH, "%s\\cmd.exe", cmdExePath);
    
    // Create command line to use cmd.exe to start python with -m parameter
    // /C means execute command and terminate
    // /S allows string with quotes after /C
    // We use start /B to run without creating a new window
    snprintf(commandLine, MAX_PATH*4, 
             "\"%s\" /S /C \"set PYTHONPATH=%s && start /B \"\" \"%s\" -m metax.gui.main_gui\"", 
             cmdExePath, metaxPath, pythonPath);
    
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE; // Hide cmd.exe window
    
    // Create cmd process which will start Python
    if (CreateProcess(NULL, commandLine, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        // Don't need to wait for cmd.exe - it will exit after starting python
        // Close process handles
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        
        // We don't need to hide Python's window because start /B runs it without a window
    }
    else {
        // Try direct launch as fallback
        snprintf(commandLine, MAX_PATH*3, 
                "set PYTHONPATH=%s && \"%s\" -m metax.gui.main_gui", 
                metaxPath, pythonPath);
        
        ZeroMemory(&si, sizeof(si));
        si.cb = sizeof(si);
        
        // Try with CREATE_NO_WINDOW flag
        if (CreateProcess(NULL, commandLine, NULL, NULL, FALSE, 
                         CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
        }
        else {
            // Last resort: Call Python directly with specific working directory
            char envPath[MAX_PATH*2];
            snprintf(envPath, MAX_PATH*2, "PYTHONPATH=%s", metaxPath);
            ShellExecute(NULL, "open", pythonPath, "-m metax.gui.main_gui", basePath, SW_SHOW);
        }
    }
    
    return 0;
}
