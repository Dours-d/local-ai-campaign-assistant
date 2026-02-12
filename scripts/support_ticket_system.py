import json
import os
import datetime
import uuid
import sys

# Configuration
DATA_DIR = "data"
TICKETS_FILE = os.path.join(DATA_DIR, "support_tickets.json")
NOTIFICATIONS_LOG = os.path.join(DATA_DIR, "whatsapp_notifications.log")
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+972592645759") # Defaulting to known number from context if available, or placeholder

class TicketSystem:
    def __init__(self):
        self._ensure_data_dir()
        self.tickets = self._load_tickets()

    def _ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _load_tickets(self):
        if not os.path.exists(TICKETS_FILE):
            return {}
        try:
            with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save_tickets(self):
        with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tickets, f, indent=2)

    def create_ticket(self, user_id, message, contact_info=None):
        """
        Creates a new support ticket and triggers a notification.
        """
        ticket_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().isoformat()
        
        ticket = {
            "id": ticket_id,
            "user_id": user_id,
            "contact_info": contact_info,
            "message": message,
            "status": "OPEN",
            "created_at": timestamp,
            "updates": []
        }
        
        self.tickets[ticket_id] = ticket
        self._save_tickets()
        
        print(f"Ticket {ticket_id} created for {user_id}.")
        
        # Trigger Notification
        self.trigger_whatsapp_notification(ticket)
        return ticket_id

    def trigger_whatsapp_notification(self, ticket):
        """
        Simulates triggering a WhatsApp notification.
        In a real scenario, this would use Twilio, PyWhatKit, or a local gateway.
        """
        # draft the message
        msg_body = (
            f"🎫 *New Ticket* [{ticket['id']}]\n"
            f"👤 User: {ticket['user_id']}\n"
            f"📞 Contact: {ticket.get('contact_info', 'N/A')}\n"
            f"📝 Issue: {ticket['message']}\n"
            f"🕒 Time: {ticket['created_at']}"
        )
        
        # 1. Log to file (Persistent record of triggers)
        with open(NOTIFICATIONS_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] SENT TO {ADMIN_PHONE}:\n{msg_body}\n{'-'*20}\n")
            
        # 2. Console Output (Visual confirmation for user/dev)
        print(f"\n[WHATSAPP TRIGGER] Sending to {ADMIN_PHONE}...")
        print(f"--- MESSAGE PAYLOAD ---\n{msg_body}\n-----------------------\n")
        
        # 3. Future Integration Point
        # send_via_gateway(ADMIN_PHONE, msg_body)

    def list_tickets(self, status=None):
        if not status:
            return self.tickets
        return {k: v for k, v in self.tickets.items() if v['status'] == status}

    def close_ticket(self, ticket_id, resolution_note=""):
        if ticket_id in self.tickets:
            self.tickets[ticket_id]['status'] = 'CLOSED'
            self.tickets[ticket_id]['updates'].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "note": f"Closed: {resolution_note}"
            })
            self._save_tickets()
            print(f"Ticket {ticket_id} closed.")
        else:
            print(f"Ticket {ticket_id} not found.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Support Ticket System")
    subparsers = parser.add_subparsers(dest="command")
    
    # Create
    p_create = subparsers.add_parser("create", help="Create a new ticket")
    p_create.add_argument("user", help="User Name or ID")
    p_create.add_argument("message", help="The doleance/issue")
    p_create.add_argument("--contact", help="Contact info (phone/email)", default=None)
    
    # List
    p_list = subparsers.add_parser("list", help="List tickets")
    p_list.add_argument("--status", help="Filter by status (OPEN/CLOSED)", default=None)
    
    # Close
    p_close = subparsers.add_parser("close", help="Close a ticket")
    p_close.add_argument("ticket_id", help="Ticket ID")
    p_close.add_argument("--note", help="Resolution note", default="Resolved")

    args = parser.parse_args()
    
    system = TicketSystem()
    
    if args.command == "create":
        system.create_ticket(args.user, args.message, args.contact)
    elif args.command == "list":
        tickets = system.list_tickets(args.status)
        print(json.dumps(tickets, indent=2))
    elif args.command == "close":
        system.close_ticket(args.ticket_id, args.note)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
