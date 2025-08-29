import os
import json
import requests

class SecureAPIClient:
    def __init__(self, local_file: str = "api.json", remote_url: str = "https://ugkeapi.netlify.app/api.json"):
        self.local_file = local_file
        self.remote_url = remote_url
        self.apis = self._load_apis()

    def _load_apis(self):
        """
        Loads APIs from local file if available and not empty.
        Otherwise fetches from remote URL and saves locally.
        """
        # ✅ Step 1: Check local file
        if os.path.exists(self.local_file):
            try:
                with open(self.local_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data:  # Not empty
                    return data
            except (json.JSONDecodeError, OSError):
                pass  # Will fetch fresh

        # ✅ Step 2: Fetch from remote
        try:
            resp = requests.get(self.remote_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Save locally
            with open(self.local_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data
        except Exception as e:
            print(f"[ERROR] Failed to fetch APIs: {e}")
            return {}

    def get_apis(self):
        """
        Returns all APIs as dictionary.
        """
        return self.apis

    def get_api(self, name: str):
        """
        Returns specific API by name.
        """
        return self.apis.get(name)

    def refresh(self):
        """
        Forces refresh from remote and updates local cache.
        """
        try:
            resp = requests.get(self.remote_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            with open(self.local_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.apis = data
            return True
        except Exception as e:
            print(f"[ERROR] Refresh failed: {e}")
            return False
