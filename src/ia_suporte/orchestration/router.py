



from telegram import Update
from telegram.ext import ContextTypes


def router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("Router")