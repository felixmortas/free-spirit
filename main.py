"""
Main Entry Point for ReAct Agent WhatsApp chatbot
"""

from dotenv import load_dotenv
load_dotenv()

import argparse

from langfuse_engine import langfuse_handler
from agent import create_email_agent
from chat_session import ChatSession       

# ==================== DISPLAY ====================
 
BANNER = """
╔══════════════════════════════════════╗
║         ReAct Agent — Terminal       ║
║  /reset  clear history               ║
║  /history  view the conversation     ║
║  /exit   leave.                      ║
╚══════════════════════════════════════╝
"""
 
def print_agent(text: str):
    print(f"\n\033[92mAgent ▶\033[0m {text}\n")
 
def print_error(text: str):
    print(f"\n\033[91m[Error]\033[0m {text}\n")
 
def print_info(text: str):
    print(f"\n\033[94m[Info]\033[0m {text}\n")

# ==================== COMMANDES ====================
 
def handle_command(cmd: str, session: ChatSession) -> bool:
    """
    Processes special orders.
    Returns True if it was an order (to skip sending it to the agent).
    """
    cmd = cmd.strip().lower()
 
    if cmd == "/exit":
        print_info("See you soon!")
        raise SystemExit(0)
 
    if cmd == "/reset":
        session.reset()
        print_info("Chat history cleared. New conversation started.")
        return True
 
    if cmd == "/history":
        history = session.get_history()
        if not history:
            print_info("No messages yet.")
        else:
            print()
            for entry in history:
                color = "\033[96m" if entry["role"] == "You" else "\033[92m"
                print(f"  {color}{entry['role']}\033[0m : {entry['content']}")
            print()
        return True
 
    return False
 
 
# ==================== REPL LOOP ====================
 
def run_chat(session: ChatSession):
    """Main read/response loop."""
    print(BANNER)
 
    while True:
        try:
            user_input = input("\033[96mYou ▶\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print_info("\nInterruption detected. See you soon!")
            break
 
        if not user_input:
            continue
 
        # Commandes spéciales
        if user_input.startswith("/"):
            handle_command(user_input, session)
            continue
 
        # Envoi à l'agent
        try:
            response = session.send(user_input)
            print_agent(response)
        except Exception as e:
            print_error(f"The agent encountered a problem: {e}")
 


# ==================== MAIN ====================

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="ReAct Agent for automated WhatsApp Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            python main.py --model mistral-large-latest
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="mistral-small-latest",
        help="Model name (e.g. mistral-large-latest, gemini-3-flash-preview)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode"
    )


    args = parser.parse_args()

        
    
    # Run the workflow
    agent = create_email_agent(model_name=args.model, debug=args.debug)

    session = ChatSession(agent=agent, langfuse_handler=langfuse_handler)
 
    run_chat(session)


if __name__ == "__main__":
    main()