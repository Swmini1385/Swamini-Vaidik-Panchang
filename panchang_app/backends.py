import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger(__name__)
User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Retrieve the email from username or kwargs
        email = username or kwargs.get('email') or kwargs.get('username')
        
        # Log authentication attempt
        print(f"[DEBUG AUTH] Email entered: '{email}'")
        
        if not email:
            print("[DEBUG AUTH] Authentication failed: No email provided.")
            return None
            
        try:
            # Case-insensitive lookup for email
            user = User.objects.get(email__iexact=email)
            print(f"[DEBUG AUTH] User found in database: {user.email} (is_active={user.is_active})")
        except User.DoesNotExist:
            print(f"[DEBUG AUTH] Authentication failed: User '{email}' not found.")
            # Run standard hashing check to prevent timing attacks
            User().set_password(password)
            return None
            
        if user.check_password(password):
            if self.user_can_authenticate(user):
                print(f"[DEBUG AUTH] Authentication success: User '{user.email}' authenticated successfully.")
                return user
            else:
                print(f"[DEBUG AUTH] Authentication failed: User '{user.email}' is not active or disabled.")
        else:
            print(f"[DEBUG AUTH] Authentication failed: Incorrect password for user '{user.email}'.")
            
        return None
