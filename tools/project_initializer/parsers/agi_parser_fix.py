from utils.agi_logger import AGILogger

class AGIReportParser:
    def __init__(self, agi_md_path: str, logger=None):
        self.agi_md_path = agi_md_path
        self.logger = logger if logger else AGILogger('INFO')
        # ... reste du code
