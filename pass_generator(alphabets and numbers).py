import random
import string

def generate_passwords(count=1000, min_length=6, max_length=12):
    passwords = set()
    characters = string.ascii_letters + string.digits

    while len(passwords) < count:
        length = random.randint(min_length, max_length)
        password = ''.join(random.choices(characters, k=length))
        passwords.add(password)

    return list(passwords)

# Generate the passwords
password_list = generate_passwords()

# Write to wordlist.txt
with open('wordlist.txt', 'w') as file:
    for pwd in password_list:
        file.write(pwd + '\n')

print("✅ 1000-password wordlist saved as 'wordlist.txt'. Ready to crack some gates.")
