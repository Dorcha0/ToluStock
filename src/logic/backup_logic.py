"""
Backup and restore logic for ToluStock.
Handles database backup, restore, and data export/import operations.
"""

import os
import shutil
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .db import db
from .user import user_manager
from .utils import export_to_json, import_from_json, sanitize_filename, format_file_size


class BackupManager:
    """Manages backup and restore operations."""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """Ensure backup directory exists."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_database_backup(self, backup_name: str = None) -> Optional[str]:
        """Create a full database backup."""
        try:
            if not user_manager.has_permission('backup_data'):
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not backup_name:
                backup_name = f"tolustock_backup_{timestamp}"
            
            backup_name = sanitize_filename(backup_name)
            backup_file = os.path.join(self.backup_dir, f"{backup_name}.db")
            
            # Create database backup
            if db.backup_database(backup_file):
                # Create metadata file
                metadata = {
                    'backup_name': backup_name,
                    'backup_date': datetime.now().isoformat(),
                    'backup_type': 'database',
                    'created_by': user_manager.get_current_user().get('username', 'Unknown'),
                    'file_size': os.path.getsize(backup_file),
                    'database_version': '1.0'
                }
                
                metadata_file = os.path.join(self.backup_dir, f"{backup_name}.json")
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return backup_file
            
            return None
        except Exception as e:
            print(f"Database backup error: {e}")
            return None
    
    def restore_database_backup(self, backup_file: str) -> bool:
        """Restore database from backup file."""
        try:
            if not user_manager.is_admin():
                return False
            
            if not os.path.exists(backup_file):
                return False
            
            # Create a backup of current database before restore
            current_backup = self.create_database_backup("pre_restore_backup")
            if not current_backup:
                return False
            
            # Restore from backup
            success = db.restore_database(backup_file)
            
            if success:
                # Log the restore operation
                self.log_operation("restore", backup_file, True)
            
            return success
        except Exception as e:
            print(f"Database restore error: {e}")
            return False
    
    def create_data_export(self, export_name: str = None, 
                          include_tables: List[str] = None) -> Optional[str]:
        """Create a JSON export of selected data."""
        try:
            if not user_manager.has_permission('export_data'):
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not export_name:
                export_name = f"tolustock_export_{timestamp}"
            
            export_name = sanitize_filename(export_name)
            
            # Default tables to export
            if not include_tables:
                include_tables = ['products', 'categories', 'customers', 'suppliers', 'users']
            
            export_data = {
                'export_info': {
                    'export_name': export_name,
                    'export_date': datetime.now().isoformat(),
                    'created_by': user_manager.get_current_user().get('username', 'Unknown'),
                    'tables_included': include_tables,
                    'version': '1.0'
                }
            }
            
            # Export each table
            for table in include_tables:
                try:
                    if table == 'users':
                        # Don't export passwords
                        data = db.execute_query(
                            "SELECT id, username, role, email, created_at, last_login FROM users"
                        )
                    else:
                        data = db.execute_query(f"SELECT * FROM {table}")
                    
                    export_data[table] = data
                except Exception as e:
                    print(f"Error exporting table {table}: {e}")
                    export_data[table] = []
            
            # Save export file
            export_file = os.path.join(self.backup_dir, f"{export_name}.json")
            if export_to_json(export_data, export_file):
                return export_file
            
            return None
        except Exception as e:
            print(f"Data export error: {e}")
            return None
    
    def import_data_export(self, export_file: str, 
                          overwrite_existing: bool = False) -> Dict[str, Any]:
        """Import data from JSON export file."""
        try:
            if not user_manager.is_admin():
                return {'success': False, 'message': 'Admin access required'}
            
            if not os.path.exists(export_file):
                return {'success': False, 'message': 'Export file not found'}
            
            # Load export data
            export_data = import_from_json(export_file)
            if not export_data:
                return {'success': False, 'message': 'Failed to read export file'}
            
            imported_tables = []
            errors = []
            
            # Import each table
            for table_name, table_data in export_data.items():
                if table_name == 'export_info':
                    continue
                
                try:
                    if table_name == 'users' and not overwrite_existing:
                        # Skip users table unless explicitly overwriting
                        continue
                    
                    # Clear table if overwriting
                    if overwrite_existing:
                        db.execute_update(f"DELETE FROM {table_name}")
                    
                    # Insert data
                    imported_count = 0
                    for row in table_data:
                        try:
                            # Construct INSERT query
                            columns = list(row.keys())
                            placeholders = ', '.join(['?' for _ in columns])
                            values = [row[col] for col in columns]
                            
                            query = f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                            rows_affected = db.execute_update(query, tuple(values))
                            if rows_affected > 0:
                                imported_count += 1
                        except Exception as e:
                            errors.append(f"Error importing row in {table_name}: {str(e)}")
                    
                    imported_tables.append({
                        'table': table_name,
                        'imported': imported_count,
                        'total': len(table_data)
                    })
                
                except Exception as e:
                    errors.append(f"Error importing table {table_name}: {str(e)}")
            
            return {
                'success': True,
                'imported_tables': imported_tables,
                'errors': errors
            }
        except Exception as e:
            print(f"Data import error: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Get list of available backups."""
        try:
            backups = []
            
            if not os.path.exists(self.backup_dir):
                return backups
            
            # Get all backup files
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.db') or filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    
                    # Get file info
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    backup_type = 'database' if filename.endswith('.db') else 'export'
                    
                    # Try to get metadata if available
                    metadata_file = os.path.join(
                        self.backup_dir, 
                        filename.replace('.db', '.json').replace('.json', '.json')
                    )
                    
                    metadata = {}
                    if os.path.exists(metadata_file) and filename.endswith('.db'):
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    backups.append({
                        'filename': filename,
                        'file_path': file_path,
                        'backup_type': backup_type,
                        'file_size': file_size,
                        'file_size_formatted': format_file_size(file_size),
                        'modified_time': modified_time.isoformat(),
                        'metadata': metadata
                    })
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x['modified_time'], reverse=True)
            
            return backups
        except Exception as e:
            print(f"Get backup list error: {e}")
            return []
    
    def delete_backup(self, filename: str) -> bool:
        """Delete a backup file."""
        try:
            if not user_manager.is_admin():
                return False
            
            file_path = os.path.join(self.backup_dir, filename)
            
            if not os.path.exists(file_path):
                return False
            
            # Delete main file
            os.remove(file_path)
            
            # Delete metadata file if exists
            if filename.endswith('.db'):
                metadata_file = os.path.join(
                    self.backup_dir, 
                    filename.replace('.db', '.json')
                )
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)
            
            return True
        except Exception as e:
            print(f"Delete backup error: {e}")
            return False
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Clean up backups older than specified days."""
        try:
            if not user_manager.is_admin():
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            
            backups = self.get_backup_list()
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup['modified_time'])
                if backup_date < cutoff_date:
                    if self.delete_backup(backup['filename']):
                        deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"Cleanup backups error: {e}")
            return 0
    
    def schedule_automatic_backup(self, frequency: str = 'daily') -> bool:
        """Schedule automatic backups (placeholder for cron/scheduler integration)."""
        # This would integrate with a task scheduler in a full application
        return True
    
    def validate_backup_integrity(self, backup_file: str) -> Dict[str, Any]:
        """Validate backup file integrity."""
        try:
            if not os.path.exists(backup_file):
                return {'valid': False, 'error': 'File not found'}
            
            file_size = os.path.getsize(backup_file)
            if file_size == 0:
                return {'valid': False, 'error': 'Empty file'}
            
            if backup_file.endswith('.db'):
                # Try to open as SQLite database
                import sqlite3
                try:
                    conn = sqlite3.connect(backup_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    conn.close()
                    
                    return {
                        'valid': True,
                        'file_size': file_size,
                        'table_count': table_count
                    }
                except sqlite3.Error as e:
                    return {'valid': False, 'error': f'Database error: {str(e)}'}
            
            elif backup_file.endswith('.json'):
                # Try to parse as JSON
                try:
                    data = import_from_json(backup_file)
                    if data:
                        return {
                            'valid': True,
                            'file_size': file_size,
                            'tables': list(data.keys())
                        }
                    else:
                        return {'valid': False, 'error': 'Invalid JSON format'}
                except Exception as e:
                    return {'valid': False, 'error': f'JSON error: {str(e)}'}
            
            return {'valid': False, 'error': 'Unsupported file format'}
        except Exception as e:
            print(f"Backup validation error: {e}")
            return {'valid': False, 'error': str(e)}
    
    def log_operation(self, operation: str, filename: str, success: bool):
        """Log backup/restore operations."""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'filename': filename,
                'success': success,
                'user': user_manager.get_current_user().get('username', 'Unknown')
            }
            
            log_file = os.path.join(self.backup_dir, 'operations.log')
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Log operation error: {e}")


# Global backup manager instance
backup_manager = BackupManager()