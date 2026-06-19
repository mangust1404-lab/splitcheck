from telegram import Bot

from app.config import settings

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.bot_token)
    return _bot


async def send_notification(telegram_id: int, message: str) -> bool:
    """Send a message to a Telegram user. Returns True on success."""
    try:
        bot = get_bot()
        await bot.send_message(chat_id=telegram_id, text=message, parse_mode="HTML")
        return True
    except Exception:
        return False


async def send_settle_reminder(
    debtor_telegram_id: int,
    debtor_name: str,
    creditor_name: str,
    amount: str,
    currency: str,
    group_name: str,
) -> bool:
    message = (
        f"\U0001f4b8 <b>Payment Reminder</b>\n\n"
        f"{debtor_name}, you owe <b>{amount} {currency}</b> to {creditor_name}\n"
        f"Group: {group_name}\n\n"
        f"Open SplitCheck to settle up!"
    )
    return await send_notification(debtor_telegram_id, message)


async def send_expense_notification(
    telegram_id: int,
    payer_name: str,
    expense_title: str,
    amount: str,
    currency: str,
    group_name: str,
) -> bool:
    message = (
        f"\U0001f4dd <b>New Expense</b>\n\n"
        f"{payer_name} added <b>{expense_title}</b> \u2014 {amount} {currency}\n"
        f"Group: {group_name}"
    )
    return await send_notification(telegram_id, message)
