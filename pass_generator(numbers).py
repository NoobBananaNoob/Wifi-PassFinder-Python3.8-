import random

def generate_numeric_passwords(count=1000, min_length=6, max_length=12):
    passwords = set()
    digits = "0123456789"

    while len(passwords) < count:
        length = random.randint(min_length, max_length)
        password = ''.join(random.choices(digits, k=length))
        passwords.add(password)

    return list(passwords)

# Generate the passwords
password_list = generate_numeric_passwords()

# Write to wordlist.txt
with open('wordlist.txt', 'w') as file:
    for pwd in password_list:
        file.write(pwd + '\n')

print("✅ 1000-number-only passwords saved as 'wordlist.txt'. Locked, loaded, and legal.")
