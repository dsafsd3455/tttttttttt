from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from solana.rpc.async_api import AsyncClient
import requests
import asyncio

# Dexscreener API URL
DEXSCREENER_API = "https://api.dexscreener.io/latest/dex/search?q="

# Function to fetch market data from Dexscreener
def fetch_market_data(contract_address):
    response = requests.get(DEXSCREENER_API + contract_address)
    if response.status_code == 200:
        data = response.json()
        if 'pairs' in data:
            return data['pairs'][0]  # Return the first market pair
    return None

# Function to fetch basic Solana data
async def fetch_solana_data(contract_address):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        try:
            account_info = await client.get_account_info(contract_address)
            return account_info['result']['value']
        except Exception as e:
            return str(e)

# Telegram bot command handler to fetch data
def get_coin_info(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Please provide a contract address.")
        return
    
    contract_address = context.args[0]
    # Fetch data from Solana and Dexscreener
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    solana_data = loop.run_until_complete(fetch_solana_data(contract_address))
    market_data = fetch_market_data(contract_address)
    
    if solana_data and market_data:
        response = (
            f"🔹 Market Data for {contract_address}:\n"
            f"💰 Price: {market_data['priceUsd']} USD\n"
            f"📈 Volume: {market_data['volume']['h24']} USD\n"
            f"🧪 Liquidity: {market_data['liquidity']['usd']} USD\n\n"
            f"🔹 Solana Account Info:\n{solana_data}"
        )
    else:
        response = "Could not fetch data. Please check the contract address."

    update.message.reply_text(response)

# Main function to run the bot
def main():
    # Your Telegram Bot Token
    TOKEN = "7257911503:AAFlwigIv6kNZb56BoHduuueYjgtLiFEQMA"
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Command to fetch coin info
    dispatcher.add_handler(CommandHandler("getcoin", get_coin_info))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
