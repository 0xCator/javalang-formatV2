import os
import shutil
import tempfile


class FileHandler:
    """
    A file handler with fault tolerance capabilities.
    If any operation fails, the file will be restored to its original state.
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.backup_path = None
    
    def read(self):
        try:
            if not os.path.exists(self.file_path):
                return None
                
            with open(self.file_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None
    
    def _create_backup(self):
        """Create a backup of the original file if it exists."""
        if os.path.exists(self.file_path):
            # Create a temporary backup file
            fd, self.backup_path = tempfile.mkstemp(prefix="backup_")
            os.close(fd)
            shutil.copy2(self.file_path, self.backup_path)
    
    def _restore_from_backup(self):
        """Restore the file from backup if a backup exists."""
        if self.backup_path and os.path.exists(self.backup_path):
            try:
                shutil.copy2(self.backup_path, self.file_path)
            except Exception as e:
                print(f"Error restoring backup: {str(e)}")
            finally:
                # Clean up the backup file
                self._cleanup_backup()
    
    def _cleanup_backup(self):
        """Clean up the backup file if it exists."""
        if self.backup_path and os.path.exists(self.backup_path):
            try:
                os.remove(self.backup_path)
            except Exception as e:
                print(f"Warning: Couldn't remove backup file {self.backup_path}: {str(e)}")
            self.backup_path = None
    
    def write(self, content):
        # Create a backup first
        self._create_backup()
        
        try:
            # Write to a temporary file first
            fd, temp_path = tempfile.mkstemp(prefix="writing_")
            os.close(fd)
            
            with open(temp_path, 'w') as temp_file:
                temp_file.write(content)
            
            # Replace the original file with the temporary file
            shutil.move(temp_path, self.file_path)
            
            # Clean up the backup since operation was successful
            self._cleanup_backup()
            return True
            
        except Exception as e:
            print(f"Error writing to file: {str(e)}")
            # Restore from backup
            self._restore_from_backup()
            return False
    
    def append(self, content):
        current_content = self.read() or ""
        return self.write(current_content + content)
    
