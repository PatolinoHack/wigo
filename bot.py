from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
from datetime import datetime
import logging
import re

# Configuración
TOKEN = "7538427876:AAHvf67AhwLT3XpekRbx9RL2ywwZD905mGI"
PLANTILLA_PATH = "plantilla.png"
TU_ID_USUARIO = 7310531724
TU_USUARIO = "@GUTYFIEL1"
GRUPO_VIP_ID = -1002567638156

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

MESES = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic."]

def notify_usage(bot: Bot, update: Update):
    try:
        user = update.effective_user
        chat = update.effective_chat

        user_info = f"👤 Usuario: {user.full_name} [@{user.username if user.username else 'sin username'}]"
        user_info += f"\n🆔 ID: {user.id}"

        chat_info = ""
        if chat.type != "private":
            chat_info = f"\n\n💬 Chat: {chat.title if chat.title else ''}"
            chat_info += f"\n🆔 Chat ID: {chat.id}"
            chat_info += f"\n🔗 Enlace: {chat.username if chat.username else 'privado'}"

        command_info = f"\n\n📩 Mensaje:\n{update.message.text}"

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mensaje = f"🚀 Bot usado - {fecha}\n{user_info}{chat_info}{command_info}"

        bot.send_message(
            chat_id=TU_ID_USUARIO,
            text=mensaje,
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"Error al enviar notificación: {e}")

def private_chat_message(update: Update, context: CallbackContext):
    notify_usage(context.bot, update)
    update.message.reply_text(
        "🚫 *Este bot solo funciona en el grupo VIP*\n\n"
        "Para obtener acceso, contacta a @GUTYFIEL1\n\n"
        f"Desarrollado por {TU_USUARIO}",
        parse_mode="Markdown"
    )

def start(update: Update, context: CallbackContext):
    notify_usage(context.bot, update)
    if update.effective_chat.id == GRUPO_VIP_ID:
        update.message.reply_text(
            "💳 *Bot de Transferencias Avanzado*\n\n"
            "Envía:\n`/transferencia Nombre Completo|Ultimos Digitos|Monto (ej: 500.00)`\n\n"
            "Ejemplo:\n`/transferencia Juana Quinteros|123|500.00`\n\n"
            f"Desarrollado por {TU_USUARIO}",
            parse_mode="Markdown"
        )
    else:
        private_chat_message(update, context)

def transferencia(update: Update, context: CallbackContext):
    if update.effective_chat.id != GRUPO_VIP_ID:
        update.message.reply_text(
            "🚫 *Este comando solo está disponible en el grupo VIP*\n\n"
            "Para obtener acceso, contacta a @GUTYFIEL1\n\n"
            f"Desarrollado por {TU_USUARIO}",
            parse_mode="Markdown"
        )
        return

    notify_usage(context.bot, update)

    try:
        args = update.message.text.split(' ', 1)[1]
        partes = [x.strip() for x in args.split('|')]

        if len(partes) != 3:
            raise ValueError("Formato incorrecto")

        nombre, numero_cuenta, monto = partes

        if not re.match(r'^\d{3}$', numero_cuenta):
            update.message.reply_text(
                "❌ El número de cuenta debe tener **exactamente 3 dígitos**.\n"
                "Ejemplo: `/transferencia Maria Lopez|123|100.50`\n\n"
                f"Desarrollado por {TU_USUARIO}",
                parse_mode="Markdown"
            )
            return

        if not re.match(r'^\d+(\.\d{1,2})?$', monto):
            update.message.reply_text(
                "❌ El monto debe ser un **número válido** (ej: 150 o 150.50).\n"
                "Ejemplo: `/transferencia Carlos Perez|456|75.00`\n\n"
                f"Desarrollado por {TU_USUARIO}",
                parse_mode="Markdown"
            )
            return

        numero_operacion = str(random.randint(10000000, 99999999))
        fecha_actual = datetime.now()
        fecha_formateada = f"{fecha_actual.day} {MESES[fecha_actual.month - 1]} {fecha_actual.year}"
        hora_arriba = fecha_actual.strftime("%H:%M")
        hora_formateada = fecha_actual.strftime("%I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")
        codigo_seguridad = f"{random.randint(0, 999):03d}"

        try:
            img = Image.open(PLANTILLA_PATH).convert("RGBA")
        except FileNotFoundError:
            update.message.reply_text(f"❌ Error: No encontré la plantilla PNG\n\nDesarrollado por {TU_USUARIO}")
            return

        draw = ImageDraw.Draw(img)

        try:
            font_grandaso = ImageFont.truetype("arialbd.ttf", 105)
            font_largo = ImageFont.truetype("arialbd.ttf", 60)
            font_mediano = ImageFont.truetype("arialbd.ttf", 40)
            font_peque = ImageFont.truetype("arial.ttf", 40)
            font_codigo = ImageFont.truetype("arialbd.ttf", 55)
        except:
            font_grandaso = font_largo = font_mediano = font_peque = font_codigo = ImageFont.load_default()

        campos = [
            (nombre, 100, 695, (66, 52, 85), font_largo),
            (f"{numero_cuenta}", 978, 1200, (27, 22, 42), font_mediano),
            (f"{monto}", 210, 578, (66, 52, 85), font_grandaso),
            (f"{numero_operacion}", 974, 1363, (27, 22, 42), font_mediano),
            (f"{fecha_formateada}", 165, 805, (102, 98, 112), font_mediano),
            (f"{hora_formateada}", 540, 805, (102, 98, 112), font_mediano),
            (f"{hora_arriba}", 50, 22, (255, 255, 255), font_peque)
        ]

        for texto, x, y, color, fuente in campos:
            draw.text((x, y), texto, fill=color, font=fuente)

        digitos = list(codigo_seguridad)
        x_base = 753
        y_pos = 976
        espacio = 87

        for i, digito in enumerate(digitos):
            draw.text(
                (x_base + (i * espacio) + 20, y_pos),
                digito,
                fill=(27, 22, 42),
                font=font_codigo
            )

        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG', quality=95)
        img_byte_arr.seek(0)

        update.message.reply_photo(
            photo=img_byte_arr,
            caption=f"❰ #OlimpoData ❱ ➣ GRATIS\n\n✅ Imagen Generada:\n\n• Cuenta: {nombre}\n• Monto: S/{monto}\n\n• Desarrollado por {TU_USUARIO}",
            parse_mode="Markdown"
        )

    except IndexError:
        update.message.reply_text(
            "⚠ Formato incorrecto. Usa:\n"
            "`/transferencia Nombre Completo|Ultimos Digitos|Monto`\n\n"
            "Ejemplo:\n`/transferencia Ana Garcia|789|200`\n\n"
            f"Desarrollado por {TU_USUARIO}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        update.message.reply_text(
            f"❌ Ocurrió un error al procesar tu solicitud\n\nDesarrollado por {TU_USUARIO}"
        )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("transferencia", transferencia))
    dp.add_handler(MessageHandler(filters.Private & (~filters.COMMAND), private_chat_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
