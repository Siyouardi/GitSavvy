import os

import sublime
from sublime_plugin import WindowCommand

from .base_command import BaseCommand


NO_REPO_MESSAGE = ("It looks like you haven't initialized Git in this directory.  "
                   "Would you like to?")
REPO_PATH_PROMPT = "Enter root path of new git repo:"
CONFIRM_REINITIALIZE = ("It looks like Git is already initialized here.  "
                        "Would you like to re-initialize?")


class GsOfferInit(WindowCommand):

    """
    If a git command fails indicating no git repo was found, this
    command will ask the user whether they'd like to init a new repo.
    """

    def run(self):
        if sublime.ok_cancel_dialog(NO_REPO_MESSAGE):
            self.window.run_command("gs_init")


class GsInit(WindowCommand, BaseCommand):

    """
    If the active Sublime window has folders added to the project (or if Sublime was
    opened from the terminal with something like `subl .`), initialize a new Git repo
    at that location.  If that directory cannot be determined, use the open file's
    directory.  If there is no open file, prompt the user for the directory to use.

    If the selected directory has previosly been initialized with Git, prompt the user
    to confirm a re-initialize before proceeding.
    """

    def run(self):
        open_folders = self.window.folders()
        if open_folders:
            suggested_git_root = open_folders[0]
        else:
            file_path = self.window.active_view().file_name()
            if file_path:
                suggested_git_root = os.path.dirname(file_path)
            else:
                suggested_git_root = ""

        if suggested_git_root and os.path.exists(os.path.join(suggested_git_root, ".git")):
            if sublime.ok_cancel_dialog(CONFIRM_REINITIALIZE):
                self.on_done(suggested_git_root, re_init=True)
            return

        self.window.show_input_panel(REPO_PATH_PROMPT, suggested_git_root, self.on_done, None, None)

    def on_done(self, path, re_init=False):
        self.git("init", working_dir=path)
        sublime.status_message("{word_start}nitialized repo successfully.".format(
            word_start="Re-i" if re_init else "I"))
