# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('main.py', '.'), ('assets', 'assets/'), ('conf', 'conf/'), ('conf\\application.conf', 'conf/'), ('templates', 'templates/'), ('templates\\AutomationScriptDocumentation.docx', 'templates/'), ('templates\\AutomationTemplate.xlsx', 'templates/'), ('templates\\pgp_template.xlsx', 'templates/'), ('templates\\staging_template.xlsx', 'templates/'), ('scripts', 'scripts/'), ('scripts\\config', 'scripts/config/'), ('scripts\\config\\__init__.py', 'scripts/config/'), ('scripts\\config\\app_configurations.py', 'scripts/config/'), ('scripts\\config\\constants.py', 'scripts/config/'), ('scripts\\config\\description.py', 'scripts/config/'), ('scripts\\constants', 'scripts/constants/'), ('scripts\\constants\\__init__.py', 'scripts/constants/'), ('scripts\\constants\\api_constants.py', 'scripts/constants/'), ('scripts\\constants\\app_constants.py', 'scripts/constants/'), ('scripts\\constants\\logbook_constants.py', 'scripts/constants/'), ('scripts\\constants\\step_constants.py', 'scripts/constants/'), ('scripts\\constants\\template_constants.py', 'scripts/constants/'), ('scripts\\constants\\workflow_constants.py', 'scripts/constants/'), ('scripts\\core', 'scripts/core/'), ('scripts\\core\\handlers', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\datagrid_handler.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\form_handler.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\logbook_handler.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\meta_data.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\new_datagrid_handler.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\table_merge.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\template_handler.py', 'scripts/core/handlers/'), ('scripts\\core\\handlers\\workflow_handler.py', 'scripts/core/handlers/'), ('scripts\\core\\schemas', 'scripts/core/schemas/'), ('scripts\\core\\schemas\\__init__.py', 'scripts/core/schemas/'), ('scripts\\core\\schemas\\step_models.py', 'scripts/core/schemas/'), ('scripts\\core\\schemas\\template_model.py', 'scripts/core/schemas/'), ('scripts\\logging', 'scripts/logging/'), ('scripts\\logging\\__init__.py', 'scripts/logging/'), ('scripts\\logging\\logger.py', 'scripts/logging/'), ('scripts\\schemas', 'scripts/schemas/'), ('scripts\\schemas\\__init__.py', 'scripts/schemas/'), ('scripts\\schemas\\input_fileds.py', 'scripts/schemas/'), ('scripts\\services', 'scripts/services/'), ('scripts\\services\\__init__.py', 'scripts/services/'), ('scripts\\services\\form_services.py', 'scripts/services/'), ('scripts\\services\\logbooks.py', 'scripts/services/'), ('scripts\\services\\new_datagrid.py', 'scripts/services/'), ('scripts\\services\\table.py', 'scripts/services/'), ('scripts\\services\\template_services.py', 'scripts/services/'), ('scripts\\utils', 'scripts/utils/'), ('scripts\\utils\\common_utils.py', 'scripts/utils/'), ('scripts\\utils\\component.json', 'scripts/utils/'), ('scripts\\utils\\fix_error.py', 'scripts/utils/'), ('scripts\\utils\\logbook_utils.py', 'scripts/utils/'), ('scripts\\utils\\sub_headers.json', 'scripts/utils/'), ('scripts\\utils\\security_utils', 'scripts/utils/security_utils/'), ('scripts\\utils\\security_utils\\__init__.py', 'scripts/utils/security_utils/'), ('scripts\\utils\\security_utils\\jwt_util.py', 'scripts/utils/security_utils/'), ('scripts\\utils\\security_utils\\security.py', 'scripts/utils/security_utils/')],
    hiddenimports=['anyio', 'click', 'colorama', 'et-xmlfile', 'exceptiongroup', 'fastapi', 'h11', 'idna', 'numpy', 'openpyxl', 'pandas', 'pydantic', 'pydantic-settings', 'pydantic_core', 'python-dateutil', 'python-dotenv', 'python-multipart', 'pytz', 'six', 'sniffio', 'starlette', 'typing_extensions', 'tzdata', 'uvicorn', 'httpx', 'requests', 'jwt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
