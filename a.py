from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize variables
saldo = 0
riwayat = []

# Define states
ADD_BALANCE, SUBTRACT_BALANCE = range(2)

# Start command handler
# Start command handler
# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['Cek Saldo', 'Riwayat Saldo'],
                      ['Kurangi Saldo', 'Tambahkan Saldo']]
    
    # Send the message only when it's the first time
    if not context.user_data.get('first_time', False):
        update.message.reply_text(
            'Selamat datang di Bot Saldo Kereta. Pilih opsi:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        context.user_data['first_time'] = True
    else:
        update.message.reply_text(
            'Pilih opsi:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )


# Cek saldo command handler
def cek_saldo(update: Update, context: CallbackContext) -> None:
    global saldo
    pesan_saldo = ''
    if saldo < 20000:
        pesan_saldo = 'Dikit banget tuh saldo.'
    elif saldo >= 20000 and saldo < 30000:
        pesan_saldo = 'Mayan tuh saldo.'
    elif saldo >= 30000 and saldo < 100000:
        pesan_saldo = 'Gacor kang banyak bet.'
    update.message.reply_text(f'Saldo Anda saat ini adalah: Rp {saldo}. {pesan_saldo}')
    start(update, context)

# Riwayat saldo command handler
def riwayat_saldo(update: Update, context: CallbackContext) -> None:
    global riwayat
    if not riwayat:
        update.message.reply_text('Belum ada riwayat transaksi.')
    else:
        riwayat_text = "\n".join(riwayat)
        update.message.reply_text(f'Riwayat Transaksi:\n{riwayat_text}')
    start(update, context)

# Tambahkan saldo command handler
def tambahkan_saldo(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Masukkan jumlah saldo yang ingin ditambahkan:')
    return ADD_BALANCE

# Handler for adding balance
def add_balance(update: Update, context: CallbackContext) -> int:
    global saldo, riwayat
    try:
        jumlah = int(update.message.text)
        saldo += jumlah
        riwayat.append(f'Tambah: Rp {jumlah}')
        update.message.reply_text(f'Saldo berhasil ditambahkan. Saldo saat ini: Rp {saldo}')
    except ValueError:
        update.message.reply_text('Masukkan jumlah saldo yang valid.')
    start(update, context)
    return ConversationHandler.END

# Kurangi saldo command handler
def kurangi_saldo(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Masukkan jumlah saldo yang ingin dikurangi:')
    return SUBTRACT_BALANCE

# Handler for subtracting balance
def subtract_balance(update: Update, context: CallbackContext) -> int:
    global saldo, riwayat
    try:
        jumlah = int(update.message.text)
        if jumlah > saldo:
            update.message.reply_text('Saldo tidak mencukupi.')
        else:
            saldo -= jumlah
            riwayat.append(f'Kurang: Rp {jumlah}')
            update.message.reply_text(f'Saldo berhasil dikurangi. Saldo saat ini: Rp {saldo}')
    except ValueError:
        update.message.reply_text('Masukkan jumlah saldo yang valid.')
    start(update, context)
    return ConversationHandler.END

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main() -> None:
    # Bot token from BotFather
    TOKEN = '7388396494:AAFsTKsRULWMaJ_8LDw_Wpt7TwShFo87YzU'

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Cek Saldo$'), cek_saldo))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Riwayat Saldo$'), riwayat_saldo))

    # Conversation handler for adding balance
    conv_handler_add = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Tambahkan Saldo$'), tambahkan_saldo)],
        states={ADD_BALANCE: [MessageHandler(Filters.text & ~Filters.command, add_balance)]},
        fallbacks=[CommandHandler('start', start)],
    )

    # Conversation handler for subtracting balance
    conv_handler_subtract = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Kurangi Saldo$'), kurangi_saldo)],
        states={SUBTRACT_BALANCE: [MessageHandler(Filters.text & ~Filters.command, subtract_balance)]},
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler_add)
    dispatcher.add_handler(conv_handler_subtract)
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
