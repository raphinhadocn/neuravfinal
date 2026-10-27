# WhatsApp da NEURA em modo de estudo

## Variáveis do ambiente

Copie `.env.example` para `.env` e preencha os valores no próprio computador.
O `.env` já está no `.gitignore`; não envie tokens nem o segredo do app pelo chat.

- `WHATSAPP_ACCESS_TOKEN` e `WHATSAPP_PHONE_NUMBER_ID`: aparecem em WhatsApp → API Setup no painel do app.
- `WHATSAPP_VERIFY_TOKEN`: texto escolhido por você e repetido no cadastro do webhook.
- `WHATSAPP_APP_SECRET`: App Secret do painel do app; valida a assinatura das mensagens recebidas.
- `WHATSAPP_INVITE_TEMPLATE_NAME`: nome de um template existente e aprovado na WABA.
- `WHATSAPP_INVITE_TEMPLATE_LANGUAGE`: idioma do template, por exemplo `pt_BR`.

## Template de convite

O código envia o convite como template com dois parâmetros no corpo. Crie na
conta de teste um template em português com o nome configurado no `.env` e este
texto, mantendo as variáveis nesta ordem:

```text
Oi, {{1}}! Sou a NEURA, assistente pessoal de {{2}}. Você foi indicado(a) como contato de confiança. Autoriza receber mensagens de emergência por este WhatsApp? Responda SIM ou NÃO.
```

Adicione os números de teste como destinatários permitidos no painel da Meta.
O cadastro da Neura pergunta se o contato autorizou receber o convite; sem esse
consentimento, a aplicação não inicia a conversa.

## Executar o servidor

Na pasta raiz do projeto:

```powershell
uvicorn servidor.app:app --host 0.0.0.0 --port 8000
```

O endpoint de callback é `/webhook`. Para receber eventos da Meta, ele precisa
estar acessível por HTTPS. Em teste local, publique uma URL temporária HTTPS
para a porta 8000 e use-a como callback; depois assine o campo `messages` no
produto WhatsApp. Respostas `SIM` e `NÃO` atualizam `tpac_user.json`.
