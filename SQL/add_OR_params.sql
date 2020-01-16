INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_OR.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_OR.sh', 'oregon');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_directory_prefix', 'Unclassified/test_or', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- illinois
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'url', 'https://secure.sos.state.or.us/muni/public.do', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'downloads_path', '/tmp/downloads/OR/', 'temp (local) folder for file downloads');
