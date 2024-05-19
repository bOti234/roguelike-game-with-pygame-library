from typing import List

class User():
    def __init__(self, username: str, password: str):
        self.username: str = username
        self.password: str = password
        self.scorehistory: List[int] = []
        self.highscore: int = 0
    
    def set_password(self, password1: str, password2: str):
        if password1 == password2:
            self.password = password1
            return "Password updated!"
        else:
            return "Please make sure that the passwords match!"