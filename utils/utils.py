import os


class Utils:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
