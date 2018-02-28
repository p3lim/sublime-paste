import sublime
from sublime_plugin import TextCommand

from urllib.request import Request, urlopen
from urllib.parse import urlencode

PANEL_NAME = 'Paste'
PANEL_TEXT = 'Uploaded successfully to \'{}\'\nAdded link to the clipboard.'

class PasteUploadAsyncCommand(TextCommand):
	def run(self, edit, text):
		settings = sublime.load_settings('Paste.sublime-settings')
		host = settings.get('host')

		# TODO: fix encoding issues, e.g. æøå doesn't work well
		data = urlencode({'c': text}).encode('utf-8')

		req = Request(host, data)
		with urlopen(req) as res:
			url = res.read().decode('utf-8')

			panel = self.view.window().create_output_panel(PANEL_NAME)
			panel.set_read_only(False)
			panel.erase(edit, sublime.Region(0, panel.size()))
			panel.insert(edit, 0, PANEL_TEXT.format(url))
			panel.set_read_only(True)
			panel.show(0)

			self.view.window().run_command('show_panel', {'panel': 'output.{}'.format(PANEL_NAME)})
			sublime.set_clipboard(url)

class PasteUploadCommand(TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			if region.empty():
				text = self.view.substr(sublime.Region(0, self.view.size()))
			else:
				text = self.view.substr(region)

			sublime.set_timeout_async(lambda: self.view.run_command('paste_upload_async', {'text': text}), 0)
