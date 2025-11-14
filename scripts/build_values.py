#!/usr/bin/env python3
"""
Usage: build_values.py <serverFlavour> [companyName]
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
        print("Usage: build_values.py <serverFlavour> [companyName]", file=sys.stderr)
        sys.exit(2)

    server_flavour = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) > 2 else None

    # Load config.json only if company_name is provided
    company = None
    
    if company_name:
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config_json = json.load(f)
        except Exception as e:
            print(f"Failed to read config.json: {e}", file=sys.stderr)
            sys.exit(3)

        companies = config_json.get("companies", [])
        
        company = next((c for c in companies if company_name.lower() in (c.get("id", "").lower())), None)
        if company is None:
            print(f"No company found with name {company_name}", file=sys.stderr)
            sys.exit(4)
        
        company_name = company.get("id")

    # Load google-services.json
    try:
        with open("app/google-services.json", "r", encoding="utf-8") as f:
            gs = json.load(f)
    except Exception as e:
        print(f"Failed to read app/google-services.json: {e}", file=sys.stderr)
        sys.exit(5)

    # Build the expected package name for this flavour
    if company:
        app_base_id = company.get("app", {}).get("id")
        if app_base_id is None:
            print("Company entry does not contain app.id", file=sys.stderr)
            sys.exit(6)

        if server_flavour.lower() == "prod":
            company_app_id = app_base_id
        else:
            company_app_id = f"{app_base_id}.{server_flavour.lower()}"
    else:
        # No company specified, derive from google-services.json directly
        company_app_id = None

    # Find the client with the matching package name
    clients = gs.get("client", [])
    client = None
    
    if company_app_id:
        # Match by package name
        for c in clients:
            pkg = (
                c.get("client_info", {}).get("android_client_info", {}).get("package_name")
            )
            if pkg == company_app_id:
                client = c
                break

        if client is None:
            print(f"No client found in google-services.json with package_name={company_app_id}", file=sys.stderr)
            sys.exit(7)
    else:
        # No company specified, use the first (and ideally only) client
        if len(clients) == 0:
            print("No clients found in google-services.json", file=sys.stderr)
            sys.exit(7)
        if len(clients) > 1:
            print("Multiple clients found in google-services.json but no company name specified", file=sys.stderr)
            sys.exit(7)
        client = clients[0]
        company_app_id = client.get("client_info", {}).get("android_client_info", {}).get("package_name")
        if not company_app_id:
            print("Could not find package_name for the client", file=sys.stderr)
            sys.exit(7)

    app_id = client.get("client_info", {}).get("mobilesdk_app_id")
    if not app_id:
        print("Could not find mobilesdk_app_id for the matched client", file=sys.stderr)
        sys.exit(8)
        
    build_part = f"{company_name or ''}{server_flavour}"
    path = f"app/build/outputs/apk/{build_part}/release/"
    build_command = f":app:assemble{build_part}Release"

    write_output(
        [
            f"COMPANY_ID={company_name or ''}",
            f"PATH={path}",
            f"BUILD_COMMAND={build_command}",
            f"APP_ID={app_id}"
        ]
    )


if __name__ == "__main__":
    main()

