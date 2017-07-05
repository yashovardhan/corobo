from errbot import BotPlugin, botcmd

from answers.final import get_answer


class Answer(BotPlugin):

    @botcmd
    def answer(self, msg, arg):
        answers = get_answer(arg, final=True)
        if answers:
            return answers[0][0]
        else:
            return 'Dunno'
