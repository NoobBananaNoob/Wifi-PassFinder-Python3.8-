import random
import string


def generate_passwords(count):
    charset = string.ascii_letters + string.digits + string.punctuation  # A-Z, a-z, 0-9, symbols
    passwords = {''.join(random.choices(charset, k=random.randint(6, 12))) for _ in range(count)}
    return passwords

# Settings
num_passwords = 1000  # Number of passwords to generate

# Generate passwords
password_list = generate_passwords(num_passwords)

# Save to file
with open("wordlist.txt", "w") as file:
    for password in password_list:
        file.write(password + "\n")

print("Password list generated and saved as password_list.txt!")
