class TooManyWordsError(Exception):
    
    def __init__(self):
        self.massage = f"Error! Your folder's name should have only 1 word"
        super().__init__(self.massage)


class UnchoosedDirectoryError(Exception):
    
    def __init__(self):
        self.massage = f"Error! Choose a directory to sort"
        super().__init__(self.massage)