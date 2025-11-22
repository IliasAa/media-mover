class FileTransferProps:
    def __init__(self, from_path, to_path, filter_blurry, filter_lookalikes, create_date_folders, save_hashes):
        self.from_path = from_path
        self.to_path = to_path
        self.filter_blurry = filter_blurry
        self.filter_lookalikes = filter_lookalikes
        self.create_date_folders = create_date_folders
        self.save_hashes = save_hashes
        self.items = []
        
        
    def toggle_blurry(self):
        self.filter_blurry = not self.filter_blurry

    def toggle_lookalikes(self):
        self.filter_lookalikes = not self.filter_lookalikes

    def toggle_date_folders(self):
        self.create_date_folders = not self.create_date_folders
        
    def toggle_hashes(self):
        self.save_hashes = not self.save_hashes