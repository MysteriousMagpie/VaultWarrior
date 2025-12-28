from datetime import datetime
import os

class DailyNoteManager:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.daily_notes_dir = os.path.join(vault_path, 'daily')
        os.makedirs(self.daily_notes_dir, exist_ok=True)

    def get_today_note_path(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.daily_notes_dir, f'{today}.md')

    def write_daily_note(self, content):
        note_path = self.get_today_note_path()
        with open(note_path, 'a') as note_file:
            note_file.write(content + '\n')

    def read_daily_note(self):
        note_path = self.get_today_note_path()
        if os.path.exists(note_path):
            with open(note_path, 'r') as note_file:
                return note_file.read()
        return None

    def clear_daily_note(self):
        note_path = self.get_today_note_path()
        if os.path.exists(note_path):
            os.remove(note_path)