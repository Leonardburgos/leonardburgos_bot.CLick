import os

class DirectoryPath:
    def __init__(self) -> None:
        pass

    def user_documents_path(self):
        """
        Returns the path to the user's Documents directory and creates 
        a '.pgocapp' folder inside it if it doesn't already exist.
        """
        # Get the path to the user's Documents directory
        user_documents = os.path.expanduser('~')
        documents_path = os.path.join(user_documents, 'Documents')
        
        # Define the new folder path inside the Documents directory
        new_folder_path = os.path.join(documents_path, 'botclickRecordings')
        
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)  # Create the folder if it doesn't exist
        
        return new_folder_path

    def generate_unique_filename(self, base_name: str, extension: str) -> str:
        """Generate a unique filename by checking if the file already exists."""
        directory = self.user_documents_path()  # Use Documents folder
        count = 1
        file_path = os.path.join(directory, f"{base_name}_{count}{extension}")

        # Check if the file already exists, and increment the count if it does
        while os.path.exists(file_path):
            count += 1
            file_path = os.path.join(directory, f"{base_name}_{count}{extension}")

        return file_path
