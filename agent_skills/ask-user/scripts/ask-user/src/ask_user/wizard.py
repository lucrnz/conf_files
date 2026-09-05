"""PySide6 wizard: one question per page, Other row, Finish-time validation."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from ask_user.payload import RESERVED_OTHER, Answer, Payload, Question, first_incomplete

ERROR_TEXT = "This question needs an answer."


class QuestionPage(QWizardPage):
    def __init__(
        self,
        question: Question,
        number: int,
        total: int,
        *,
        is_last: bool,
    ) -> None:
        super().__init__()
        self._question = question
        self._is_last = is_last
        self._option_buttons: list[tuple[QAbstractButton, str]] = []
        self.setTitle(f"Question {number} of {total}")

        layout = QVBoxLayout(self)
        prompt = QLabel(question.question)
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        self._group: QButtonGroup | None = None
        if not question.multi_select:
            self._group = QButtonGroup(self)
            self._group.setExclusive(True)

        for index, option in enumerate(question.options):
            button = self._make_option_button(option.label)
            self._option_buttons.append((button, option.label))
            if self._group is not None:
                self._group.addButton(button)
            row = QHBoxLayout()
            row.addWidget(button)
            if index == 0:
                badge = QLabel("Recommended")
                row.addWidget(badge)
            row.addStretch()
            layout.addLayout(row)
            if option.description:
                description = QLabel(option.description)
                description.setWordWrap(True)
                layout.addWidget(description)
            button.toggled.connect(self._hide_error)

        other_row = QHBoxLayout()
        self._other_button = self._make_option_button(RESERVED_OTHER)
        if self._group is not None:
            self._group.addButton(self._other_button)
        self._other_edit = QLineEdit()
        self._other_edit.setEnabled(False)
        self._other_button.toggled.connect(self._sync_other)
        self._other_edit.textChanged.connect(self._hide_error)
        other_row.addWidget(self._other_button)
        other_row.addWidget(self._other_edit)
        layout.addLayout(other_row)

        self._error = QLabel(ERROR_TEXT)
        self._error.setWordWrap(True)
        self._error.hide()
        layout.addWidget(self._error)
        layout.addStretch()

    def _make_option_button(self, label: str) -> QAbstractButton:
        if self._question.multi_select:
            return QCheckBox(label)
        return QRadioButton(label)

    def isComplete(self) -> bool:
        return True

    def validateCurrentPage(self) -> bool:
        if not self._is_last:
            return True
        wizard = self.wizard()
        assert isinstance(wizard, AskWizard)
        return wizard.validate_all()

    def selection(self) -> tuple[tuple[str, ...], str | None]:
        selected = tuple(label for button, label in self._option_buttons if button.isChecked())
        other = None
        if self._other_button.isChecked():
            text = self._other_edit.text().strip()
            if text:
                other = text
        return selected, other

    def show_error(self) -> None:
        self._error.setText(ERROR_TEXT)
        self._error.show()

    def _hide_error(self, *_args: object) -> None:
        self._error.hide()

    def _sync_other(self, checked: bool) -> None:
        self._other_edit.setEnabled(checked)
        self._hide_error()
        if checked:
            self._other_edit.setFocus()


class AskWizard(QWizard):
    def __init__(self, payload: Payload) -> None:
        super().__init__()
        self.setWindowTitle("ask-user")
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
        self.setOption(QWizard.WizardOption.IndependentPages, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        self.setOption(QWizard.WizardOption.NoCancelButton, False)
        self.setOption(QWizard.WizardOption.HaveNextButtonOnLastPage, False)
        self.setOption(QWizard.WizardOption.HaveFinishButtonOnEarlyPages, False)
        self.setMinimumSize(520, 400)
        self.pages: list[QuestionPage] = []
        self._page_ids: list[int] = []
        total = len(payload.questions)
        for index, question in enumerate(payload.questions):
            page = QuestionPage(
                question,
                index + 1,
                total,
                is_last=index == total - 1,
            )
            page_id = self.addPage(page)
            self.pages.append(page)
            self._page_ids.append(page_id)

    def validate_all(self) -> bool:
        states = [page.selection() for page in self.pages]
        index = first_incomplete(states)
        if index is None:
            return True
        self.setCurrentId(self._page_ids[index])
        self.pages[index].show_error()
        return False


def run_wizard(payload: Payload) -> list[Answer] | None:
    wizard = AskWizard(payload)
    wizard.show()
    wizard.raise_()
    wizard.activateWindow()
    if wizard.exec() != QDialog.DialogCode.Accepted:
        return None
    answers: list[Answer] = []
    for question, page in zip(payload.questions, wizard.pages, strict=True):
        selected, other = page.selection()
        answers.append(Answer(question=question.question, selected=selected, other=other))
    return answers
