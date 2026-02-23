import tkinter as tk
from tkinter import ttk, messagebox
import json
import pyperclip
import os
from datetime import datetime

# Paths to data files
UNIFIED_JSON = "data/campaigns_unified.json"
TEMPLATE_FILE = "data/standard_beneficiary_onboarding.txt"
LOG_FILE = "data/onboarding_log.json"

class OnboardingApplet:
    def __init__(self, root):
        self.root = root
        self.root.title("Amanah Onboarding Applet")
        self.root.geometry("600x700")

        # Load IDs initially
        self.all_ids = self.load_existing_ids()

        # UI Elements
        tk.Label(root, text="WhyDonate Link:", font=("Arial", 10, "bold")).pack(pady=5)
        self.link_entry = tk.Entry(root, width=70)
        self.link_entry.pack(pady=5)

        self.resolve_btn = tk.Button(root, text="Resolve ID & Name", command=self.resolve_data, bg="lightblue")
        self.resolve_btn.pack(pady=10)

        tk.Label(root, text="Beneficiary Name:", font=("Arial", 10, "bold")).pack(pady=5)
        self.name_entry = tk.Entry(root, width=50)
        self.name_entry.pack(pady=5)

        tk.Label(root, text="(Internal ID - Optional):", font=("Arial", 10, "italic")).pack(pady=5)
        self.id_combo = ttk.Combobox(root, width=47, values=self.all_ids)
        self.id_combo.pack(pady=5)
        # Disable mouse wheel scrolling on the combobox
        self.id_combo.bind("<MouseWheel>", lambda e: "break")

        # Control Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)

        self.gen_btn = tk.Button(btn_frame, text="🚀 Generate & Copy Message", command=self.generate_message, bg="lightgreen", font=("Arial", 10, "bold"), padx=10)
        self.gen_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = tk.Button(btn_frame, text="🧹 Clear Form", command=self.clear_form, bg="#ffcccb", font=("Arial", 10))
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        self.output_text = tk.Text(root, height=10, width=70)
        self.output_text.pack(pady=10)

    def load_existing_ids(self):
        try:
            if os.path.exists(UNIFIED_JSON):
                with open(UNIFIED_JSON, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    campaigns = data.get('campaigns', [])
                    ids = sorted(list(set(c['privacy']['internal_name'] for c in campaigns if c['privacy'].get('internal_name'))))
                    return ids
        except Exception as e:
            print(f"Error loading IDs: {e}")
        return []

    def clear_form(self):
        self.link_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.id_combo.set("")
        self.output_text.delete(1.0, tk.END)

    def log_association(self, name, bid, link):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "beneficiary_name": name,
            "internal_id": bid,
            "whydonate_link": link
        }
        
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def resolve_data(self):
        link = self.link_entry.get().strip()
        if not link:
            messagebox.showwarning("Warning", "Please enter a WhyDonate link.")
            return

        try:
            with open(UNIFIED_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                campaigns = data.get('campaigns', [])
                messagebox.showinfo("Note", "Automatic resolution is limited. Please select ID and enter Name manually if needed.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def generate_message(self):
        name = self.name_entry.get().strip()
        bid = self.id_combo.get().strip()
        link = self.link_entry.get().strip()

        if not all([name, link]):
            messagebox.showwarning("Warning", "Please fill in at least the Name and WhyDonate Link.")
            return

        final_bid = bid if bid else "(Unique ID Pending)"

        try:
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                template = f.read()

            message = template.replace("[BENEFICIARY_NAME]", name)
            message = message.replace("[BENEFICIARY_ID]", final_bid)
            message = message.replace("[WHYDONATE_LINK]", link)

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, message)

            pyperclip.copy(message)
            
            # Log the success
            self.log_association(name, final_bid, link)

            message_info = "Message generated"
            if not bid:
                message_info += " (with Pending ID)"
            messagebox.showinfo("Success", f"{message_info} and copied to clipboard!\nAssociation logged to {LOG_FILE}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate message: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OnboardingApplet(root)
    root.mainloop()
