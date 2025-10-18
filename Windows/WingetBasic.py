import subprocess
import sys
import platform

def run_winget_upgrade_manager():
    """
    Checks for available winget upgrades, displays the list, and prompts the user
    to run 'winget upgrade --all' for full system update.
    """
    # Check if the operating system is Windows
    if platform.system() != "Windows":
        print("This script is designed to run on Windows and requires the winget utility.")
        return

    print("--- Running 'winget upgrade' to check for available updates... ---\n")

    try:
        # 1. Execute 'winget upgrade' to list available updates
        # capture_output=True grabs stdout and stderr
        # text=True ensures output is decoded as a string
        result = subprocess.run(
            ['winget', 'upgrade'],
            capture_output=True,
            text=True,
            check=False, # Don't raise an exception immediately if winget returns a non-zero exit code (e.g., if no updates are found)
            shell=False
        )

        # 2. Display the output (list of available updates or confirmation of no updates)
        if result.stdout:
            print(result.stdout.strip())
        
        # Check for stderr, which might indicate an issue, but often winget's "No upgrades available" message
        # or similar non-critical messages end up here or stdout.
        if "No upgrades available" in result.stdout:
            print("\n----------------------------------------------------")
            print("Winget reported: No package upgrades are currently available.")
            print("----------------------------------------------------")
            return
        elif result.stderr and "No package found matching input" not in result.stderr:
            # Print stderr if there's any important error message
            print(f"\n[Warning/Error from winget check]:\n{result.stderr.strip()}")
            

        print("\n" + "="*70)
        print("Do you want to proceed with installing ALL the listed upgrades?")
        print("This will execute 'winget upgrade --all'.")
        print("="*70)

        # 3. Prompt the user for confirmation
        while True:
            user_input = input("Enter yes or y to proceed with the upgrade, or no or n to exit: ").strip().lower()

            if user_input in ['yes', 'y']:
                print("\n--- Starting 'winget upgrade --all'. This may take a while... ---")
                
                # 4. Execute 'winget upgrade --all' if confirmed
                # We don't capture the output here so the user can see the live install progress
                subprocess.run(
                    ['winget', 'upgrade', '--all', '--accept-package-agreements', '--accept-source-agreements'],
                    check=False,
                    shell=False
                )
                print("\n--- Winget upgrade process finished. ---")
                return
            
            elif user_input in ['no', 'n']:
                # 5. Exit if not confirmed
                print("\nOperation canceled by user. No packages were upgraded.")
                return
            
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    except FileNotFoundError:
        print("\nERROR: 'winget' command not found. Ensure winget is installed and in your system PATH.")
        print("Winget is usually included with modern versions of Windows 10/11.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    run_winget_upgrade_manager()
