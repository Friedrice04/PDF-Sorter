"""
Single File Installer for OCR File Sorter
This creates a self-contained installer that includes:
1. The OCR File Sorter executable
2. Tesseract OCR installation
3. Automatic setup and configuration
"""

import os
import sys
import subprocess
import tempfile
import zipfile
import shutil
import urllib.request
import json
from pathlib import Path
import winreg
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time

class OCRFileSorterInstaller:
    """Main installer class for OCR File Sorter and dependencies."""
    
    def __init__(self):
        self.install_dir = Path.home() / "OCR File Sorter"
        self.tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
        self.tesseract_installer = None
        self.progress_var = None
        self.status_var = None
        self.root = None
        
    def create_gui(self):
        """Create the installer GUI."""
        self.root = tk.Tk()
        self.root.title("OCR File Sorter Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="OCR File Sorter Installer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Description
        desc_text = """This installer will set up OCR File Sorter and all required dependencies:

• OCR File Sorter application
• Tesseract OCR engine for document processing
• Desktop shortcuts and file associations
• Automatic PATH configuration

Installation Directory:"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Install directory
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.dir_var = tk.StringVar(value=str(self.install_dir))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=50)
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.grid(row=0, column=1, padx=(10, 0))
        
        dir_frame.columnconfigure(0, weight=1)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        desktop_cb = ttk.Checkbutton(options_frame, text="Create desktop shortcut", 
                                   variable=self.desktop_shortcut_var)
        desktop_cb.grid(row=0, column=0, sticky=tk.W)
        
        self.start_menu_var = tk.BooleanVar(value=True)
        start_cb = ttk.Checkbutton(options_frame, text="Add to Start Menu", 
                                 variable=self.start_menu_var)
        start_cb.grid(row=1, column=0, sticky=tk.W)
        
        self.install_tesseract_var = tk.BooleanVar(value=True)
        tesseract_cb = ttk.Checkbutton(options_frame, text="Install Tesseract OCR (required for scanned PDFs)", 
                                     variable=self.install_tesseract_var)
        tesseract_cb.grid(row=2, column=0, sticky=tk.W)
        
        # Progress
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                     maximum=100, length=400)
        progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="Ready to install")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.install_btn = ttk.Button(button_frame, text="Install", command=self.start_installation)
        self.install_btn.grid(row=0, column=0, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.quit)
        cancel_btn.grid(row=0, column=1)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def browse_directory(self):
        """Browse for installation directory."""
        from tkinter import filedialog
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)
            self.install_dir = Path(directory)
    
    def update_progress(self, value, status):
        """Update progress bar and status."""
        self.progress_var.set(value)
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def download_file(self, url, destination, description="file"):
        """Download a file with progress tracking."""
        try:
            self.update_progress(0, f"Downloading {description}...")
            
            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) / total_size)
                    self.update_progress(percent * 0.3, f"Downloading {description}... {percent:.1f}%")
            
            urllib.request.urlretrieve(url, destination, reporthook=report_progress)
            return True
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download {description}:\n{str(e)}")
            return False
    
    def install_tesseract(self):
        """Download and install Tesseract OCR."""
        if not self.install_tesseract_var.get():
            return True
        
        # Check if Tesseract is already installed
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.update_progress(40, "Tesseract OCR already installed")
                return True
        except FileNotFoundError:
            pass
        
        # Download Tesseract installer
        temp_dir = Path(tempfile.gettempdir())
        tesseract_installer = temp_dir / "tesseract_installer.exe"
        
        if not self.download_file(self.tesseract_url, tesseract_installer, "Tesseract OCR"):
            return False
        
        try:
            # Run Tesseract installer silently
            self.update_progress(35, "Installing Tesseract OCR...")
            
            # Try silent install first
            result = subprocess.run([
                str(tesseract_installer), 
                '/VERYSILENT', 
                '/NORESTART',
                '/DIR=C:\\Program Files\\Tesseract-OCR'
            ], capture_output=True)
            
            if result.returncode != 0:
                # If silent install fails, try interactive
                self.update_progress(35, "Running Tesseract installer (follow prompts)...")
                result = subprocess.run([str(tesseract_installer)], capture_output=True)
            
            # Add Tesseract to PATH
            tesseract_path = Path("C:/Program Files/Tesseract-OCR")
            if tesseract_path.exists():
                self.add_to_path(str(tesseract_path))
            
            self.update_progress(40, "Tesseract OCR installation completed")
            return True
            
        except Exception as e:
            messagebox.showerror("Installation Error", 
                               f"Failed to install Tesseract OCR:\n{str(e)}")
            return False
        finally:
            # Clean up installer
            try:
                tesseract_installer.unlink()
            except:
                pass
    
    def add_to_path(self, directory):
        """Add directory to system PATH."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                              0, winreg.KEY_ALL_ACCESS) as key:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
                if directory not in current_path:
                    new_path = current_path + ";" + directory
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        except Exception:
            # If we can't modify system PATH, try user PATH
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment",
                                  0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "PATH")
                    except FileNotFoundError:
                        current_path = ""
                    
                    if directory not in current_path:
                        new_path = current_path + ";" + directory if current_path else directory
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            except Exception:
                pass  # PATH modification failed, but not critical
    
    def extract_application(self):
        """Extract the OCR File Sorter application."""
        try:
            self.update_progress(50, "Creating installation directory...")
            
            # Create installation directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the embedded application data
            app_data = self.get_embedded_app_data()
            if not app_data:
                raise Exception("Application data not found in installer")
            
            self.update_progress(60, "Extracting application files...")
            
            # Extract application files
            app_exe_path = self.install_dir / "OCR File Sorter.exe"
            with open(app_exe_path, 'wb') as f:
                f.write(app_data)
            
            # Make executable
            os.chmod(app_exe_path, 0o755)
            
            self.update_progress(70, "Application extracted successfully")
            return True
            
        except Exception as e:
            messagebox.showerror("Installation Error", 
                               f"Failed to extract application:\n{str(e)}")
            return False
    
    def create_shortcuts(self):
        """Create desktop and start menu shortcuts."""
        try:
            app_exe = self.install_dir / "OCR File Sorter.exe"
            
            if self.desktop_shortcut_var.get():
                self.update_progress(80, "Creating desktop shortcut...")
                desktop = Path.home() / "Desktop"
                shortcut_path = desktop / "OCR File Sorter.lnk"
                self.create_shortcut(str(app_exe), str(shortcut_path))
            
            if self.start_menu_var.get():
                self.update_progress(85, "Adding to Start Menu...")
                start_menu = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
                start_menu.mkdir(parents=True, exist_ok=True)
                shortcut_path = start_menu / "OCR File Sorter.lnk"
                self.create_shortcut(str(app_exe), str(shortcut_path))
            
            self.update_progress(90, "Shortcuts created successfully")
            return True
            
        except Exception as e:
            messagebox.showerror("Shortcut Error", 
                               f"Failed to create shortcuts:\n{str(e)}")
            return False
    
    def create_shortcut(self, target, shortcut_path):
        """Create a Windows shortcut."""
        try:
            # Try using win32com first
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = str(Path(target).parent)
                shortcut.IconLocation = target
                shortcut.save()
                return
            except ImportError:
                pass
            
            # Fallback: Create a batch file
            batch_path = Path(shortcut_path).with_suffix('.bat')
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{Path(target).parent}"\n')
                f.write(f'start "" "{target}"\n')
                
        except Exception as e:
            # If all else fails, create a simple launcher script
            try:
                script_path = Path(shortcut_path).with_suffix('.py')
                with open(script_path, 'w') as f:
                    f.write(f'import subprocess\n')
                    f.write(f'import os\n')
                    f.write(f'os.chdir(r"{Path(target).parent}")\n')
                    f.write(f'subprocess.run([r"{target}"])\n')
            except:
                pass  # Give up on shortcuts if nothing works
    
    def get_embedded_app_data(self):
        """Get embedded application data."""
        # This would be replaced with actual embedded data
        # For now, return None to indicate no embedded data
        return None
    
    def create_uninstaller(self):
        """Create an uninstaller."""
        try:
            uninstaller_content = f'''
import os
import shutil
import sys
from pathlib import Path
import winreg

def remove_from_path(directory):
    """Remove directory from PATH."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment",
                          0, winreg.KEY_ALL_ACCESS) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
                paths = current_path.split(";")
                paths = [p for p in paths if p != directory]
                new_path = ";".join(paths)
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            except FileNotFoundError:
                pass
    except Exception:
        pass

def main():
    install_dir = Path("{self.install_dir}")
    
    # Remove shortcuts
    desktop = Path.home() / "Desktop" / "OCR File Sorter.lnk"
    if desktop.exists():
        desktop.unlink()
    
    start_menu = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/OCR File Sorter.lnk"
    if start_menu.exists():
        start_menu.unlink()
    
    # Remove from PATH
    remove_from_path(str(install_dir))
    
    # Remove installation directory
    if install_dir.exists():
        shutil.rmtree(install_dir)
    
    print("OCR File Sorter has been uninstalled.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
            
            uninstaller_path = self.install_dir / "uninstall.py"
            with open(uninstaller_path, 'w') as f:
                f.write(uninstaller_content)
            
            return True
        except Exception:
            return False
    
    def start_installation(self):
        """Start the installation process."""
        self.install_btn.config(state='disabled')
        self.install_dir = Path(self.dir_var.get())
        
        def install():
            try:
                # Install Tesseract
                if not self.install_tesseract():
                    return
                
                # Extract application
                if not self.extract_application():
                    return
                
                # Create shortcuts
                if not self.create_shortcuts():
                    return
                
                # Create uninstaller
                self.create_uninstaller()
                
                # Add to PATH
                self.add_to_path(str(self.install_dir))
                
                self.update_progress(100, "Installation completed successfully!")
                
                messagebox.showinfo("Installation Complete", 
                                  f"OCR File Sorter has been installed successfully!\n\n"
                                  f"Installation directory: {self.install_dir}\n\n"
                                  f"You can now start using OCR File Sorter from the desktop shortcut "
                                  f"or Start Menu.")
                
                self.root.quit()
                
            except Exception as e:
                messagebox.showerror("Installation Failed", 
                                   f"Installation failed:\n{str(e)}")
            finally:
                self.install_btn.config(state='normal')
        
        # Run installation in separate thread
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
    
    def run(self):
        """Run the installer."""
        self.create_gui()
        self.root.mainloop()


def main():
    """Main entry point."""
    # Check if running as admin (recommended for Tesseract installation)
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            messagebox.showwarning("Administrator Rights", 
                                 "For best results, run this installer as Administrator.\n"
                                 "This ensures Tesseract OCR can be installed system-wide.")
    except:
        pass
    
    installer = OCRFileSorterInstaller()
    installer.run()


if __name__ == "__main__":
    main()
