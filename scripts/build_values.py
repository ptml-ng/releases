#!/usr/bin/env python3
"""
Usage: build_values.py <serverFlavour> [companyName] [packageName]
"""
import sys
import json

from write_output import write_output

def titlecase_first(s: str) -> str:
    if not s:
        return s
    return s[0].upper() + s[1:] if s[0].islower() else s

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: build_values.py <serverFlavour> [companyName] [packageName]", file=sys.stderr)
        sys.exit(1)

    server_flavour = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    package_name = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None

    # Load config.json only if company_name is provided
    company = None
    
    if company_name:
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config_json = json.load(f)
        except Exception as e:
            print(f"Failed to read config.json: {e}", file=sys.stderr)
            sys.exit(2)

        companies = config_json.get("companies", [])
        
        company = next((c for c in companies if company_name.lower() in (c.get("id", "").lower())), None)
        if company is None:
            print(f"No company found with name {company_name}", file=sys.stderr)
            sys.exit(3)
        
        company_name = company.get("id")

    # Load google-services.json
    try:
        with open("app/google-services.json", "r", encoding="utf-8") as f:
            gs = json.load(f)
    except Exception as e:
        print(f"Failed to read app/google-services.json: {e}", file=sys.stderr)
        sys.exit(4)

    # Get the package name from the company if not provided
    if company and not package_name:
        package_name = company.get("app", {}).get("id")
        if package_name is None:
            print("Company entry does not contain app.id", file=sys.stderr)
            sys.exit(5)
            
    # Package name must be provided now
    if not package_name:
        print("Package name must be provided either via company config or as an argument", file=sys.stderr)
        sys.exit(5)
        
    if server_flavour.lower() != "prod":
        package_name = f"{package_name}.{server_flavour.lower()}"

    # Find the client with the matching package name
    clients = gs.get("client", [])
    client = None
    
    # Match by package name
    for c in clients:
        pkg = c.get("client_info", {}).get("android_client_info", {}).get("package_name")
        if pkg == package_name:
            client = c
            break

    if client is None:
        print(f"No client found in google-services.json with package_name={package_name}", file=sys.stderr)
        sys.exit(6)

    app_id = client.get("client_info", {}).get("mobilesdk_app_id")
    if not app_id:
        print("Could not find mobilesdk_app_id for the matched client", file=sys.stderr)
        sys.exit(7)
        
    build_part = f"{company_name or ''}{titlecase_first(server_flavour) if company_name else server_flavour}"
    path = f"app/build/outputs/apk/{build_part}/release/"
    build_command = f":app:assemble{build_part}Release"

    write_output(
        [
            f"PACKAGE_NAME={package_name}",
            f"PATH={path}",
            f"BUILD_COMMAND={build_command}",
            f"APP_ID={app_id}"
        ]
    )


if __name__ == "__main__":
    main()

