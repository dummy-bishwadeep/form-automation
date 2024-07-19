import os
import shutil
from scripts.constants import EnvironmentConstants


class KeyPath:
    keys_path = EnvironmentConstants.key_path
    if not os.path.isfile(os.path.join(keys_path, "public")) or not os.path.isfile(os.path.join(keys_path, "private")):
        if not os.path.exists(keys_path):
            os.makedirs(keys_path)
        shutil.copy(os.path.join("assets", "keys", "public"), os.path.join(keys_path, "public"))

        shutil.copy(os.path.join("assets", "keys", "private"), os.path.join(keys_path, "private"))

    public = os.path.join(keys_path, "public")
    private = os.path.join(keys_path, "private")
