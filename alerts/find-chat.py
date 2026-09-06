"""Read recent private bot chats without printing or saving the bot token."""
import getpass,json,urllib.request,urllib.error
key=getpass.getpass('Telegram bot token (hidden): ').strip()
try:
    req=urllib.request.Request('https://api.telegram.org/bot'+key+'/getUpdates',data=b'{"allowed_updates":["message"]}',headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as r: data=json.load(r)
    if not data.get('ok'): raise RuntimeError('Telegram rejected request')
    chats={m['message']['chat']['id']:m['message']['chat'] for m in data['result'] if m.get('message',{}).get('chat',{}).get('type')=='private'}
    if not chats: print('No recent private chats found. Send /start to your new bot, then run again. Use a dedicated bot without an existing webhook.')
    for i,c in chats.items():print('Chat ID:',i,'| Name:',c.get('first_name',''),c.get('last_name',''),'| Username:',c.get('username','(none)'))
    print('Use only the private chat that you recognize as yours. This helper does not select a chat or send a message.')
except Exception:
    print('Could not retrieve chats. Check the token, internet connection, and that this is a new bot without a webhook. No token was saved.')
