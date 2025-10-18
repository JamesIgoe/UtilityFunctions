import subprocess
import sys
import platform
import re # Added for robust output parsing

def parse_winget_output(output):
    """
    Parses the output of 'winget upgrade' to extract a list of upgradable packages.
    Returns a list of dictionaries: [{'name': '...', 'id': '...'}, ...]
    """
    packages = []
    lines = output.strip().split('\n')
    
    # Find the header separator line (usually '---' or '====') to determine where data starts
    data_start_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(('---', '====')):
            data_start_index = i + 1
            break
            
    if data_start_index == -1:
        return packages

    # Process lines after the separator
    for line in lines[data_start_index:]:
        line = line.strip()
        if not line or line.startswith('Found'):
            continue
            
        # Use regex to split by 2 or more spaces, which usually separates winget columns
        # Output columns are typically: Name | Id | Version | Available | Source
        parts = re.split(r'\s{2,}', line)
        
        if len(parts) >= 5:
            name = parts[0].strip()
            pkg_id = parts[1].strip()
            
            if name and pkg_id:
                packages.append({
                    'name': name,
                    'id': pkg_id,
                    'version': parts[2].strip(),
                    'available': parts[3].strip()
                })
                
    return packages

def run_winget_upgrade_manager():
    """
    Checks for available winget upgrades, displays the list, and prompts the user
    to run 'winget upgrade --all' or select a specific package.
    """
    # Check if the operating system is Windows
    if platform.system() != "Windows":
        print("This script is designed to run on Windows and requires the winget utility.")
        return

    print("--- Running 'winget upgrade' to check for available updates... ---\n")

    try:
        # 1. Execute 'winget upgrade' to list available updates
        result = subprocess.run(
            ['winget', 'upgrade'],
            capture_output=True,
            text=True,
            check=False,
            shell=False
        )

        # 2. Parse the output to get the list of upgradable packages
        packages_to_upgrade = parse_winget_output(result.stdout)

        if not packages_to_upgrade:
            print("\n----------------------------------------------------")
            print("Winget reported: No package upgrades are currently available.")
            print("----------------------------------------------------")
            return
            
        # Print any warnings/errors that occurred during the check
        if result.stderr and "No package found matching input" not in result.stderr:
            print(f"\n[Warning/Error from winget check]:\n{result.stderr.strip()}")

        # 3. Enter the selection loop
        while True:
            print("\n" + "="*70)
            print("AVAILABLE PACKAGE UPGRADES:")
            print("="*70)
            
            # Display the numbered list of packages
            for i, pkg in enumerate(packages_to_upgrade, 1):
                print(f"[{i: >2}] {pkg['name']} (ID: {pkg['id']}) - {pkg['version']} -> {pkg['available']}")

            print("\n" + "-"*70)
            print("[ 0] UPGRADE ALL listed packages.")
            print("[ C] Cancel/Stop and exit the script.")
            print("-"*70)

            user_input = input("Enter option [0-{}], or 'C' to cancel: ".format(len(packages_to_upgrade))).strip()

            if user_input.lower() == 'c':
                print("\nOperation canceled by user. Exiting.")
                return

            if user_input == '0':
                print("\n--- Starting 'winget upgrade --all'. This may take a while... ---")
                
                # Execute 'winget upgrade --all'
                subprocess.run(
                    ['winget', 'upgrade', '--all', '--accept-package-agreements', '--accept-source-agreements'],
                    check=False,
                    shell=False
                )
                print("\n--- Winget upgrade process finished. ---")
                return

            try:
                selection_index = int(user_input)
                if 1 <= selection_index <= len(packages_to_upgrade):
                    selected_pkg = packages_to_upgrade[selection_index - 1]
                    pkg_id = selected_pkg['id']
                    
                    print(f"\n--- Starting upgrade for: {selected_pkg['name']} (ID: {pkg_id}) ---")
                    
                    # Execute upgrade for the selected package
                    subprocess.run(
                        ['winget', 'upgrade', '--id', pkg_id, '--accept-package-agreements', '--accept-source-agreements'],
                        check=False,
                        shell=False
                    )
                    
                    print(f"\n--- Upgrade finished for {selected_pkg['name']}. ---")
                    
                    # Remove the successful upgrade from the list and continue
                    packages_to_upgrade.pop(selection_index - 1)
                    
                    if not packages_to_upgrade:
                        print("\nAll packages in the original list have been upgraded. Exiting.")
                        return

                else:
                    print(f"Invalid option. Please enter a number between 1 and {len(packages_to_upgrade)}, 0, or 'C'.")
            
            except ValueError:
                print("Invalid input. Please enter a number (0 or 1-{}) or 'C'.".format(len(packages_to_upgrade)))

    except FileNotFoundError:
        print("\nERROR: 'winget' command not found. Ensure winget is installed and in your system PATH.")
        print("Winget is usually included with modern versions of Windows 10/11.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    run_winget_upgrade_manager()
