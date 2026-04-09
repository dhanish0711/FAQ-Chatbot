#!/usr/bin/env python3
"""
Multichannel CLI Simulator for NICS FAQ Chatbot.

Demonstrates how the same chatbot engine behaves across three channels:
  - Web (HTML-formatted with badges)
  - Mobile (plain-text compact JSON)
  - WhatsApp (plain-text with numbered quick-replies)

Usage:
  python multichannel_cli.py              # Interactive mode (pick a channel)
  python multichannel_cli.py --demo       # Auto-run demo scenarios on all 3 channels
  python multichannel_cli.py --channel web  # Interactive mode on specific channel

Requires: Flask server running at http://localhost:5000
"""

import requests
import sys
import json
import re
import textwrap

BASE_URL = "http://localhost:5000"

# Channel endpoint mapping
CHANNELS = {
    'web': '/get_response',
    'mobile': '/api/v1/chat',
    'whatsapp': '/whatsapp/webhook',
}

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def strip_html_for_display(html_text):
    """Strip HTML tags for CLI display."""
    text = html_text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    text = re.sub(r'<div[^>]*>', '\n', text)
    text = text.replace('</div>', '\n')
    text = re.sub(r'<b>(.*?)</b>', r'\1', text)
    text = re.sub(r'<i>(.*?)</i>', r'\1', text)
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


def send_message(channel, message, session_id='cli-test-session'):
    """Send a message to a specific channel endpoint."""
    url = BASE_URL + CHANNELS[channel]
    
    payload = {'message': message}
    if channel in ('mobile', 'whatsapp'):
        payload['session_id'] = session_id
    if channel == 'whatsapp':
        payload['from'] = '+919999999999'
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}ERROR: Cannot connect to {BASE_URL}")
        print(f"Make sure the Flask server is running: python app.py{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}ERROR: {e}{Colors.RESET}")
        sys.exit(1)


def format_web_response(data):
    """Format web channel response for CLI display."""
    lines = []
    lines.append(f"{Colors.BOLD}📱 WEB RESPONSE{Colors.RESET}")
    lines.append(f"{'─' * 50}")
    
    # Response text (strip HTML for display)
    response = strip_html_for_display(data.get('response', ''))
    lines.append(f"{response}")
    
    # Badges
    method = data.get('method', '?')
    confidence = data.get('confidence', 0)
    intent = data.get('intent', '?')
    badge_color = Colors.GREEN if confidence >= 0.3 else Colors.YELLOW if confidence >= 0.15 else Colors.RED
    lines.append(f"\n{badge_color}[{method.upper()}] Confidence: {confidence*100:.1f}%{Colors.RESET}  Intent: {intent}")
    
    # Entity context
    entity_ctx = data.get('entity_context', '')
    if entity_ctx:
        lines.append(f"{Colors.CYAN}🔍 {entity_ctx}{Colors.RESET}")
    
    # Suggestions as clickable chips
    suggestions = data.get('suggestions', [])
    if suggestions:
        chips = '  '.join(f"[💬 {s}]" for s in suggestions)
        lines.append(f"\n{Colors.BLUE}{chips}{Colors.RESET}")
    
    lines.append(f"{'─' * 50}")
    return '\n'.join(lines)


def format_mobile_response(data):
    """Format mobile channel response for CLI display."""
    lines = []
    lines.append(f"{Colors.BOLD}📲 MOBILE RESPONSE{Colors.RESET}")
    lines.append(f"{'─' * 50}")
    
    # Plain text response
    lines.append(f"{data.get('text', '(no text)')}")
    
    # Compact metadata
    method = data.get('method', '?')
    confidence = data.get('confidence', 0)
    intent = data.get('intent', '?')
    lines.append(f"\n{Colors.DIM}channel: mobile | method: {method} | confidence: {confidence:.2f} | intent: {intent}{Colors.RESET}")
    
    # Suggestions as list
    suggestions = data.get('suggestions', [])
    if suggestions:
        lines.append(f"{Colors.CYAN}Suggestions: {json.dumps(suggestions)}{Colors.RESET}")
    
    # Session
    lines.append(f"{Colors.DIM}session: {data.get('session_id', '?')}{Colors.RESET}")
    
    lines.append(f"{'─' * 50}")
    return '\n'.join(lines)


def format_whatsapp_response(data):
    """Format WhatsApp channel response for CLI display."""
    lines = []
    lines.append(f"{Colors.BOLD}💬 WHATSAPP RESPONSE{Colors.RESET}")
    lines.append(f"{'─' * 50}")
    lines.append(f"{Colors.DIM}To: {data.get('to', '?')}{Colors.RESET}")
    
    # WhatsApp body (already plain text with numbered replies)
    body = data.get('body', '(no body)')
    lines.append(f"\n{body}")
    
    # Quick replies
    qr = data.get('quick_replies', [])
    if qr:
        lines.append(f"\n{Colors.GREEN}Quick Replies: {json.dumps([r['title'] for r in qr])}{Colors.RESET}")
    
    lines.append(f"{'─' * 50}")
    return '\n'.join(lines)


FORMATTERS = {
    'web': format_web_response,
    'mobile': format_mobile_response,
    'whatsapp': format_whatsapp_response,
}


def run_demo():
    """Run preset demo scenarios across all 3 channels."""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print(f"   MULTICHANNEL DEPLOYMENT DEMO — NICS FAQ Chatbot")
    print(f"{'=' * 60}{Colors.RESET}\n")
    
    scenarios = [
        ("What are the fees?", "Normal FAQ query"),
        ("Tell me about MECH placements", "Entity-boosted query"),
        ("What is the weather today?", "Out-of-scope query"),
        ("asdfgh", "Fallback (gibberish)"),
    ]
    
    for query, description in scenarios:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}━━━ Scenario: {description} ━━━{Colors.RESET}")
        print(f'{Colors.DIM}Query: "{query}"{Colors.RESET}\n')
        
        for channel in ['web', 'mobile', 'whatsapp']:
            # Use unique session per channel to avoid cross-contamination
            sid = f"demo-{channel}-{hash(query) % 10000}"
            data = send_message(channel, query, session_id=sid)
            formatted = FORMATTERS[channel](data)
            print(formatted)
            print()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Demo complete! Same engine, 3 different channel formats.{Colors.RESET}\n")


def run_interactive(channel='web'):
    """Run interactive chat on a specific channel."""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print(f"   INTERACTIVE MODE — Channel: {channel.upper()}")
    print(f"{'=' * 60}{Colors.RESET}")
    print(f"{Colors.DIM}Type your message and press Enter. Type 'quit' to exit.")
    print(f"Type '/switch <channel>' to change channel (web/mobile/whatsapp).{Colors.RESET}\n")
    
    sid = f"interactive-{channel}"
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}You > {Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ('quit', 'exit', 'q'):
            print(f"{Colors.DIM}Goodbye!{Colors.RESET}")
            break
        
        # Switch channel command
        if user_input.lower().startswith('/switch'):
            parts = user_input.split()
            if len(parts) == 2 and parts[1].lower() in CHANNELS:
                channel = parts[1].lower()
                sid = f"interactive-{channel}"
                print(f"{Colors.GREEN}Switched to {channel.upper()} channel.{Colors.RESET}\n")
            else:
                print(f"{Colors.RED}Usage: /switch web|mobile|whatsapp{Colors.RESET}\n")
            continue
        
        data = send_message(channel, user_input, session_id=sid)
        formatted = FORMATTERS[channel](data)
        print(f"\n{formatted}\n")


def main():
    args = sys.argv[1:]
    
    if '--demo' in args:
        run_demo()
    elif '--channel' in args:
        idx = args.index('--channel')
        if idx + 1 < len(args) and args[idx + 1] in CHANNELS:
            run_interactive(args[idx + 1])
        else:
            print(f"Usage: python multichannel_cli.py --channel web|mobile|whatsapp")
    else:
        # Default: interactive mode, ask which channel
        print(f"\n{Colors.BOLD}NICS Chatbot — Multichannel Simulator{Colors.RESET}")
        print(f"  1. Web (HTML responses)")
        print(f"  2. Mobile (plain-text compact)")
        print(f"  3. WhatsApp (numbered replies)")
        print(f"  4. Demo (run all channels)")
        
        try:
            choice = input(f"\n{Colors.BOLD}Choose [1-4]: {Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        
        if choice == '1':
            run_interactive('web')
        elif choice == '2':
            run_interactive('mobile')
        elif choice == '3':
            run_interactive('whatsapp')
        elif choice == '4':
            run_demo()
        else:
            print(f"Invalid choice. Running demo...")
            run_demo()


if __name__ == '__main__':
    main()
