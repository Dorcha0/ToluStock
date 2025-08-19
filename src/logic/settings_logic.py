"""
Settings management logic for ToluStock.
Handles application settings, preferences, and configuration.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .db import db
from .user import user_manager
from .utils import config


class SettingsManager:
    """Manages application settings and preferences."""
    
    def __init__(self):
        self.cache = {}
        self.load_settings()
    
    def load_settings(self):
        """Load settings from database into cache."""
        try:
            settings = db.execute_query("SELECT key, value FROM settings")
            self.cache = {setting['key']: setting['value'] for setting in settings}
            
            # Merge with default config
            for key, value in config.to_dict().items():
                if key not in self.cache:
                    self.cache[key] = str(value)
        except Exception as e:
            print(f"Load settings error: {e}")
            self.cache = config.to_dict()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        try:
            value = self.cache.get(key, default)
            
            # Try to convert to appropriate type
            if isinstance(default, bool):
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default, int):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, float):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            return value
        except Exception as e:
            print(f"Get setting error: {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value."""
        try:
            if not user_manager.has_permission('manage_settings'):
                return False
            
            # Convert value to string for storage
            str_value = str(value)
            
            # Update database
            rows_affected = db.execute_update(
                "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, str_value)
            )
            
            if rows_affected > 0:
                # Update cache
                self.cache[key] = str_value
                return True
            
            return False
        except Exception as e:
            print(f"Set setting error: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        return self.cache.copy()
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, bool]:
        """Update multiple settings."""
        results = {}
        
        for key, value in settings.items():
            results[key] = self.set_setting(key, value)
        
        return results
    
    def reset_setting(self, key: str) -> bool:
        """Reset a setting to its default value."""
        try:
            if not user_manager.has_permission('manage_settings'):
                return False
            
            # Get default value from config
            default_value = config.get(key)
            if default_value is not None:
                return self.set_setting(key, default_value)
            else:
                # Remove setting if no default
                return self.delete_setting(key)
        except Exception as e:
            print(f"Reset setting error: {e}")
            return False
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting."""
        try:
            if not user_manager.has_permission('manage_settings'):
                return False
            
            rows_affected = db.execute_update(
                "DELETE FROM settings WHERE key = ?",
                (key,)
            )
            
            if rows_affected > 0:
                # Remove from cache
                self.cache.pop(key, None)
                return True
            
            return False
        except Exception as e:
            print(f"Delete setting error: {e}")
            return False
    
    def reset_all_settings(self) -> bool:
        """Reset all settings to defaults."""
        try:
            if not user_manager.is_admin():
                return False
            
            # Clear all settings from database
            db.execute_update("DELETE FROM settings")
            
            # Reload default settings
            self.cache = config.to_dict()
            
            # Save defaults to database
            for key, value in self.cache.items():
                db.execute_update(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (key, str(value))
                )
            
            return True
        except Exception as e:
            print(f"Reset all settings error: {e}")
            return False
    
    def get_application_settings(self) -> Dict[str, Any]:
        """Get application-specific settings."""
        app_settings = {}
        app_keys = [
            'app_name', 'version', 'window_width', 'window_height',
            'theme', 'language', 'auto_backup', 'backup_interval_days',
            'low_stock_alert', 'currency_symbol', 'date_format', 'decimal_places'
        ]
        
        for key in app_keys:
            app_settings[key] = self.get_setting(key, config.get(key))
        
        return app_settings
    
    def get_user_preferences(self, user_id: int = None) -> Dict[str, Any]:
        """Get user-specific preferences."""
        if not user_id:
            current_user = user_manager.get_current_user()
            if not current_user:
                return {}
            user_id = current_user['id']
        
        # For now, return general settings
        # In a full implementation, this would be user-specific
        return {
            'theme': self.get_setting('theme', 'light'),
            'language': self.get_setting('language', 'en'),
            'date_format': self.get_setting('date_format', '%Y-%m-%d'),
            'currency_symbol': self.get_setting('currency_symbol', '$'),
            'decimal_places': self.get_setting('decimal_places', 2)
        }
    
    def update_user_preferences(self, preferences: Dict[str, Any], user_id: int = None) -> bool:
        """Update user-specific preferences."""
        # For now, update general settings
        # In a full implementation, this would be user-specific
        results = self.update_settings(preferences)
        return all(results.values())
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            import platform
            import sys
            
            # Database info
            db_stats = db.execute_query("""
                SELECT 
                    (SELECT COUNT(*) FROM products) as product_count,
                    (SELECT COUNT(*) FROM customers) as customer_count,
                    (SELECT COUNT(*) FROM suppliers) as supplier_count,
                    (SELECT COUNT(*) FROM users) as user_count,
                    (SELECT COUNT(*) FROM stock_movements) as movement_count
            """)[0]
            
            return {
                'application': {
                    'name': self.get_setting('app_name', 'ToluStock'),
                    'version': self.get_setting('version', '1.0.0'),
                    'database_file': db.db_path
                },
                'system': {
                    'platform': platform.platform(),
                    'python_version': sys.version,
                    'architecture': platform.architecture()[0]
                },
                'database': db_stats,
                'settings_count': len(self.cache)
            }
        except Exception as e:
            print(f"Get system info error: {e}")
            return {}
    
    def export_settings(self, filename: str = None) -> Optional[str]:
        """Export settings to file."""
        try:
            if not user_manager.has_permission('backup_data'):
                return None
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tolustock_settings_{timestamp}.json"
            
            from .utils import export_to_json
            
            export_data = {
                'export_info': {
                    'export_date': datetime.now().isoformat(),
                    'exported_by': user_manager.get_current_user().get('username', 'Unknown'),
                    'application': self.get_setting('app_name', 'ToluStock'),
                    'version': self.get_setting('version', '1.0.0')
                },
                'settings': self.get_all_settings()
            }
            
            if export_to_json(export_data, filename):
                return filename
            
            return None
        except Exception as e:
            print(f"Export settings error: {e}")
            return None
    
    def import_settings(self, filename: str, overwrite_existing: bool = False) -> Dict[str, Any]:
        """Import settings from file."""
        try:
            if not user_manager.is_admin():
                return {'success': False, 'message': 'Admin access required'}
            
            from .utils import import_from_json
            
            data = import_from_json(filename)
            if not data or 'settings' not in data:
                return {'success': False, 'message': 'Invalid settings file'}
            
            imported_count = 0
            errors = []
            
            for key, value in data['settings'].items():
                if not overwrite_existing and key in self.cache:
                    continue
                
                if self.set_setting(key, value):
                    imported_count += 1
                else:
                    errors.append(f"Failed to import setting: {key}")
            
            return {
                'success': True,
                'imported': imported_count,
                'total': len(data['settings']),
                'errors': errors
            }
        except Exception as e:
            print(f"Import settings error: {e}")
            return {'success': False, 'message': str(e)}
    
    def validate_settings(self) -> Dict[str, Any]:
        """Validate current settings."""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Validate window dimensions
            width = self.get_setting('window_width', 1200)
            height = self.get_setting('window_height', 800)
            
            if width < 800:
                validation_results['warnings'].append('Window width is less than recommended minimum (800px)')
            if height < 600:
                validation_results['warnings'].append('Window height is less than recommended minimum (600px)')
            
            # Validate backup settings
            backup_interval = self.get_setting('backup_interval_days', 7)
            if backup_interval < 1:
                validation_results['errors'].append('Backup interval must be at least 1 day')
                validation_results['valid'] = False
            
            # Validate decimal places
            decimal_places = self.get_setting('decimal_places', 2)
            if decimal_places < 0 or decimal_places > 6:
                validation_results['warnings'].append('Decimal places should be between 0 and 6')
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
            validation_results['valid'] = False
        
        return validation_results
    
    def get_setting_definition(self, key: str) -> Dict[str, Any]:
        """Get setting definition and metadata."""
        definitions = {
            'app_name': {
                'type': 'string',
                'description': 'Application name',
                'default': 'ToluStock',
                'required': True
            },
            'version': {
                'type': 'string',
                'description': 'Application version',
                'default': '1.0.0',
                'readonly': True
            },
            'window_width': {
                'type': 'integer',
                'description': 'Default window width',
                'default': 1200,
                'min': 800,
                'max': 2560
            },
            'window_height': {
                'type': 'integer',
                'description': 'Default window height',
                'default': 800,
                'min': 600,
                'max': 1440
            },
            'theme': {
                'type': 'choice',
                'description': 'Application theme',
                'default': 'light',
                'choices': ['light', 'dark']
            },
            'language': {
                'type': 'choice',
                'description': 'Application language',
                'default': 'en',
                'choices': ['en', 'tr']
            },
            'auto_backup': {
                'type': 'boolean',
                'description': 'Enable automatic backups',
                'default': True
            },
            'backup_interval_days': {
                'type': 'integer',
                'description': 'Backup interval in days',
                'default': 7,
                'min': 1,
                'max': 365
            },
            'low_stock_alert': {
                'type': 'boolean',
                'description': 'Enable low stock alerts',
                'default': True
            },
            'currency_symbol': {
                'type': 'string',
                'description': 'Currency symbol',
                'default': '$',
                'max_length': 3
            },
            'date_format': {
                'type': 'choice',
                'description': 'Date format',
                'default': '%Y-%m-%d',
                'choices': ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
            },
            'decimal_places': {
                'type': 'integer',
                'description': 'Number of decimal places for currency',
                'default': 2,
                'min': 0,
                'max': 6
            }
        }
        
        return definitions.get(key, {
            'type': 'string',
            'description': f'Setting: {key}',
            'default': None
        })


# Global settings manager instance
settings_manager = SettingsManager()