import sys 
import ctypes

production_ip = "13.251.136.207"
production_domain = "app.sdg-dashboard.com"

def show_menu():
    print("\n Windows hosts file manager \n")
    print("--------------------------")
    print("[1] Add host entry")
    print("[2] Remove host entry")
    print("[0] Exit")

def is_admin():
    try:
       
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    while True:

        if is_admin():

            show_menu()
            choice = input("\n Select opton: ").strip()

            if choice == "1":
                success = add_host_entry(production_ip, production_domain)

                if success:
                    print(f"\n Host entry added: {production_ip} {production_domain}\n")
                else:
                    print(f"\n Host failed to add: {production_ip} {production_domain}\n")

            elif choice == "2":
                success = remove_host_entry(production_domain)

                if success:
                    print(f"\n Host entry removed: {production_domain}\n")
                else:
                    print(f"\n Host failed to remove: {production_domain}\n")

            elif choice == "0":
                print("\n Exiting...\n")
                sys.exit(0)
            else:
                print("\n Invalid option. Please try again.\n")
        else:
            print("This script requires administrative privileges to run.")
            print("Please run the script as an administrator.")
            sys.exit(1)

if __name__ == "__main__":
    main()
