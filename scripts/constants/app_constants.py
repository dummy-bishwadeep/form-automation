class AppConstants:
    step_category = 'step_category'
    project_type = 'project_type'
    tz = 'tz'
    langauge = 'language'
    metadata_sheet = 'Metadata'
    permissions = 'Permissions'

class AutomationConstants:
    tz = 'Asia/Kolkata'
    language = 'en'
    project_type = 'n_level_hierarchy'


class Secrets:
    LOCK_OUT_TIME_MINS = 30
    leeway_in_mins = 10
    unique_key = "45c37939-0f75"
    token = "8674cd1d-2578-4a62-8ab7-d3ee5f9a"
    issuer = "ilens"
    alg = "HS256"
    signature_key = "kliLensKLiLensKL"
    signature_key_alg = ["HS256"]
    headers = {
        'Content-Type': 'application/json',
    }