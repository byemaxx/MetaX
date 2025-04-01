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
    char scriptPath[MAX_PATH];
    char commandLine[MAX_PATH*2];
    
    // Get base path
    GetModuleFileName(NULL, basePath, MAX_PATH);
    *strrchr(basePath, '\\') = '\0';
    
    // Use python.exe
    snprintf(pythonPath, MAX_PATH, "%s\\pyenv\\python.exe", basePath);
    snprintf(scriptPath, MAX_PATH, "%s\\metax\\metax\\gui\\main_gui.py", basePath);
    
    snprintf(commandLine, MAX_PATH*2, "\"%s\" \"%s\"", pythonPath, scriptPath);
    
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    
    // Create Python process
    if (CreateProcess(NULL, commandLine, NULL, NULL, FALSE, CREATE_NEW_CONSOLE, NULL, NULL, &si, &pi)) {
        DWORD procId = pi.dwProcessId;
        HWND consoleWindow = NULL;
        BOOL windowFound = FALSE;
        
        // Use a smarter waiting strategy
        const int MAX_WAIT_TIME = 5000;  // Wait up to 5 seconds
        const int CHECK_INTERVAL = 50;   // Check every 50ms
        int totalWaitTime = 0;
        
        while (totalWaitTime < MAX_WAIT_TIME) {
            // Try to find the console window
            DWORD tempProcId = procId;
            EnumWindows(EnumWindowsProc, (LPARAM)&tempProcId);
            
            // If window found
            if (tempProcId != procId) {
                consoleWindow = (HWND)tempProcId;
                
                // Additional verification to ensure we have the right window
                DWORD verifyProcessId = 0;
                GetWindowThreadProcessId(consoleWindow, &verifyProcessId);
                
                if (verifyProcessId == procId) {
                    windowFound = TRUE;
                    
                    // Hide the found window
                    ShowWindow(consoleWindow, SW_HIDE);
                    break;
                }
            }
            
            // Brief sleep then retry
            Sleep(CHECK_INTERVAL);
            totalWaitTime += CHECK_INTERVAL;
            
            // Check if Python process is still running
            DWORD exitCode;
            if (GetExitCodeProcess(pi.hProcess, &exitCode) && exitCode != STILL_ACTIVE) {
                // Python process has ended, exit the loop
                break;
            }
        }
        
        // If window not found but process is still running
        if (!windowFound) {
            // Can add logging or other handling logic
            // But don't block program from continuing
        }
        
        // Don't close process handle, let Python process continue running
        CloseHandle(pi.hThread);
    }
    else {
        // If process creation failed, try ShellExecute
        ShellExecute(NULL, "open", pythonPath, scriptPath, NULL, SW_SHOW);
    }
    
    return 0;
}
