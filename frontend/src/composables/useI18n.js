import { ref } from 'vue'

// Detect language from Telegram WebApp user data, default to English
const langCode = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || 'en'
const locale = ref(langCode === 'ru' ? 'ru' : 'en')

const messages = {
  en: {
    // MyTrips
    'myTrips.title': 'My Trips',
    'myTrips.active': 'Active',
    'myTrips.archive': 'Archive',
    'myTrips.authFailed': 'Auth failed. Please reopen the app.',
    'myTrips.loading': 'Loading...',
    'myTrips.noActive': 'No active trips',
    'myTrips.noArchived': 'No archived trips',
    'myTrips.newTrip': '+ New Trip',

    // CreateGroup
    'createGroup.title': 'New Trip',
    'createGroup.tripName': 'Trip name',
    'createGroup.tripPlaceholder': 'e.g. Bali with friends',
    'createGroup.baseCurrency': 'Base currency',
    'createGroup.participants': 'Participants',
    'createGroup.participantN': 'Participant {n}',
    'createGroup.addParticipant': '+ Add participant',
    'createGroup.creating': 'Creating...',
    'createGroup.create': 'Create Trip',

    // TripDetail
    'tripDetail.invite': 'Invite',
    'tripDetail.expenses': 'Expenses',
    'tripDetail.balances': 'Balances',
    'tripDetail.settlements': 'Settlements',
    'tripDetail.noExpenses': 'No expenses yet',
    'tripDetail.totalSpending': 'Total Spending',
    'tripDetail.allSettled': 'All settled!',
    'tripDetail.scanReceipt': 'Scan Receipt',
    'tripDetail.manual': 'Manual',
    'tripDetail.inviteCopied': 'Invite link copied!',
    'tripDetail.reminderSent': 'Reminder sent!',
    'tripDetail.reminderFailed': 'Failed to send reminder',

    // AddExpense
    'addExpense.title': 'Add Expense',
    'addExpense.expenseTitle': 'Title',
    'addExpense.titlePlaceholder': 'e.g. Restaurant',
    'addExpense.amount': 'Amount',
    'addExpense.currency': 'Currency',
    'addExpense.paidBy': 'Paid by',
    'addExpense.splitMode': 'Split mode',
    'addExpense.equal': 'Equal',
    'addExpense.custom': 'Custom',
    'addExpense.splitAmong': 'Split among',
    'addExpense.amounts': 'Amounts',
    'addExpense.assigned': 'Assigned: {assigned} / {total} · Remaining: {remaining}',
    'addExpense.splitRemainder': 'Split remainder equally',
    'addExpense.saving': 'Saving...',
    'addExpense.save': 'Save Expense',
    'addExpense.editTitle': 'Edit Expense',
    'addExpense.update': 'Update Expense',

    // ScanReceipt
    'scanReceipt.title': 'Scan Receipt',
    'scanReceipt.tapToScan': 'Tap to take a photo or choose from gallery',
    'scanReceipt.camera': 'Camera',
    'scanReceipt.gallery': 'Gallery',
    'scanReceipt.scanning': 'Scanning receipt...',
    'scanReceipt.expensePlaceholder': 'Expense title',
    'scanReceipt.paidBy': 'Paid by:',
    'scanReceipt.assigned': 'Assigned:',
    'scanReceipt.remaining': 'Remaining:',
    'scanReceipt.saving': 'Saving...',
    'scanReceipt.save': 'Save Expense',
    'scanReceipt.defaultTitle': 'Scanned receipt',
    'scanReceipt.scanFailed': 'Failed to scan receipt. Try again.',
    'scanReceipt.detectedCurrency': 'Currency: {currency}',
    'scanReceipt.discount': 'Discount',
    'scanReceipt.itemsTotal': 'Items total',
    'scanReceipt.receiptTotal': 'Receipt total',
    'scanReceipt.selectedCount': '{count} selected',
    'scanReceipt.assignTo': 'Assign to:',
    'scanReceipt.selectItems': 'Tap items to select, then assign',

    // GroupSettings
    'groupSettings.title': 'Group Settings',
    'groupSettings.tripName': 'Trip name',
    'groupSettings.inviteLink': 'Invite link',
    'groupSettings.copy': 'Copy',
    'groupSettings.participants': 'Participants ({count})',
    'groupSettings.telegramLinked': 'Telegram linked',
    'groupSettings.virtual': 'Virtual',
    'groupSettings.admin': 'Admin',
    'groupSettings.addPlaceholder': 'Add participant',
    'groupSettings.add': 'Add',
    'groupSettings.archive': 'Archive Trip',
    'groupSettings.reactivate': 'Reactivate Trip',
    'groupSettings.delete': 'Delete Trip',
    'groupSettings.deleteConfirm': 'Delete this trip permanently?',
    'groupSettings.deleteFailed': 'Failed to delete',
    'groupSettings.inviteCopied': 'Invite link copied!',

    // JoinGroup
    'joinGroup.loading': 'Loading...',
    'joinGroup.backToTrips': 'Back to My Trips',
    'joinGroup.invitedTo': 'You are invited to',
    'joinGroup.participants': 'Participants ({count})',
    'joinGroup.telegramLinked': 'Telegram linked',
    'joinGroup.virtual': 'Virtual',
    'joinGroup.thisIsMe': 'This is me',
    'joinGroup.joining': 'Joining...',
    'joinGroup.joinAsNew': 'Join as new participant',
    'joinGroup.authFailed': 'Auth failed. Please reopen the app.',
    'joinGroup.invalidInvite': 'Invalid invite link',
    'joinGroup.joinFailed': 'Failed to join group',

    // ExpenseItem
    'expenseItem.paid': '{name} paid · {splitType}',

    // ExpenseDetail
    'expenseDetail.loading': 'Loading...',
    'expenseDetail.paidBy': '{name} paid',
    'expenseDetail.rate': 'Rate',
    'expenseDetail.items': 'Items',
    'expenseDetail.distribution': 'Distribution',
    'expenseDetail.edit': 'Edit',
    'expenseDetail.delete': 'Delete Expense',
    'expenseDetail.deleting': 'Deleting...',
    'expenseDetail.deleteConfirm': 'Delete this expense?',

    // JoinGroup (extra)
    'joinGroup.title': 'Join Trip',

    // SettlementCard
    'settlementCard.paidConfirmed': 'Paid and confirmed',
    'settlementCard.paid': 'Paid',
    'settlementCard.markPaid': 'Mark Paid',
    'settlementCard.remind': 'Remind',
    'settlementCard.undo': 'Undo',
    'settlementCard.noTelegram': '{name} has no Telegram linked. They need to join via invite link.',
  },

  ru: {
    // MyTrips
    'myTrips.title': 'Мои поездки',
    'myTrips.active': 'Активные',
    'myTrips.archive': 'Архив',
    'myTrips.authFailed': 'Ошибка авторизации. Откройте приложение заново.',
    'myTrips.loading': 'Загрузка...',
    'myTrips.noActive': 'Нет активных поездок',
    'myTrips.noArchived': 'Нет архивных поездок',
    'myTrips.newTrip': '+ Новая поездка',

    // CreateGroup
    'createGroup.title': 'Новая поездка',
    'createGroup.tripName': 'Название',
    'createGroup.tripPlaceholder': 'напр. Бали с друзьями',
    'createGroup.baseCurrency': 'Основная валюта',
    'createGroup.participants': 'Участники',
    'createGroup.participantN': 'Участник {n}',
    'createGroup.addParticipant': '+ Добавить участника',
    'createGroup.creating': 'Создание...',
    'createGroup.create': 'Создать поездку',

    // TripDetail
    'tripDetail.invite': 'Пригласить',
    'tripDetail.expenses': 'Расходы',
    'tripDetail.balances': 'Балансы',
    'tripDetail.settlements': 'Расчёты',
    'tripDetail.noExpenses': 'Расходов пока нет',
    'tripDetail.totalSpending': 'Общие расходы',
    'tripDetail.allSettled': 'Все рассчитались!',
    'tripDetail.scanReceipt': 'Скан чека',
    'tripDetail.manual': 'Вручную',
    'tripDetail.inviteCopied': 'Ссылка-приглашение скопирована!',
    'tripDetail.reminderSent': 'Напоминание отправлено!',
    'tripDetail.reminderFailed': 'Не удалось отправить напоминание',

    // AddExpense
    'addExpense.title': 'Новый расход',
    'addExpense.expenseTitle': 'Название',
    'addExpense.titlePlaceholder': 'напр. Ресторан',
    'addExpense.amount': 'Сумма',
    'addExpense.currency': 'Валюта',
    'addExpense.paidBy': 'Оплатил',
    'addExpense.splitMode': 'Способ разделения',
    'addExpense.equal': 'Поровну',
    'addExpense.custom': 'Вручную',
    'addExpense.splitAmong': 'Разделить между',
    'addExpense.amounts': 'Суммы',
    'addExpense.assigned': 'Назначено: {assigned} / {total} · Остаток: {remaining}',
    'addExpense.splitRemainder': 'Разделить остаток поровну',
    'addExpense.saving': 'Сохранение...',
    'addExpense.save': 'Сохранить расход',
    'addExpense.editTitle': 'Редактировать расход',
    'addExpense.update': 'Обновить расход',

    // ScanReceipt
    'scanReceipt.title': 'Скан чека',
    'scanReceipt.tapToScan': 'Сфотографируйте чек или выберите из галереи',
    'scanReceipt.camera': 'Камера',
    'scanReceipt.gallery': 'Галерея',
    'scanReceipt.scanning': 'Сканирование чека...',
    'scanReceipt.expensePlaceholder': 'Название расхода',
    'scanReceipt.paidBy': 'Оплатил:',
    'scanReceipt.assigned': 'Назначено:',
    'scanReceipt.remaining': 'Остаток:',
    'scanReceipt.saving': 'Сохранение...',
    'scanReceipt.save': 'Сохранить расход',
    'scanReceipt.defaultTitle': 'Сканированный чек',
    'scanReceipt.scanFailed': 'Не удалось распознать чек. Попробуйте ещё раз.',
    'scanReceipt.detectedCurrency': 'Валюта: {currency}',
    'scanReceipt.discount': 'Скидка',
    'scanReceipt.itemsTotal': 'Итого позиции',
    'scanReceipt.receiptTotal': 'Итого по чеку',
    'scanReceipt.selectedCount': 'Выбрано: {count}',
    'scanReceipt.assignTo': 'Назначить:',
    'scanReceipt.selectItems': 'Выберите позиции, затем назначьте',

    // GroupSettings
    'groupSettings.title': 'Настройки группы',
    'groupSettings.tripName': 'Название',
    'groupSettings.inviteLink': 'Ссылка-приглашение',
    'groupSettings.copy': 'Копировать',
    'groupSettings.participants': 'Участники ({count})',
    'groupSettings.telegramLinked': 'Telegram привязан',
    'groupSettings.virtual': 'Виртуальный',
    'groupSettings.admin': 'Админ',
    'groupSettings.addPlaceholder': 'Добавить участника',
    'groupSettings.add': 'Добавить',
    'groupSettings.archive': 'Архивировать поездку',
    'groupSettings.reactivate': 'Восстановить поездку',
    'groupSettings.delete': 'Удалить поездку',
    'groupSettings.deleteConfirm': 'Удалить поездку безвозвратно?',
    'groupSettings.deleteFailed': 'Не удалось удалить',
    'groupSettings.inviteCopied': 'Ссылка-приглашение скопирована!',

    // JoinGroup
    'joinGroup.loading': 'Загрузка...',
    'joinGroup.backToTrips': 'Вернуться к поездкам',
    'joinGroup.invitedTo': 'Вас приглашают в',
    'joinGroup.participants': 'Участники ({count})',
    'joinGroup.telegramLinked': 'Telegram привязан',
    'joinGroup.virtual': 'Виртуальный',
    'joinGroup.thisIsMe': 'Это я',
    'joinGroup.joining': 'Присоединение...',
    'joinGroup.joinAsNew': 'Присоединиться как новый участник',
    'joinGroup.authFailed': 'Ошибка авторизации. Откройте приложение заново.',
    'joinGroup.invalidInvite': 'Недействительная ссылка-приглашение',
    'joinGroup.joinFailed': 'Не удалось присоединиться к группе',

    // ExpenseItem
    'expenseItem.paid': '{name} оплатил · {splitType}',

    // ExpenseDetail
    'expenseDetail.loading': 'Загрузка...',
    'expenseDetail.paidBy': '{name} оплатил',
    'expenseDetail.rate': 'Курс',
    'expenseDetail.items': 'Позиции',
    'expenseDetail.distribution': 'Распределение',
    'expenseDetail.edit': 'Редактировать',
    'expenseDetail.delete': 'Удалить расход',
    'expenseDetail.deleting': 'Удаление...',
    'expenseDetail.deleteConfirm': 'Удалить этот расход?',

    // JoinGroup (extra)
    'joinGroup.title': 'Присоединиться',

    // SettlementCard
    'settlementCard.paidConfirmed': 'Оплачено и подтверждено',
    'settlementCard.paid': 'Оплачено',
    'settlementCard.markPaid': 'Оплатил',
    'settlementCard.remind': 'Напомнить',
    'settlementCard.undo': 'Отменить',
    'settlementCard.noTelegram': '{name} не привязан к Telegram. Нужно присоединиться по ссылке-приглашению.',
  },
}

/**
 * Lightweight i18n composable with shared reactive locale.
 * Auto-detects language from Telegram WebApp user data.
 */
export function useI18n() {
  /**
   * Translate a key, optionally interpolating {param} placeholders.
   * Falls back to the key itself if no translation is found.
   */
  function t(key, params) {
    let msg = messages[locale.value]?.[key] || messages.en[key] || key
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        msg = msg.replace(`{${k}}`, v)
      }
    }
    return msg
  }

  function setLocale(lang) {
    locale.value = lang === 'ru' ? 'ru' : 'en'
  }

  return { locale, t, setLocale }
}
