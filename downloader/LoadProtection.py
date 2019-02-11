

class LoadProtection:

    used_attempts = 0
    max_attempts = 10

    def register_new_usage(self):
        self.used_attempts += 1

    def is_allowed_to_handle(self):
        return self.get_attempts_count() > 0

    def get_attempts_count(self):
        return self.max_attempts - self.used_attempts

    def reset_license(self):
        self.used_attempts = 0
